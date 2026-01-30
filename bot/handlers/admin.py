from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from config import TIMEZONE
from bot.database import stats
from bot.utils.time import today, week

tz = pytz.timezone(TIMEZONE)

scheduler = AsyncIOScheduler(timezone=tz)

async def reset_today():
    await stats.update_many({}, {
        "$set": {
            "today.count": 0,
            "today.date": today()
        }
    })

async def reset_week():
    await stats.update_many({}, {
        "$set": {
            "week.count": 0,
            "week.week": week()
        }
    })

scheduler.add_job(reset_today, "cron", hour=0, minute=0)
scheduler.add_job(reset_week, "cron", day_of_week="mon", hour=0, minute=0)

scheduler.start()
