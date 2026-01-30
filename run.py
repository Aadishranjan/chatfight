from bot.client import app

# FORCE IMPORT ALL HANDLERS
import bot.handlers.ranking
import bot.handlers.admin
import bot.handlers.start
import bot.handlers.counter

print("🔥 ChatFight Bot is running...")
app.run()
