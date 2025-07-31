from fastapi import APIRouter, HTTPException
from app.features.tags.controller import TagsController
from app.features.tags.schema import TagModel
from typing import List

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/create", response_model=dict)
async def create_tag(tag: TagModel):
    return await TagsController.create_tag(tag)

@router.get("/", response_model=List[dict])
async def get_all_tags():
    return await TagsController.get_all_tags() 