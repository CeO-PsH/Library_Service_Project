import os

import requests


def send_to_telegram(message: str) -> None:
    apiToken = os.environ.get("TELEGRAM_BOT_API")
    chatID = os.environ.get("CHAT_ID")
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"

    try:
        requests.post(apiURL, json={"chat_id": chatID, "text": message})
    except Exception as error:
        print(error)
