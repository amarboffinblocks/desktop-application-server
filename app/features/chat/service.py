from fastapi import HTTPException, status
from app.features.characters.schemas import CharacterModel
from app.db.mongo import get_characters_collection
from bson.objectid import ObjectId

class ChatService:
    @staticmethod
    async def get_character_by_id(character_id: str):
        db = await get_characters_collection()
        character = await db.find_one({"_id": ObjectId(character_id)})
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with id {character_id} not found"
            )
        return CharacterModel(**character)
    @staticmethod
    async def get_chat_history_by_id(chat_id: str):
        db = await get_characters_collection()
        chat_history = await db.find_one({"_id": ObjectId(chat_id)})
        if not chat_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat history with id {chat_id} not found"
            )
        return chat_history.get("messages", [])

