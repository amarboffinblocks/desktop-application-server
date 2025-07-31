from fastapi import APIRouter, HTTPException, status, Depends,UploadFile
from typing import List,Optional
from app.features.characters.schemas import CharacterModel
from app.features.characters import controller

router = APIRouter(prefix="/characters", tags=["Characters"])

@router.post("/create", response_model=CharacterModel)
async def create_character(
    data: CharacterModel,
    avatar: Optional[UploadFile] = None,
    background_image: Optional[UploadFile] = None,
    gallery: Optional[List[UploadFile]] = None):
    return await controller.create_character_controller(data=data,avatar_file=avatar,background_file=background_image,gallery_files=gallery)
