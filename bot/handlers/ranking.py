from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import os

import bot.database as database
from bot.utils.time import today, week
from bot.utils.image import leaderboard_image


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
    if mode == "overall":
        data = await database.stats.find(
            {"chat_id": chat_id}
        ).sort("overall", -1).limit(10).to_list(10)

        title = "LEADERBOARD"
        get_count = lambda u: u.get("overall", 0)

    elif mode == "today":
        data = await database.stats.find(
            {"chat_id": chat_id, "today.date": today()}
        ).sort("today.count", -1).limit(10).to_list(10)

        title = "TODAY LEADERBOARD"
        get_count = lambda u: u.get("today", {}).get("count", 0)

    else:  # week
        data = await database.stats.find(
            {"chat_id": chat_id, "week.week": week()}
        ).sort("week.count", -1).limit(10).to_list(10)

        title = "WEEK LEADERBOARD"
        get_count = lambda u: u.get("week", {}).get("count", 0)

    if not data:
        return "<b>📈 {}</b>\n\n<i>No data yet.</i>".format(title)

    text = "<b>📈 {}</b>\n\n".format(title)
    total = 0

    for i, u in enumerate(data, 1):
        c = get_count(u)
        total += c
        text += "<b>{}. {} • {}</b>\n".format(i, u['name'], c)

    text += "\n<b>✉️ Total messages: {}</b>".format(total)
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
        {"chat_id": chat_id}
    ).sort("overall", -1).limit(10).to_list(10)

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
