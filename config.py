from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
OWNER_USERNAME = os.getenv("OWNER_USERNAME")
BOT_NAME = os.getenv("BOT_NAME")
BOT_USERNAME = os.getenv("BOT_USERNAME")
UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL")
TIMEZONE = "Asia/Kolkata"