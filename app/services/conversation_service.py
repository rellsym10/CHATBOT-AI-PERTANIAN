import json
import os
import asyncio
from datetime import datetime, timedelta

CONV_FILE = "conversations.json"
MAX_HISTORY = 6
EXPIRY_MINUTES = 30

conversation_lock = asyncio.Lock()


def _read_json(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except:
        return {}


def _write_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def get_history(user_id):
    """Ambil riwayat percakapan, kosongkan jika sudah > 30 menit tidak aktif"""
    async with conversation_lock:
        data = _read_json(CONV_FILE)
        user_data = data.get(user_id)

        if not user_data:
            return []

        updated = datetime.fromisoformat(user_data["updated_at"])
        if datetime.now() - updated > timedelta(minutes=EXPIRY_MINUTES):
            return []

        return user_data["messages"]


async def add_message(user_id, role, content):
    """Tambah pesan baru ke riwayat, batasi MAX_HISTORY"""
    async with conversation_lock:
        data = _read_json(CONV_FILE)

        if user_id not in data:
            data[user_id] = {"messages": [], "updated_at": None}

        data[user_id]["messages"].append({"role": role, "content": content})
        data[user_id]["messages"] = data[user_id]["messages"][-MAX_HISTORY:]
        data[user_id]["updated_at"] = datetime.now().isoformat()

        _write_json(CONV_FILE, data)