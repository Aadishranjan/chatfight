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
