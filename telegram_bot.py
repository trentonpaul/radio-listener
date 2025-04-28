from telegram import Bot
from telegram.error import TimedOut
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def send_message(message):
    asyncio.run(send_notification(message))

async def send_notification(message, retries=3):
    bot = Bot(token=bot_token)
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            break  # Success! Exit the loop
        except TimedOut:
            print(f"Attempt {attempt + 1} failed due to timeout.")
            if attempt < retries - 1:
                await asyncio.sleep(2)  # wait a bit before retrying
            else:
                print("All retry attempts failed.")
