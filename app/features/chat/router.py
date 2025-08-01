from fastapi import APIRouter, HTTPException,Depends
from app.features.chat.controller import chat_with_model_controller, create_chat_session_controller
from app.features.chat.schemas import ChatRequest, ChatSession
from fastapi.responses import StreamingResponse
from fastapi import Query
from typing import Optional
from app.common.dependencies import authenticated_user
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/create")
async def create_chat_session_endpoint(
    title: str,
    model: Optional[str] = None,
    character_id: Optional[str] = None,
    # current_user: dict = Depends(authenticated_user)
):
        user_id = "687753a9771e91870b596bb2"
        chat_session = await create_chat_session_controller(user_id, title, model, character_id)
        return chat_session
    
    

@router.get("/stream",response_class=StreamingResponse)
async def chat_stream_endpoint(
    chat_id: str,
    prompt: str ,
    stream: bool = True,
    max_tokens: int = 200,
    temperature: float = 0.7,
    top_p: float = 0.9,
    # current_user: dict = Depends(authenticated_user)
):  
    request = ChatRequest(
        chat_id=chat_id,
        prompt=prompt,
        stream=stream,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p
    )

    return await chat_with_model_controller(request)