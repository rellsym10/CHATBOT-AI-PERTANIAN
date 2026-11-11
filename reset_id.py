import json
import os

os.chdir(r"D:\CHATBOT AI PERTANIAN")

for filename in ["log_konsultasi.json", "log_pesan_teks.json"]:
    if not os.path.exists(filename):
        print(f"File tidak ditemukan: {filename}")
        continue

    # ✅ Tambahkan encoding="utf-8" saat membaca
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️  {filename} kosong atau rusak.")
            continue

    if not data:
        print(f"⚠️  {filename} tidak ada datanya.")
        continue

    print(f"\n{filename} — total data: {len(data)}")

    # Reset ID berurutan dari 1
    for i, item in enumerate(data):
        item["id"] = i + 1

    # ✅ Tambahkan encoding="utf-8" saat menulis agar emoji tidak error
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Berhasil reset: {filename} — {len(data)} data")