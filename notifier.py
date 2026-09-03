"""
Telegram Bot API se message bhejta hai. Bot token aur chat id
Render environment variables se aayenge.

Setup (ek baar karna hai):
1. Telegram pe @BotFather ko message karo -> /newbot -> naam do -> token milega
2. Apne bot ko Telegram pe search karke /start bhejo
3. Apna chat_id nikalne ke liye: https://api.telegram.org/bot<TOKEN>/getUpdates
   khol ke browser me, wahan "chat":{"id": ...} milega
"""
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, REQUEST_TIMEOUT

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_job_alert(source: str, title: str, company: str, location: str,
                    experience_text: str, link: str):
    text = (
        f"🆕 *{title}*\n"
        f"🏢 {company}\n"
        f"📍 {location or 'Not specified'}\n"
        f"🎯 Experience: {experience_text or 'Not specified'}\n"
        f"🔗 Source: {source}\n"
        f"👉 {link}"
    )
    _send(text)


def send_text(text: str):
    _send(text)


def _send(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notifier] TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set, skipping send.")
        print(text)
        return
    try:
        resp = requests.post(
            TELEGRAM_API,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            print(f"[notifier] Telegram send failed: {resp.status_code} {resp.text}")
    except requests.RequestException as e:
        print(f"[notifier] Telegram send error: {e}")
