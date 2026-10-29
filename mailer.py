# server/mailer.py
import os
import random
import httpx

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def send_code(chat_id: str, code: str) -> bool:
    if not BOT_TOKEN:
        print("[mailer] TELEGRAM_BOT_TOKEN пустой")
        return False
    if not chat_id:
        print("[mailer] chat_id пустой")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"твой код: {code}\nдействует 10 минут.",
    }
    try:
        r = httpx.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"[mailer] код ушёл в chat_id={chat_id}")
            return True
        print(f"[mailer] telegram error: {r.text}")
        return False
    except Exception as e:
        print(f"[mailer] fail: {e}")
        return False


def generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"