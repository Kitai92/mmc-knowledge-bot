
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Получаем переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# URL для отправки сообщений в Telegram
TELEGRAM_SEND_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_message(chat_id, text):
    """Отправка сообщения пользователю через Telegram API"""
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(TELEGRAM_SEND_URL, json=payload)

def query_openai(user_message):
    """
    Отправка запроса к OpenAI Assistant и получение ответа.
    Этот пример использует запрос к тестовому API-эндоинту.
    Необходима настройка согласно документации OpenAI.
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v1"
    }
    
    payload = {
        "messages": [{"role": "user", "content": user_message}],
        "assistant_id": ASSISTANT_ID
    }
    
    response = requests.post(
        "https://api.openai.com/v1/threads",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        try:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return "Ошибка при обработке ответа OpenAI."
    else:
        return f"Ошибка OpenAI API: {response.status_code}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    """
    Обработчик webhook Telegram.
    При получении сообщения от Telegram, пересылает его в OpenAI Assistant и отправляет ответ обратно.
    """
    data = request.get_json()
    
    try:
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        user_message = message.get("text", "")
    except Exception:
        return jsonify(ok=False)
    
    if not chat_id or not user_message:
        return jsonify(ok=False)
    
    openai_reply = query_openai(user_message)
    
    send_message(chat_id, openai_reply)
    
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
