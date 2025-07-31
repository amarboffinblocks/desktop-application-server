from fastapi import APIRouter
from app.features.auth.router import router as auth_router
from app.features.model.router import router as model_router
from app.features.chat.router import router as chat_router
from app.features.tags.router import router as tags_router
from app.features.characters.router import router as character_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(model_router)
api_router.include_router(chat_router)
api_router.include_router(tags_router)
api_router.include_router(character_router)