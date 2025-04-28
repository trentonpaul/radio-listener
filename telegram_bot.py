from telegram import Bot
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def send_message(message):
    asyncio.run(send_notification(message))

async def send_notification(message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)