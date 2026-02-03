import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from pymongo import UpdateOne
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

import bot.database as database
from bot.utils.time import today, week

FLUSH_INTERVAL_SEC = 60
SPAM_WINDOW_SEC = 10
SPAM_THRESHOLD = 10
SPAM_BLOCK_SEC = 20 * 60

# (chat_id, user_id) -> {count, name, username}
_buffer: Dict[Tuple[int, int], Dict[str, object]] = {}
# (chat_id, user_id) -> deque[timestamps]
_recent_messages: Dict[Tuple[int, int], Deque[float]] = defaultdict(deque)
# (chat_id, user_id) -> blocked_until timestamp
_blocked_until: Dict[Tuple[int, int], float] = {}
_buffer_lock = asyncio.Lock()


async def counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = update.effective_message
    if not m or not m.from_user:
        return

    # ignore commands
    if m.text and m.text.startswith("/"):
        return

    chat_id = update.effective_chat.id
    user = m.from_user
    key = (chat_id, user.id)
    now = time.monotonic()

    blocked_until = _blocked_until.get(key)
    if blocked_until:
        if now < blocked_until:
            return
        _blocked_until.pop(key, None)

    recent = _recent_messages[key]
    cutoff = now - SPAM_WINDOW_SEC
    while recent and recent[0] < cutoff:
        recent.popleft()
    recent.append(now)

    if len(recent) >= SPAM_THRESHOLD:
        _blocked_until[key] = now + SPAM_BLOCK_SEC
        recent.clear()
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="⛔️ {} is flooding: blocked for 20 minutes for using the bot.".format(user.first_name),
            )
        except Exception:
            pass
        return

    async with _buffer_lock:
        entry = _buffer.get(key)
        if entry is None:
            entry = {"count": 0, "name": user.first_name, "username": user.username}
            _buffer[key] = entry
        entry["count"] = int(entry["count"]) + 1
        entry["name"] = user.first_name
        entry["username"] = user.username


async def _flush_counts(context: ContextTypes.DEFAULT_TYPE):
    async with _buffer_lock:
        if not _buffer:
            return
        snapshot = _buffer.copy()
        _buffer.clear()

    ops = []
    for (chat_id, user_id), data in snapshot.items():
        count = int(data.get("count", 0))
        if count <= 0:
            continue
        ops.append(
            UpdateOne(
                {"chat_id": chat_id, "user_id": user_id},
                {
                    "$set": {
                        "name": data.get("name"),
                        "username": data.get("username"),
                        "today.date": today(),
                        "week.week": week(),
                    },
                    "$inc": {
                        "overall": count,
                        "today.count": count,
                        "week.count": count,
                    },
                },
                upsert=True,
            )
        )

    if ops:
        await database.stats.bulk_write(ops, ordered=False)


def register(app):
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.StatusUpdate.ALL, counter))
    app.job_queue.run_repeating(
        _flush_counts,
        interval=FLUSH_INTERVAL_SEC,
        first=FLUSH_INTERVAL_SEC,
        job_kwargs={
            "coalesce": True,
            "misfire_grace_time": FLUSH_INTERVAL_SEC * 2,
        },
    )
