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


from bot.client import app

# FORCE IMPORT ALL HANDLERS
import bot.handlers.ranking
import bot.handlers.admin
import bot.handlers.start
import bot.handlers.counter

print("🔥 ChatFight Bot is running...")
app.run()
