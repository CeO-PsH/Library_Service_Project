import os

import requests


def send_to_telegram(message):
    apiToken = os.environ.get("TELEGRAM_BOT_API")
    chatID = os.environ.get("CHAT_ID")
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"

    try:
        response = requests.post(apiURL, json={"chat_id": chatID, "text": message})
        print(response.text)
    except Exception as e:
        print(e)
