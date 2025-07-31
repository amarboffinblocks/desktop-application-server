from fastapi import APIRouter, HTTPException
from app.features.chat.controller import chat_with_model_controller
from app.features.chat.schemas import ChatRequest
from fastapi import Query
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat_endpoint(request: ChatRequest):
    result = await chat_with_model_controller(request)
    return result



@router.get("/stream")
async def chat_stream_endpoint(
    prompt: str = Query(..., description="User message"),
    stream: bool = Query(True, description="Enable streaming"),
    max_tokens: int = Query(200),
    temperature: float = Query(0.7),
    top_p: float = Query(0.9)
):
    request = ChatRequest(
        prompt=prompt,
        stream=stream,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p
    )

    return await chat_with_model_controller(request)