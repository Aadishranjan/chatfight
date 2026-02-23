# Copyright (c) 2026 Aadish Ranjan
# Location: India
#
# All rights reserved.
#
# This code is the intellectual property of Aadish Ranjan.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Project: aadishranjan35@gmail.com


from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes, CommandHandler

from config import BOT_USERNAME, UPDATES_CHANNEL, OWNER_ID


def _build_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Add me to Group",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                ),
            ],
            [
                InlineKeyboardButton("Owner", url=f"tg://user?id={OWNER_ID}"),
                InlineKeyboardButton("Developer", url="tg://user?id=8433938551"), 
            ],
            [
                InlineKeyboardButton("Updates", url=f"https://t.me/{UPDATES_CHANNEL}"),
            ]
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = _build_keyboard()

    if update.effective_chat.type == "private":
        welcome_text = (
            "🤖 Welcome, this bot will count group messages, "
            "create rankings and give prizes to users!"
        )
    else:
        welcome_text = (
            "🤖 Welcome to the group chat fight bot! "
            "This bot will count group messages, "
            "create rankings and give prizes to users!"
        )

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("assets/logo.png", "rb"),
        caption=welcome_text,
        reply_markup=keyboard
    )


def register(app):
    app.add_handler(CommandHandler("start", start))


# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team    