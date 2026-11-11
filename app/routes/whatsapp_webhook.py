from fastapi import APIRouter, Request
import time
import json
import asyncio

from datetime import datetime, timedelta
from app.config import VERIFY_TOKEN
from app.services.gemini_service import ask_gemini
from app.services.whatsapp_service import send_whatsapp_message, download_image
from app.services.yolo_service import detect_disease
from app.services.log_service import save_consultation, save_text_log
from app.services.conversation_service import get_history, add_message

router = APIRouter()
processed_messages = {}
lock = asyncio.Lock()

def is_duplicate(message_id: str) -> bool:
    """Cek duplikat dan otomatis hapus entry lama (> 5 menit)"""
    now = datetime.now()

    expired = [k for k, v in processed_messages.items() if now - v > timedelta(minutes=5)]
    for k in expired:
        del processed_messages[k]

    if message_id in processed_messages:
        return True

    processed_messages[message_id] = now
    return False

# ==========================
# VERIFIKASI WEBHOOK
# ==========================
@router.get("/webhook/whatsapp")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "verification failed"}

# ==========================
# MENERIMA PESAN
# ==========================
@router.post("/webhook/whatsapp")
async def receive_message(request: Request):

    body = await request.json()

    print("Webhook Received")
    print(json.dumps(body, indent=2))

    try:
        # Validasi struktur bertahap
        if "entry" not in body or not body["entry"]:
            return {"status": "no entry"}

        entry = body["entry"][0]

        if "changes" not in entry or not entry["changes"]:
            return {"status": "no changes"}

        changes = entry["changes"][0]

        if "value" not in changes:
            return {"status": "no value"}

        value = changes["value"]

        if "messages" not in value:
            return {"status": "no message"}

        message = value["messages"][0]

        # Cek duplikat dengan lock agar thread-safe
        message_id = message.get("id")
        async with lock:
            if is_duplicate(message_id):
                print(f"⚠️ Duplikat diabaikan: {message_id}")
                return {"status": "duplicate"}

        sender = message["from"]
        print("MESSAGE TYPE:", message["type"])

        # ==========================
        # PESAN TEXT
        # ==========================
        if message["type"] == "text":

            user_text = message["text"]["body"]
            print("User:", user_text)
            
            # Mulai timer
            start = time.time()

            greetings = ["halo", "hai", "hello", "assalamualaikum"]

            if user_text.lower() in greetings:
                reply = "Halo 👋! Saya chatbot konsultasi pertanian 🌱. Silakan kirim pertanyaan atau foto tanaman yang ingin Anda konsultasikan."
            else:
                # Ambil riwayat percakapan pengguna
                history = await get_history(sender)

                # Kirim pertanyaan + riwayat ke Gemini
                reply = ask_gemini(user_text, history=history)

                # Simpan pertanyaan dan jawaban ke riwayat
                await add_message(sender, "user", user_text)
                await add_message(sender, "assistant", reply)
            
            send_whatsapp_message(sender, reply)
            
            # Hitung waktu respons
            elapsed = round(time.time() - start, 2)
            print("Response time teks:", elapsed, "detik")
        
            # Simpan log pesan teks
            save_text_log(sender, user_text, reply, response_time=elapsed)

        # ==========================
        # PESAN GAMBAR
        # ==========================
        elif message["type"] == "image":

            print("IMAGE MESSAGE DETECTED")

            image_id = message["image"]["id"]
            caption = message["image"].get("caption", "")
            print("Caption:", caption)
            
            send_whatsapp_message(sender, "🔍 Sedang menganalisis gambar tanaman...")

            # mulai timer
            start = time.time()
            
            image_path = download_image(image_id)
            print("Image saved:", image_path)

            detection_result = detect_disease(image_path)
            print("Detection:", detection_result)

            if "tidak dapat dikenali" in detection_result.lower():
                prompt = f"""
Pengguna mengirim gambar tanaman namun sistem tidak dapat mengenali penyakitnya.

Pesan pengguna:
"{caption}"

Tanyakan kepada pengguna kondisi tanaman lebih detail agar dapat membantu diagnosis.
"""
            else:
                prompt = f"""
Sistem mendeteksi gambar Tanaman Cabai: {detection_result}
Pesan Pengguna : "{caption}"

Jelaskan kepada petani dengan bahasa yang mudah dipahami:
1. Penyebab penyakit
2. Dampaknya pada tanaman
3. Solusi pengendalian atau penanganannya.
"""

            # Ambil riwayat percakapan
            history = await get_history(sender)
            ai_response = ask_gemini(prompt, history=history)

            # final_message
            final_message = f"""🌿 Hasil Deteksi:
{detection_result}

{ai_response}

Semoga membantu 🙏"""

            send_whatsapp_message(sender, final_message)
            
            elapsed = round(time.time() - start, 2)  # hitung waktu respons
            print("Response time:", elapsed, "detik")

            # Simpan konteks gambar ke riwayat 
            await add_message(sender, "user", f"[Gambar] Hasil deteksi: {detection_result}. Pesan: {caption}")
            await add_message(sender, "assistant", ai_response)

            save_consultation(sender, image_path, detection_result, response_time=elapsed)  # simpan log

        return {"status": "success"}

    except KeyError as e:
        print(f"KeyError: key {e} tidak ditemukan dalam payload")
        return {"status": "error", "detail": f"missing key: {e}"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}