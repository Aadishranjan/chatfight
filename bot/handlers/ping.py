# Copyright (c) 2026 Aadish Ranjan

import asyncio
import io
import logging
import time

from telegram import Update, InputFile
from telegram.error import TimedOut
from telegram.ext import CommandHandler, ContextTypes

from bot.utils.image import system_stats_image_bytes
from bot.utils.system_stats import collect_system_stats

logger = logging.getLogger(__name__)
BOT_START_MONOTONIC = time.monotonic()


def _format_uptime(seconds: float) -> str:
    total = int(max(seconds, 0))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours}h:{minutes}m:{secs}s"


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    bot_username = context.bot.username
    bot_mention = f"@{bot_username}" if bot_username else "Bot"

    stats = await collect_system_stats()
    bot_uptime = _format_uptime(time.monotonic() - BOT_START_MONOTONIC)
    caption = (
        f"{bot_mention} ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ :\n\n"
        f"↬ ᴜᴘᴛɪᴍᴇ : {bot_uptime}\n"
        f"↬ ʀᴀᴍ : {stats['ram_percent']}%\n"
        f"↬ ᴄᴘᴜ : {stats['cpu_percent']}%\n"
        f"↬ ᴅɪꜱᴋ : {stats['disk_percent']}%"
    )

    lines = [
        f"↬ uptime : {bot_uptime}",
        f"↬ ram : {stats['ram_percent']}%",
        f"↬ cpu : {stats['cpu_percent']}%",
        f"↬ disk : {stats['disk_percent']}%",
    ]
    image_bytes = system_stats_image_bytes(lines, title="SYSTEM STATS")

    try:
        for attempt in range(2):
            try:
                photo = InputFile(io.BytesIO(image_bytes), filename="system_stats.png")
                await message.reply_photo(
                    photo=photo,
                    caption=caption,
                    connect_timeout=10,
                    write_timeout=30,
                    read_timeout=30,
                    pool_timeout=10,
                )
                break
            except TimedOut:
                if attempt == 0:
                    await asyncio.sleep(1)
                    continue
                raise
    except TimedOut:
        logger.warning("ping send_photo timed out; sending text fallback")
        await message.reply_text(caption)


def register(app):
    app.add_handler(CommandHandler("ping", ping))
