import re
import time
from html import escape
from typing import Dict

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

import bot.database as database
from bot.handlers.counter import get_chat_buffer_snapshot

TOP_LIMIT = 10
CACHE_TTL_SEC = 30
_activity_cache = {}
USERSTATS_USAGE_TEXT = (
    "<b>Usage:</b> /userstats <reply/@username/user_id>\n"
    "Reply to a user's message or pass @username/user_id."
)


def _format_name(name: str, username: str | None) -> str:
    safe_name = escape(name)
    if username:
        return f"{safe_name} (@{escape(username)})"
    return safe_name


def _cache_get(key):
    item = _activity_cache.get(key)
    if not item:
        return None
    expires_at, value = item
    if time.monotonic() >= expires_at:
        _activity_cache.pop(key, None)
        return None
    return value


def _cache_set(key, value):
    _activity_cache[key] = (time.monotonic() + CACHE_TTL_SEC, value)


async def topusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text(
            "<b>This command only works in groups.</b>",
            parse_mode="HTML",
        )
        return

    chat_id = update.effective_chat.id
    cache_key = ("topusers", chat_id)
    cached = _cache_get(cache_key)
    if cached:
        await update.effective_message.reply_text(cached, parse_mode="HTML")
        return

    data = await database.stats.find(
        {"chat_id": chat_id},
        {"_id": 0, "user_id": 1, "name": 1, "username": 1, "overall": 1},
    ).sort("overall", -1).limit(TOP_LIMIT).to_list(TOP_LIMIT)
    buffered = await get_chat_buffer_snapshot(chat_id)

    merged: Dict[int, Dict[str, object]] = {}
    for doc in data:
        merged[doc["user_id"]] = {
            "name": doc.get("name") or "User",
            "username": doc.get("username"),
            "count": int(doc.get("overall", 0)),
        }

    for user_id, entry in buffered.items():
        record = merged.get(user_id)
        if record is None:
            merged[user_id] = {
                "name": entry.get("name") or "User",
                "username": entry.get("username"),
                "count": int(entry.get("count", 0)),
            }
            continue
        record["count"] = int(record["count"]) + int(entry.get("count", 0))
        if entry.get("name"):
            record["name"] = entry["name"]
        if entry.get("username"):
            record["username"] = entry["username"]

    if not merged:
        await update.effective_message.reply_text(
            "<b>📈 ACTIVITY TRACKER</b>\n\n<i>No activity data yet.</i>",
            parse_mode="HTML",
        )
        return

    top = sorted(merged.values(), key=lambda x: int(x["count"]), reverse=True)[:TOP_LIMIT]
    lines = ["<b>📈 ACTIVITY TRACKER</b>", "", "<b>Top 10 active users:</b>", ""]
    for idx, user in enumerate(top, start=1):
        lines.append(f"<b>{idx}. {_format_name(user['name'], user.get('username'))} • {int(user['count'])}</b>")

    text = "\n".join(lines)
    _cache_set(cache_key, text)
    await update.effective_message.reply_text(text, parse_mode="HTML")


async def userstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text(
            "<b>This command only works in groups.</b>",
            parse_mode="HTML",
        )
        return

    target_user = None
    if update.effective_message.reply_to_message and update.effective_message.reply_to_message.from_user:
        target_user = update.effective_message.reply_to_message.from_user
    elif context.args:
        arg = context.args[0].strip()
        if arg.isdigit():
            target_id = int(arg)
            cache_key = ("userstats", update.effective_chat.id, str(target_id))
            cached = _cache_get(cache_key)
            if cached:
                await update.effective_message.reply_text(cached, parse_mode="HTML")
                return
            doc = await database.stats.find_one(
                {"chat_id": update.effective_chat.id, "user_id": target_id},
                {"_id": 0, "user_id": 1, "name": 1, "username": 1, "overall": 1},
                sort=[("overall", -1)],
            )
        else:
            username = arg[1:] if arg.startswith("@") else arg
            username_lc = username.lower()
            cache_key = ("userstats", update.effective_chat.id, username_lc)
            cached = _cache_get(cache_key)
            if cached:
                await update.effective_message.reply_text(cached, parse_mode="HTML")
                return
            doc = await database.stats.find_one(
                {
                    "chat_id": update.effective_chat.id,
                    "username_lc": username_lc,
                },
                {"_id": 0, "user_id": 1, "name": 1, "username": 1, "overall": 1},
                sort=[("overall", -1)],
            )
            if not doc:
                doc = await database.stats.find_one(
                    {
                        "chat_id": update.effective_chat.id,
                        "username": {"$regex": f"^{re.escape(username)}$", "$options": "i"},
                    },
                    {"_id": 0, "user_id": 1, "name": 1, "username": 1, "overall": 1},
                    sort=[("overall", -1)],
                )
        if doc:
            buffered = await get_chat_buffer_snapshot(update.effective_chat.id)
            pending = int(buffered.get(doc["user_id"], {}).get("count", 0))
            total = int(doc.get("overall", 0)) + pending
            text = (
                "<b>📈 USER STATS</b>\n\n"
                f"<b>User:</b> {_format_name(doc.get('name') or 'User', doc.get('username'))}\n"
                f"<b>Messages:</b> {total}"
            )
            _cache_set(cache_key, text)
            await update.effective_message.reply_text(
                text,
                parse_mode="HTML",
            )
            return
        await update.effective_message.reply_text(
            "<b>User not found.</b>\n" + USERSTATS_USAGE_TEXT,
            parse_mode="HTML",
        )
        return

    if target_user is None:
        await update.effective_message.reply_text(
            USERSTATS_USAGE_TEXT,
            parse_mode="HTML",
        )
        return

    chat_id = update.effective_chat.id
    user_id = target_user.id
    cache_key = ("userstats", chat_id, str(user_id))
    cached = _cache_get(cache_key)
    if cached:
        await update.effective_message.reply_text(cached, parse_mode="HTML")
        return

    doc = await database.stats.find_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"_id": 0, "overall": 1},
    )
    buffered = await get_chat_buffer_snapshot(chat_id)
    pending = int(buffered.get(user_id, {}).get("count", 0))

    stored = int(doc.get("overall", 0)) if doc else 0
    total = stored + pending
    name = target_user.first_name
    username = target_user.username

    text = (
        "<b>📈 USER STATS</b>\n\n"
        f"<b>User:</b> {_format_name(name, username)}\n"
        f"<b>Messages:</b> {total}"
    )
    _cache_set(cache_key, text)
    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
    )


def register(app):
    app.add_handler(CommandHandler("topusers", topusers))
    app.add_handler(CommandHandler("userstats", userstats))
