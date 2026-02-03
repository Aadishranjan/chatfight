import bot.database as database
from bot.utils.time import today, week

async def reset_if_needed():
    # DAILY RESET
    await database.stats.update_many(
        {"today.date": {"$ne": today()}},
        {"$set": {"today.count": 0, "today.date": today()}}
    )

    # WEEKLY RESET
    await database.stats.update_many(
        {"week.week": {"$ne": week()}},
        {"$set": {"week.count": 0, "week.week": week()}}
    )
