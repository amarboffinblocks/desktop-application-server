from fastapi import HTTPException
from app.features.tags.schema import TagModel
from app.db.mongo import db
from pymongo.errors import PyMongoError
from typing import Dict, Any


class TagsController:
    @staticmethod
    async def create_tag(tag_data: TagModel) -> Dict[str, Any]:
        try:
            existing = await db.tags.find_one({"name": tag_data.name})
            if existing:
                raise HTTPException(status_code=400, detail="Tag already exists")
            result = await db.tags.insert_one(tag_data.model_dump())
            tag = await db.tags.find_one({"_id": result.inserted_id})
            return tag
        except PyMongoError as e:
            # Log error if needed
            raise HTTPException(status_code=500, detail="Database error")

    @staticmethod
    async def get_all_tags() -> list[dict]:
        try:
            tags_cursor = db.tags.find()
            return [tag async for tag in tags_cursor]
        except PyMongoError as e:
            # Log error if needed
            raise HTTPException(status_code=500, detail="Database error")


