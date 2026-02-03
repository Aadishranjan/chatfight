from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import bot.database as database
from bot.utils.time import today, week
from typing import Callable

LIMIT = 5


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
            }
        )
        .sort(field, -1)
        .limit(LIMIT)
    )

    text = f"<b>📈 LEADERBOARD | {user_first_name}</b>\n\n"
    i = 1

    async for doc in cursor:
        chat_id = doc["chat_id"]
        count = doc["today"]["count"] if mode == "today" else \
                doc["week"]["count"] if mode == "week" else doc["overall"]

        try:
            chat = await context.bot.get_chat(chat_id)
            chat_name = getattr(chat, "title", str(chat_id))
        except:
            chat_name = "Unknown Group"

        text += f"<b>{i}. 👥 {chat_name} • {count}</b>\n"
        i += 1

    if i == 1:
        text += "<b><i>No data found.</i></b>"

    return text


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
