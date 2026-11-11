import json
import os
from datetime import datetime

LOG_FILE = "log_konsultasi.json"
TEXT_LOG = "log_pesan_teks.json"


def get_next_id(data):
    if not data:
        return 1
    return max(item.get("id", 0) for item in data) + 1


def _read_json(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []


def _write_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_consultation(user, image, result, response_time=None, message_type="image"):
    data = _read_json(LOG_FILE)

    data.append({
        "id": get_next_id(data),
        "user": user,
        "message_type": message_type,
        "image": image,
        "detection_result": result,
        "response_time_sec": response_time,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    _write_json(LOG_FILE, data)


def save_text_log(user, user_text, ai_response, response_time=None):
    data = _read_json(TEXT_LOG)

    data.append({
        "id": get_next_id(data),
        "user": user,
        "pertanyaan": user_text,
        "jawaban": ai_response,
        "response_time_sec": response_time,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    _write_json(TEXT_LOG, data)