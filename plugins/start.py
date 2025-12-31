
from pyrogram import Client, filters

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user = message.from_user
    name = user.first_name if user else "User"

    await message.reply_text(
        f"👋 Hello {name}!\n\n"
        "✅ Bot is running successfully.\n"
        "🚀 /help for more commands."
    )
