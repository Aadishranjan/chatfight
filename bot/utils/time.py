from datetime import datetime
import pytz
from config import TIMEZONE

tz = pytz.timezone(TIMEZONE)

def today():
    return datetime.now(tz).strftime("%Y-%m-%d")

def week():
    return datetime.now(tz).strftime("%Y-%W")
