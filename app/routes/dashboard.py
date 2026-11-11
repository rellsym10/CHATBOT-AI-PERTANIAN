from fastapi import APIRouter
import json
import os

router = APIRouter()

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


@router.get("/stats")
def get_stats():

    konsultasi = load_json("log_konsultasi.json")
    teks       = load_json("log_pesan_teks.json")

    total_gambar = len(konsultasi)
    total_teks   = len(teks)
    total_semua  = total_gambar + total_teks

    # Hitung deteksi berhasil vs gagal
    berhasil = sum(1 for d in konsultasi if "tidak" not in d["detection_result"].lower())
    gagal    = total_gambar - berhasil

    # Rata-rata waktu respons
    times = [d["response_time_sec"] for d in konsultasi if d.get("response_time_sec")]
    avg_time = round(sum(times) / len(times), 2) if times else 0

    # Distribusi penyakit terdeteksi
    penyakit = {}
    for d in konsultasi:
        if "tidak" not in d["detection_result"].lower():
            label = d["detection_result"].split("(")[0].strip()
            penyakit[label] = penyakit.get(label, 0) + 1

    # Pengguna unik
    semua_user = set(
        [d["user"] for d in konsultasi] +
        [d["user"] for d in teks]
    )

    return {
        "ringkasan": {
            "total_konsultasi"       : total_semua,
            "total_konsultasi_gambar": total_gambar,
            "total_konsultasi_teks"  : total_teks,
            "total_pengguna_unik"    : len(semua_user)
        },
        "deteksi_penyakit": {
            "berhasil"              : berhasil,
            "gagal"                 : gagal,
            "akurasi_persen"        : round(berhasil / max(total_gambar, 1) * 100, 2),
            "rata_waktu_respons_det": avg_time,
            "distribusi_penyakit"   : penyakit
        }
    }


@router.get("/logs/gambar")
def get_logs_gambar():
    return load_json("log_konsultasi.json")


@router.get("/logs/teks")
def get_logs_teks():
    return load_json("log_pesan_teks.json")

