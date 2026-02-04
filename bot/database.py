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

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

# Initialize these lazily in `init_db()` so the Motor client
# is created after the asyncio event loop is running.
mongo = None
db = None

stats = None
groups = None


def init_db():
	global mongo, db, stats, groups
	if mongo is None:
		mongo = AsyncIOMotorClient(MONGO_URL)
		db = mongo.chatfight
		stats = db.stats
		groups = db.groups



# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team