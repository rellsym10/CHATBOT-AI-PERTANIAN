import requests
import time
from app.config import GEMINI_API_KEY

API_URL = "https://api.koboillm.com/v1/chat/completions"

def ask_gemini(prompt, history=None, retries=2):

    if history is None:
        history = []

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": """
            Anda adalah asisten konsultasi pertanian yang membantu petani di Indonesia.
            Tugas utama Anda adalah memberikan informasi dan rekomendasi pertanian berdasarkan praktik budidaya yang umum digunakan, literatur pertanian, serta prinsip pertanian yang baik.

            Aturan Jawaban:
            - Gunakan bahasa Indonesia yang sederhana, jelas, dan mudah dipahami petani.
            - Berikan jawaban yang relevan, akurat, dan sesuai konteks pertanian.
            - Utamakan informasi yang didasarkan pada praktik pertanian yang umum digunakan serta sumber ilmiah atau referensi terpercaya.
            - Jangan memberikan informasi di luar bidang pertanian.
            - Jika informasi yang diberikan pengguna belum cukup, mintalah informasi tambahan sebelum memberikan kesimpulan.
            - Jika diperlukan, sarankan pengguna mengirimkan foto tanaman untuk membantu proses identifikasi.
            - Berikan solusi yang realistis, praktis, dan dapat diterapkan di lapangan.
            - Hindari pernyataan yang terlalu pasti apabila tingkat keyakinan diagnosis masih rendah.
            - Jawab langsung pada inti pertanyaan tanpa memberikan pembukaan atau penutup yang terlalu panjang dan hindari penjelasan yang berulang.
            - Gunakan gaya bahasa ramah, sopan, dan profesional.

            Format Tampilan Jawaban:
            - Jawaban akan ditampilkan di aplikasi WhatsApp.
            - Gunakan emoji secara proposional agar kelihatan lebih menarik untuk dibaca.
            - Jangan pernah menggunakan markdown ini : #
            - Jika ingin menembalkan teks, gunakan format seperti ini: *teks*, bukan seperti ini: **teks**.
            - Gunakan penomoran sederhana: Nomor(1,2,3), bullet (•) atau Hayphen(-) untuk daftar.
            - Pastikan setiap daftar sejajar dan selalu rata kiri. 
            - Jangan gunakan spasi sebelum semua jenis markdown daftar.
            - Jangan gunakan markdown : (*) sebagai penomoran daftar.

            ATURAN KONTEKS PERCAKAPAN:
            - Jika pertanyaan baru berkaitan dengan topik sebelumnya 
              (informasi tambahan, gejala lanjutan, atau pertanyaan 
              susulan), gunakan riwayat percakapan untuk memberikan 
              jawaban yang berkelanjutan dan tidak bertanya ulang 
              hal yang sudah disebutkan.
            - Jika pertanyaan baru TIDAK berkaitan dengan topik 
              sebelumnya (tanaman, masalah, atau topik berbeda), 
              ABAIKAN riwayat percakapan dan jawab pertanyaan baru 
              tersebut secara mandiri tanpa mengaitkannya dengan 
              topik sebelumnya.
            """
        }
    ]

    # Tambahkan history
    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": prompt})

    data = {
        "model": "gemini-2.5-flash",
        "messages": messages,
        "temperature": 0.6,
        "tools": [          
            {
                "type": "web_search_20250305",
                "name": "web_search"
            }
        ]
    }

    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
            print("Gemini status:", response.status_code)
            print("Gemini response:", response.json())

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Jika content berupa list (ada tool_use block)
                if isinstance(content, list):
                    full_text = " ".join(
                        block.get("text", "") 
                        for block in content 
                        if block.get("type") == "text"
                    )
                    return full_text if full_text else "Tidak ada respons teks."
                return content

        except Exception as e:
            print(f"Attempt {attempt+1} error: {e}")
            if attempt < retries - 1:
                time.sleep(2)

    return "Maaf, sistem AI tidak dapat memberikan jawaban saat ini."