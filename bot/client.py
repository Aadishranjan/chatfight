from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN


def build_app():
    return ApplicationBuilder().token(BOT_TOKEN).build()
