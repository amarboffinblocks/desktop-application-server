from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
settings = Settings()

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client.get_default_database()


async def get_user_collection():
    col = db["users"]
    # Ensure unique index on email
    await col.create_index("email", unique=True)
    return col


def get_blacklist_collection():
    return db["token_blacklist"]


def get_access_blacklist_collection():
    return db["access_token_blacklist"]
