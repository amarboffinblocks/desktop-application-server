from fastapi import HTTPException, status
from app.features.characters.schemas import CharacterModel
from app.db.mongo import get_characters_collection, get_chats_collection
from bson.objectid import ObjectId
from datetime import datetime, timezone   
from app.features.chat.schemas import ChatSession,ChatMessage,MessageContent
from typing import Optional
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
    async def create_chat_session(user_id: str, title: str, model: Optional[str] = None, character_id: Optional[str] = None)-> ChatSession:
        try:
            db = await get_chats_collection()
            chat_session = ChatSession(
            title=title,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            model=model,
            character_id=character_id,
            messages=[]
        )
            result = await db.insert_one(chat_session.dict())
            chat_session.id = str(result.inserted_id)
            return chat_session 
        except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
        
    
    @staticmethod
    async def append_message_to_chat_session(chat_id: str, role: str, content: MessageContent, tokens_used: Optional[int] = None) -> ChatMessage:
        db = await get_chats_collection()
        chat_session = await db.find_one({"_id": ObjectId(chat_id)})
        if not chat_session:
            ValueError("Chat session not found")
        
        # Create message object
        message = ChatMessage(
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc),
            tokens_used=tokens_used
        )

        chat_session["messages"].append(message.model_dump())
        await db.update_one({"_id": ObjectId(chat_id)}, {"$set": {"messages": chat_session["messages"]}})
        return message
