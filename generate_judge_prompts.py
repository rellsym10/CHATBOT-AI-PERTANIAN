"""
Generator Prompt LLM as a Judge (Manual via Claude.ai / ChatGPT)

Script ini TIDAK memanggil API apapun. Script ini hanya membaca
log_pesan_teks.json dan menghasilkan file teks berisi prompt
siap pakai untuk setiap pertanyaan.

CARA PAKAI:
1. Jalankan: python generate_judge_prompts.py
2. Buka file prompts_for_judge.txt yang dihasilkan
3. Copy SATU PER SATU prompt ke Claude.ai atau ChatGPT
4. Catat hasil skor JSON yang dikembalikan
5. Kumpulkan semua hasil ke file hasil_llm_judge.json
   mengikuti format yang sudah disediakan di bagian bawah
"""

import json
import os

LOG_FILE = "log_pesan_teks.json"
OUTPUT_FILE = "prompts_for_judge.txt"

# 10 pertanyaan yang digunakan saat pengujian waktu respons
PERTANYAAN_UJI = [
    "Mengapa irigasi tetes lebih baik daripada irigasi banjir?",
    "Apa peran penting plasma nutfah dalam pemuliaan tanaman?",
    "Tanaman tomat saya layu padahal sudah disiram, apa penyebabnya dan bagaimana solusinya?",
    "Cara mengatasi hama ulat pada tanaman kubis secara alami?",
    "Pupuk apa yang cocok untuk mempercepat pertumbuhan jagung?",
    "Cara budidaya tanaman cabai yang baik dan benar",
    "Daun padi saya menguning dan ada bercak coklat, itu penyakit apa dan bagaimana mengatasinya?",
    "Kapan waktu yang tepat untuk menanan padi",
    "Apa fungsi pupuk NPK pada tanaman?",
    "Bagaimana cara mengatasi tanaman terong saya yg terkena jamur?",
]


def main():
    if not os.path.exists(LOG_FILE):
        print(f"❌ File {LOG_FILE} tidak ditemukan.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_data = json.load(f)

    output_lines = []
    output_lines.append("=" * 100)
    output_lines.append("PROMPT LLM AS A JUDGE - SIAP COPY-PASTE KE CLAUDE.AI / CHATGPT")
    output_lines.append("Petunjuk: Copy SATU prompt di bawah (dari === PROMPT N === sampai akhir)")
    output_lines.append("ke Claude.ai atau ChatGPT, lalu catat hasil JSON yang dikembalikan.")
    output_lines.append("=" * 100)
    output_lines.append("")

    found = 0
    for i, pertanyaan_target in enumerate(PERTANYAAN_UJI, 1):
        item = next(
            (d for d in log_data if pertanyaan_target.lower() in d["pertanyaan"].lower()
             or d["pertanyaan"].lower() in pertanyaan_target.lower()),
            None
        )

        if item is None:
            output_lines.append(f"⚠️  [{i}] PERTANYAAN TIDAK DITEMUKAN DI LOG: {pertanyaan_target}")
            output_lines.append("    -> Kirim ulang pertanyaan ini ke chatbot terlebih dahulu\n")
            continue

        found += 1
        prompt = f"""=== PROMPT {i} ===

Anda adalah evaluator ahli pertanian yang bertugas menilai kualitas jawaban chatbot konsultasi pertanian.

PERTANYAAN PENGGUNA:
"{item['pertanyaan']}"

JAWABAN CHATBOT:
"{item['jawaban']}"

Nilai jawaban chatbot tersebut berdasarkan tiga kriteria berikut, masing-masing dengan skala 1 sampai 5:

1. Relevansi: Apakah jawaban sesuai dan menjawab pertanyaan yang diajukan?
2. Akurasi: Apakah informasi yang diberikan secara umum benar berdasarkan praktik pertanian yang berlaku?
3. Kejelasan: Apakah jawaban mudah dipahami oleh petani awam?

Balas HANYA dengan format JSON berikut, tanpa teks tambahan:
{{"relevansi": <angka 1-5>, "akurasi": <angka 1-5>, "kejelasan": <angka 1-5>, "alasan": "<penjelasan singkat 1 kalimat>"}}

"""
        output_lines.append(prompt)
        output_lines.append("-" * 100)
        output_lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"✅ {found}/10 prompt berhasil dibuat di file: {OUTPUT_FILE}")
    print(f"\nLangkah selanjutnya:")
    print(f"1. Buka file {OUTPUT_FILE}")
    print(f"2. Copy SATU prompt (dari === PROMPT N === sampai garis ----)")
    print(f"3. Paste ke Claude.ai atau ChatGPT")
    print(f"4. Catat hasil JSON yang dikembalikan")
    print(f"5. Ulangi untuk semua prompt")
    print(f"6. Kirim semua hasil JSON ke Claude (chat ini) untuk dibuatkan tabel skripsi")

    if found < 10:
        print(f"\n⚠️  Hanya {found}/10 pertanyaan ditemukan di log.")
        print(f"   Pertanyaan yang belum ada perlu dikirim ulang ke chatbot WhatsApp")
        print(f"   agar tersimpan di {LOG_FILE} sebelum menjalankan script ini lagi.")


if __name__ == "__main__":
    main()