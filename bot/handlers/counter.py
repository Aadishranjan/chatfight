from pyrogram import filters, types
from bot.client import app
from bot.database import stats
from bot.utils.time import today, week

@app.on_message(filters.group & ~filters.service)
async def counter(_, m):
    if not m.from_user:
        return
    
    if m.command:
        return

    chat_id = m.chat.id
    user = m.from_user

    await stats.update_one(
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
