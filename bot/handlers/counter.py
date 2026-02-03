from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
import bot.database as database
from bot.utils.time import today, week


async def counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = update.effective_message
    if not m or not m.from_user:
        return

    # ignore commands
    if m.text and m.text.startswith("/"):
        return

    chat_id = update.effective_chat.id
    user = m.from_user

    await database.stats.update_one(
        {"chat_id": chat_id, "user_id": user.id},
        {
            "$set": {
                "name": user.first_name,
                "username": user.username,
                "today.date": today(),
                "week.week": week()
            },
            "$inc": {
                "overall": 1,
                "today.count": 1,
                "week.count": 1
            }
        },
        upsert=True
    )


def register(app):
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.StatusUpdate.ALL, counter))
