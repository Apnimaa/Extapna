import asyncio
import logging
from pyrogram import Client, idle
from config import Config

logging.basicConfig(level=logging.INFO)

bot = Client(
    "Master",
    api_id=27433400,
    api_hash="1a286620de5ffe0a7d9b57e604293555",
    bot_token="8282655063:AAFKE7fkSPMg_nEiaV1gTKY87JK7Jgd-y7s",
    plugins=dict(root="plugins")
)

async def main():
    await bot.start()
    logging.info("Bot started successfully.")
    await idle()
    await bot.stop()
    logging.info("Bot stopped.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
