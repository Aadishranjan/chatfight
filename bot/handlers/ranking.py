from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.client import app
from bot.database import stats
from bot.utils.time import today, week
from bot.utils.image import leaderboard_image


# ---------- KEYBOARD ----------
def keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏺️ Overall", callback_data="rank_overall"),
            ],
            [
                InlineKeyboardButton("⏺️ Today", callback_data="rank_today"),
                InlineKeyboardButton("⏺️ Week", callback_data="rank_week"),
            ]
        ]
    )


# ---------- TEXT BUILDER ----------
async def build_text(chat_id, mode):
    if mode == "overall":
        data = await stats.find(
            {"chat_id": chat_id}
        ).sort("overall", -1).limit(10).to_list(10)

        title = "LEADERBOARD"
        get_count = lambda u: u.get("overall", 0)

    elif mode == "today":
        data = await stats.find(
            {"chat_id": chat_id, "today.date": today()}
        ).sort("today.count", -1).limit(10).to_list(10)

        title = "TODAY LEADERBOARD"
        get_count = lambda u: u.get("today", {}).get("count", 0)

    else:  # week
        data = await stats.find(
            {"chat_id": chat_id, "week.week": week()}
        ).sort("week.count", -1).limit(10).to_list(10)

        title = "WEEK LEADERBOARD"
        get_count = lambda u: u.get("week", {}).get("count", 0)

    if not data:
        return f"📈 **{title}**\n\n_No data yet._"

    text = f"📈 **{title}**\n\n"
    total = 0

    for i, u in enumerate(data, 1):
        c = get_count(u)
        total += c
        text += f"{i}. {u['name']} • `{c}`\n"

    text += f"\n✉️ Total messages: `{total}`"
    return text


# ---------- /ranking ----------
@app.on_message(filters.command("rankings", prefixes="/"))
async def ranking(_, m):
    chat_id = m.chat.id

    # ONLY OVERALL IMAGE
    data = await stats.find(
        {"chat_id": chat_id}
    ).sort("overall", -1).limit(10).to_list(10)

    if not data:
        await m.reply_text(
            "🏆 **CHATFIGHT LEADERBOARD**\n\n_No data yet._",
            reply_markup=keyboard()
        )
        return

    leaderboard_data = [
        {"name": u["name"], "count": u.get("overall", 0)}
        for u in data
    ]

    image_path = leaderboard_image(leaderboard_data, "LEADERBOARD")
    caption = await build_text(chat_id, "overall")

    await m.reply_photo(
        image_path,
        caption=caption,
        reply_markup=keyboard()
    )


# ---------- CALLBACKS (TEXT ONLY) ----------
@app.on_callback_query(filters.regex("^rank_"))
async def ranking_callback(_, q):
    chat_id = q.message.chat.id
    mode = q.data.replace("rank_", "")

    text = await build_text(chat_id, mode)

    await q.edit_message_caption(
        text,
        reply_markup=keyboard()
    )
    await q.answer()
