from telegram import Bot
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def send_message(message):
    asyncio.run(send_notification(message))

async def send_notification(message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=f'101.9 THE MIX ALERT: {message}')