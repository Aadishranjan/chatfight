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
                InlineKeyboardButton("Developer", url="tg://user?id=8223925872"), 
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