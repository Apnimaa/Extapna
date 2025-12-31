from pyrogram import Client, filters
import os, sys, aiofiles, asyncio, io, shutil, subprocess
from datetime import datetime, timedelta
from urllib.parse import unquote

import pytz, requests, cloudscraper

from config import Config
import msg
import master.key as key
from database import db, standarddb

import logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

scraper = cloudscraper.create_scraper()
IST = pytz.timezone("Asia/Kolkata")

# ---------------- BOT INSTANCE ---------------- #

bot = Client(
    "Master",
    api_id=27433400,
    api_hash="1a286620de5ffe0a7d9b57e604293555",
    bot_token="8282655063:AAFKE7fkSPMg_nEiaV1gTKY87JK7Jgd-y7s"
)

# ---------------- THUMB SAFE ---------------- #

thumb = None
try:
    if subprocess.getstatusoutput(
        f"wget '{Config.THUMB_URL}' -O 'thumb.jpg'"
    )[0] == 0:
        thumb = "thumb.jpg"
except Exception as e:
    LOGGER.warning("Thumbnail download failed: %s", e)

# ---------------- COMMANDS ---------------- #

@bot.on_message(filters.command("status") & filters.private)
async def status_command(_, m):
    if m.chat.id not in Config.ADMIN_ID:
        return await m.reply_text("You are not authorized to use this command.")
    count = await db.db_instance.get_subscription_count()
    await m.reply_text(f"Number of subscribers: {count}")

@bot.on_message(filters.command("id"))
async def get_chat_id(_, m):
    await m.reply_text(f"<blockquote><b>Chat ID:</b></blockquote> `{m.chat.id}`")

@bot.on_message(filters.command("restart") & filters.private)
async def restart_handler(_, m):
    if m.chat.id not in Config.ADMIN_ID:
        return await m.reply_text("You are not authorized.")
    await m.reply_text("🚦 **RESTARTING** 🚦")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ---------------- BROADCAST ---------------- #

@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(bot, m):
    if m.chat.id not in Config.ADMIN_ID:
        return await m.reply_text("You are not authorized.")

    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.reply_text("Usage: /broadcast <message>")

    message = parts[1]
    subscribers = await db.db_instance.get_subscribers_collections()

    async for user in subscribers:
        try:
            await bot.send_message(user["_id"], message)
        except Exception as e:
            LOGGER.error("Broadcast failed to %s: %s", user["_id"], e)

    await m.reply_text("✅ Broadcast completed")

# ---------------- FILE CLEANER ---------------- #

async def clear_handler():
    exts = (".mp4", ".jpg", ".png", ".mkv", ".pdf", ".ts", ".m4a", ".mpd", ".m3u8", ".json", ".txt")
    for root, _, files in os.walk(os.getcwd()):
        for f in files:
            if f.endswith(exts):
                os.remove(os.path.join(root, f))

    if os.path.exists("temp"):
        shutil.rmtree("temp")

    LOGGER.info("Temporary files cleared")

# ---------------- STOP ---------------- #

@bot.on_message(filters.command("stop") & filters.private)
async def stop_command(_, m):
    uid = m.from_user.id
    if uid not in Config.ADMIN_ID and not await db.db_instance.get_premium_user(uid):
        return await m.reply_text(msg.UPGRADE, reply_markup=key.contact())

    await clear_handler()
    await m.reply_text("🚦 **STOPPED** 🚦")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ---------------- SAVE API ---------------- #

@bot.on_message(filters.command("saveapi") & filters.private)
async def save_api(bot, m):
    uid = m.chat.id
    access, _ = await db.db_instance.access_checking(uid)
    if not access:
        return await m.reply_text("❌ Access denied")

    ask = await m.reply_text("Send: `AppName:API_URL`", quote=True)
    reply = await bot.listen(uid)
    text = reply.text.strip()

    if ":" not in text:
        return await ask.edit("Invalid format")

    app, api = map(str.strip, text.split(":", 1))

    try:
        if "api" in api:
            r = requests.get(api, timeout=10)
            if r.status_code == 200:
                await standarddb.db_instance.insert_or_update_appx_api(app, api)
                await ask.edit(f"✅ API saved for {app}")
        else:
            r = scraper.get(api)
            cookie = r.headers.get("Set-Cookie", "")
            base = ""
            for part in cookie.split(";"):
                if part.strip().startswith("base_url="):
                    base = unquote(part.strip()[9:])
                    break
            if base:
                await standarddb.db_instance.insert_or_update_appx_api(app, base)
                await ask.edit(f"✅ API saved for {app}")
    except Exception as e:
        LOGGER.error("Save API error: %s", e)
        await ask.edit("❌ Failed to save API")
        


