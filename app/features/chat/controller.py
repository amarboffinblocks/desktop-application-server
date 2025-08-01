from fastapi import HTTPException

from app.features.model.manager import ModelManager
from app.features.model.schemas import ModelSelectRequest
from app.features.agents.builder import AiAgentBuilder
from app.features.chat.service import ChatService
from fastapi.responses import StreamingResponse
from typing import Optional, List
from app.features.chat.schemas import ChatSession, ChatMessage, MessageContent, ChatRequest
import asyncio


async def create_chat_session_controller(user_id: str, title: str, model: Optional[str] = None, character_id: Optional[str] = None):
    try:
        return  await ChatService.create_chat_session(user_id, title, model, character_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



async def chat_with_model_controller(request: ChatRequest):
    manager = ModelManager()
    try:
        # 1. Save user message
        user_content = MessageContent(type="text", value=request.prompt)
        await ChatService.append_message_to_chat_session(
            request.chat_id, "user", user_content
        )

        # 2. Build prompt
        character = None
        if request.character_id:
            character = await ChatService.get_character_by_id(request.character_id)
            messages = AiAgentBuilder.build_persona_prompt(character, [], request.prompt)
        else:
            messages = AiAgentBuilder.build_default_prompt([], request.prompt)

        # 3. Create async generator
        async def generate_tokens():
            # Convert sync generator to async
            for token in manager.generate_response(
                prompt=messages,
                max_tokens=request.max_tokens or 200,
                temperature=request.temperature or 0.7,
                top_p=request.top_p or 0.9,
                stream=True,
            ):
                yield token
                # Small sleep to prevent blocking the event loop
                await asyncio.sleep(0.001)

        # 4. SSE wrapper
        async def sse_wrapper():
            collected_text = ""
            async for token in generate_tokens():
                collected_text += token
                yield f"data: {token}\n\n"
            
            # Save assistant message
            await ChatService.append_message_to_chat_session(
                request.chat_id, 
                "assistant", 
                MessageContent(type="text", value=collected_text)
            )
            yield "data: [END]\n\n"

        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/event-stream',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }

        return StreamingResponse(
            sse_wrapper(),
            headers=headers,
            media_type="text/event-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))