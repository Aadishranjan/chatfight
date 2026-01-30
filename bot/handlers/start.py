from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.client import app

from config import BOT_USERNAME, OWNER_USERNAME, UPDATES_CHANNEL


@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Add me to Group",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                ),
            ],
            [
                InlineKeyboardButton("Owner", url=f"https://t.me/{OWNER_USERNAME}"),
                InlineKeyboardButton("Developer", url="https://t.me/aakshi1209"),
            ],
            [
                InlineKeyboardButton("Updates", url=f"https://t.me/{UPDATES_CHANNEL}"),
            ]
        ]
    )

    welcome_text = (
        "🤖 Welcome, this bot will count group messages, "
        "create rankings and give prizes to users!"
    )

    await client.send_photo(
        chat_id=message.chat.id,
        photo="assets/logo.png",
        caption=welcome_text,
        reply_markup=keyboard
    )

