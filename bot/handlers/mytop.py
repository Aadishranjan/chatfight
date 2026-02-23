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
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import bot.database as database
from html import escape
import time

LIMIT = 5
CHAT_TITLE_TTL_SEC = 3600
_chat_title_cache = {}


def mytop_buttons(mode: str):
    overall_text = "✅ Overall" if mode == "overall" else "⏺️ Overall"
    today_text = "✅ Today" if mode == "today" else "⏺️ Today"
    week_text = "✅ Week" if mode == "week" else "⏺️ Week"
    
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    overall_text,
                    callback_data="mytop_overall" if mode != "overall" else "noop"
                ),
            ],
            [    
                InlineKeyboardButton(
                    today_text,
                    callback_data="mytop_today" if mode != "today" else "noop"
                ),
                InlineKeyboardButton(
                    week_text,
                    callback_data="mytop_week" if mode != "week" else "noop"
                ),
            ]
        ]
    )

async def get_mytop_text(context: ContextTypes.DEFAULT_TYPE, user_id, mode: str, user_first_name: str = "User"):
    field = {
        "today": "today.count",
        "week": "week.count",
        "overall": "overall"
    }[mode]

    cursor = (
        database.stats.find(
            {
                "user_id": user_id,
                field: {"$gt": 0}
            },
            {
                "_id": 0,
                "chat_id": 1,
                "chat_title": 1,
                "overall": 1,
                "today.count": 1,
                "week.count": 1,
            },
        )
        .sort(field, -1)
        .limit(LIMIT)
    )

    text = f"<b>📈 LEADERBOARD | {escape(user_first_name)}</b>\n\n"
    i = 1

    async for doc in cursor:
        chat_id = doc.get("chat_id")
        count = doc["today"]["count"] if mode == "today" else \
                doc["week"]["count"] if mode == "week" else doc["overall"]
        chat_name = await _resolve_chat_title(context, chat_id, doc.get("chat_title"))

        text += f"<b>{i}. 👥 {chat_name} • {count}</b>\n"
        i += 1

    if i == 1:
        text += "<b><i>No data found.</i></b>"

    return text


async def _resolve_chat_title(context: ContextTypes.DEFAULT_TYPE, chat_id: int, existing_title: str | None) -> str:
    if existing_title:
        safe_title = escape(existing_title)
        _chat_title_cache[chat_id] = (time.monotonic() + CHAT_TITLE_TTL_SEC, safe_title)
        return safe_title

    now = time.monotonic()
    cached = _chat_title_cache.get(chat_id)
    if cached and now < cached[0]:
        return cached[1]

    group_doc = await database.groups.find_one({"chat_id": chat_id}, {"_id": 0, "title": 1})
    if group_doc and group_doc.get("title"):
        safe_title = escape(group_doc["title"])
        _chat_title_cache[chat_id] = (now + CHAT_TITLE_TTL_SEC, safe_title)
        await database.stats.update_many(
            {"chat_id": chat_id, "chat_title": {"$in": [None, ""]}},
            {"$set": {"chat_title": group_doc["title"]}},
        )
        return safe_title

    title = "Unknown Group"
    try:
        chat = await context.bot.get_chat(chat_id)
        title = getattr(chat, "title", None) or title
    except Exception:
        pass

    safe_title = escape(title)
    _chat_title_cache[chat_id] = (now + CHAT_TITLE_TTL_SEC, safe_title)

    if title != "Unknown Group":
        await database.groups.update_one(
            {"chat_id": chat_id},
            {"$set": {"title": title}},
            upsert=True,
        )
        await database.stats.update_many(
            {"chat_id": chat_id, "chat_title": {"$in": [None, ""]}},
            {"$set": {"chat_title": title}},
        )

    return safe_title


async def mytop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    text = await get_mytop_text(context, user_id, "overall", user_first_name)


    await update.effective_message.reply_text(
        text,
        reply_markup=mytop_buttons("overall"),
        parse_mode="HTML"
    )


async def mytop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.split("_")[1]
    user_first_name = query.from_user.first_name

    text = await get_mytop_text(context, query.from_user.id, mode, user_first_name)

    await query.edit_message_text(
        text,
        reply_markup=mytop_buttons(mode),
        parse_mode="HTML"
    )


def register(app):
    app.add_handler(CommandHandler("mytop", mytop_cmd))
    app.add_handler(CallbackQueryHandler(mytop_callback, pattern=r"^mytop_"))




# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team
