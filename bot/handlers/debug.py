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

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config import DEBUG_UPDATES


async def debug_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not DEBUG_UPDATES:
        return

    m = update.effective_message
    if not m:
        return

    text = m.text or m.caption or ""
    from_id = m.from_user.id if m.from_user else None
    print(
        "DEBUG update: "
        f"chat_id={m.chat.id} "
        f"type={m.chat.type} "
        f"from_id={from_id} "
        f"text={text!r}"
    )


def register(app):
    app.add_handler(MessageHandler(filters.ALL, debug_updates))



# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team