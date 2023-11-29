from celery import shared_task
import requests
from config import settings


@shared_task
def send_telegram_message(**kwargs):
    params = {'chat_id': kwargs['chat_id'], 'text': f"Я буду {kwargs['action']} в {kwargs['time']} в {kwargs['place']}"}
    message = requests.post(f'https://api.telegram.org/bot{settings.BOT_API_TOKEN}/sendMessage', params=params)
    print(message.status_code)
