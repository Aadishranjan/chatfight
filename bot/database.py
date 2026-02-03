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


