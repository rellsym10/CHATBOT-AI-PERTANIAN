import requests
from app.config import WHATSAPP_TOKEN, PHONE_NUMBER_ID
import os

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}

# fungsi membagi pesan panjang
def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]


def send_whatsapp_message(phone, message):
    messages = split_message(message)
    for msg in messages:

        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {
                "body": msg
            }
        }
        response = requests.post(WHATSAPP_URL, headers=headers, json=data)
        print("WhatsApp Response:", response.text)
        print("SENDING MESSAGE TO:", phone)
        print("MESSAGE SENT")

def download_image(image_id):
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    url = f"https://graph.facebook.com/v20.0/{image_id}"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    print("MEDIA DATA:", data)

    if "url" not in data:
        raise Exception("URL gambar tidak ditemukan")

    image_url = data["url"]
    image_response = requests.get(image_url, headers=headers)
    file_path = f"downloads/{image_id}.jpg"
    
    os.makedirs("downloads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(image_response.content)

    print("Image saved:", file_path)
    return file_path