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
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import time
import os

import bot.database as database
from bot.utils.time import today, week
from bot.utils.image import leaderboard_image

TOP_LIMIT = 10
RANKING_CACHE_TTL_SEC = 30
_ranking_text_cache = {}


def _cache_key(chat_id: int, mode: str):
    return (chat_id, mode)


def _cache_get(chat_id: int, mode: str):
    item = _ranking_text_cache.get(_cache_key(chat_id, mode))
    if not item:
        return None
    expires_at, value = item
    if time.monotonic() >= expires_at:
        _ranking_text_cache.pop(_cache_key(chat_id, mode), None)
        return None
    return value


def _cache_set(chat_id: int, mode: str, value: str):
    _ranking_text_cache[_cache_key(chat_id, mode)] = (
        time.monotonic() + RANKING_CACHE_TTL_SEC,
        value,
    )


# ---------- KEYBOARD ----------
def keyboard(mode: str = "overall"):
    overall_text = "✅ Overall" if mode == "overall" else "⏺️ Overall"
    today_text = "✅ Today" if mode == "today" else "⏺️ Today"
    week_text = "✅ Week" if mode == "week" else "⏺️ Week"
    
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(overall_text, callback_data="rank_overall"),
            ],
            [
                InlineKeyboardButton(today_text, callback_data="rank_today"),
                InlineKeyboardButton(week_text, callback_data="rank_week"),
            ]
        ]
    )


# ---------- TEXT BUILDER ----------
async def build_text(chat_id, mode):
    cached = _cache_get(chat_id, mode)
    if cached:
        return cached

    projection = {"_id": 0, "name": 1, "overall": 1, "today.count": 1, "week.count": 1}
    if mode == "overall":
        data = await database.stats.find(
            {"chat_id": chat_id},
            projection,
        ).sort("overall", -1).limit(TOP_LIMIT).to_list(TOP_LIMIT)

        title = "LEADERBOARD"
        get_count = lambda u: u.get("overall", 0)

    elif mode == "today":
        data = await database.stats.find(
            {"chat_id": chat_id, "today.date": today()},
            projection,
        ).sort("today.count", -1).limit(TOP_LIMIT).to_list(TOP_LIMIT)

        title = "TODAY LEADERBOARD"
        get_count = lambda u: u.get("today", {}).get("count", 0)

    else:  # week
        data = await database.stats.find(
            {"chat_id": chat_id, "week.week": week()},
            projection,
        ).sort("week.count", -1).limit(TOP_LIMIT).to_list(TOP_LIMIT)

        title = "WEEK LEADERBOARD"
        get_count = lambda u: u.get("week", {}).get("count", 0)

    if not data:
        text = "<b>📈 {}</b>\n\n<i>No data yet.</i>".format(title)
        _cache_set(chat_id, mode, text)
        return text

    text = "<b>📈 {}</b>\n\n".format(title)
    total = 0

    for i, u in enumerate(data, 1):
        c = get_count(u)
        total += c
        text += "<b>{}. {} • {}</b>\n".format(i, u['name'], c)

    text += "\n<b>✉️ Total messages: {}</b>".format(total)
    _cache_set(chat_id, mode, text)
    return text


# ---------- /ranking ----------
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only allow in groups
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text(
            "<b>This command only works in groups.</b>",
            parse_mode="HTML"
        )
        return

    m = update.effective_message
    chat = update.effective_chat
    chat_id = chat.id

    # ONLY OVERALL IMAGE
    data = await database.stats.find(
        {"chat_id": chat_id},
        {"_id": 0, "name": 1, "overall": 1},
    ).sort("overall", -1).limit(TOP_LIMIT).to_list(TOP_LIMIT)

    if not data:
        await m.reply_text(
            "<b>🏆 CHATFIGHT LEADERBOARD</b>\n\n<i>No data yet.</i>",
            reply_markup=keyboard("overall"),
            parse_mode="HTML"
        )
        return

    leaderboard_data = [
        {"name": u["name"], "count": u.get("overall", 0)}
        for u in data
    ]

    image_path = leaderboard_image(leaderboard_data, "LEADERBOARD")
    caption = await build_text(chat_id, "overall")

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=open(image_path, "rb"),
        caption=caption,
        reply_markup=keyboard("overall"),
        parse_mode="HTML"
    )

    # Delete the image after sending
    if os.path.exists(image_path):
        os.remove(image_path)


# ---------- CALLBACKS (TEXT ONLY) ----------
async def ranking_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat.id
    mode = q.data.replace("rank_", "")

    text = await build_text(chat_id, mode)
    try:
        await q.edit_message_caption(
            text,
            reply_markup=keyboard(mode),
            parse_mode="HTML",
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


def register(app):
    app.add_handler(CommandHandler("rankings", ranking))
    app.add_handler(CallbackQueryHandler(ranking_callback, pattern=r"^rank_"))


# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team
