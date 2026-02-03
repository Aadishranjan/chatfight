# Copyright (c) 2026 Aadish Ranjan
# Location: India
#
# All rights reserved.
#
# This code is the intellectual property of Aadish Ranjan.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Project: aadishranjan35@gmail.com


import asyncio
import logging
from datetime import time, datetime, timedelta
import zoneinfo

from bot.client import build_app
from bot.utils.reset_check import reset_if_needed
from config import TIMEZONE

# handlers (import modules explicitly to avoid package `__all__` collisions)
import importlib
mytop = importlib.import_module("bot.handlers.mytop")
ranking = importlib.import_module("bot.handlers.ranking")
start_handler = importlib.import_module("bot.handlers.start")
counter = importlib.import_module("bot.handlers.counter")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Suppress verbose logs from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    print("Starting ChatFight Bot...")

    app = build_app()

    # initialize database immediately (sync)
    from bot.database import init_db
    init_db()

    # schedule async reset after app starts
    async def _run_reset(context):
        await reset_if_needed()

    app.job_queue.run_once(_run_reset, when=0)

    # register handlers
    mytop.register(app)
    ranking.register(app)
    start_handler.register(app)
    counter.register(app)

    # schedule daily reset at 00:00 in configured timezone
    tz = zoneinfo.ZoneInfo(TIMEZONE)
    app.job_queue.run_daily(lambda ctx: asyncio.create_task(reset_if_needed()), time=time(0, 0, 0, tzinfo=tz))

    app.run_polling()


if __name__ == "__main__":
    main()
