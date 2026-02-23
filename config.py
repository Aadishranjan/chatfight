from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
OWNER_USERNAME = os.getenv("OWNER_USERNAME")
OWNER_ID = int(os.getenv("OWNER_ID"))
EXTRA_OWNER_IDS = [
    int(x.strip())
    for x in os.getenv("EXTRA_OWNER_IDS", "").split(",")
    if x.strip().isdigit()
]
BOT_NAME = os.getenv("BOT_NAME")
BOT_USERNAME = os.getenv("BOT_USERNAME")
UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL")
TIMEZONE = "Asia/Kolkata"

UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "https://github.com/Aadishranjan/chatfight")
UPSTREAM_BRANCH = os.getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = os.getenv("GIT_TOKEN", None)


# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team
