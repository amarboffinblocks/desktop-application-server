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


async def get_chat_session_collection():
    return db["chat_sessions"]

async def get_message_collection():
    return db["messages"]

async def get_characters_collection():
    return db["characters"]

async def get_votes_collection():
    return db["votes"]

async def get_favourites_collection():
    return db["favourites"]

async def get_tags_collection():
    return db["tags"]

async def get_chats_collection():
    return db["chats"]
async def get_chat_messages_collection():
    return db["chat_messages"]