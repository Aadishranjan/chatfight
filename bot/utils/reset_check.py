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


# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team