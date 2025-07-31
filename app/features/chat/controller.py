from fastapi import HTTPException
from app.features.chat.schemas import ChatRequest
from app.features.model.manager import ModelManager
from app.features.model.schemas import ModelSelectRequest
from app.features.agents.builder import AiAgentBuilder
from app.features.chat.service import ChatService
from fastapi.responses import StreamingResponse
# Convert your chat_history to role/content format
chat_history = [
    {"role": "user", "content": "Hey Tony, what are you working on right now?"},
    {"role": "assistant", "content": "Just another world-saving invention. Oh, and it also makes great espresso."},
    
    {"role": "user", "content": "Do you ever take a break from saving the world?"},
    {"role": "assistant", "content": "Break? What’s that? My version of a break is upgrading my suit while listening to AC/DC."},
    
    {"role": "user", "content": "Are you afraid without your armor?"},
    {"role": "assistant", "content": "Afraid? No. I’m still Tony Stark. The suit is just… extra shiny confidence."},
    
    {"role": "user", "content": "Who’s your best friend among the Avengers?"},
    {"role": "assistant", "content": "Rhodey, obviously. But don’t tell Cap — he’s too serious for my taste."},
    
    {"role": "user", "content": "How do you deal with stress?"},
    {"role": "assistant", "content": "Whiskey, humor, and building something ridiculously overpowered."},
    
    {"role": "user", "content": "Do you trust AI like J.A.R.V.I.S.?"},
    {"role": "assistant", "content": "I built him. Of course I trust him. Mostly. Until he starts judging my playlist choices."}
]






# async def chat_with_model_controller(request: ChatRequest):
#     manager = ModelManager()
#     character = None
#     if False:
#         character = await ChatService.get_character_by_id(request.character_id)
#     try:
#         if character:
#             # Build persona prompt
#             messages = AiAgentBuilder.build_persona_prompt(character, chat_history, request.prompt)
#         else:
#             # Fallback to default prompt if no character provided
#             messages = AiAgentBuilder.build_default_prompt(chat_history, request.prompt)

#         result = manager.generate_response(
#             prompt=messages,  # now messages is proper format
#             max_tokens=request.max_tokens,
#             temperature=request.temperature,
#         )
        
#         return {
#             "response": result.get("response", "No response generated."),
#             "model": result.get("model", "local-model"),
#             "tokens_used": result.get("usage", {}).get("total_tokens", 0)
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

async def chat_with_model_controller(request: ChatRequest):
    manager = ModelManager()
    character = None

    try:
        # Future: Character fetch logic
        if False:
            character = await ChatService.get_character_by_id(request.character_id)

        # Build prompt
        if character:
            messages = AiAgentBuilder.build_persona_prompt(character, chat_history, request.prompt)
        else:
            messages = AiAgentBuilder.build_default_prompt(chat_history, request.prompt)

        # SSE wrapper for streaming tokens
        def sse_wrapper():
            for token in manager.generate_response(
                prompt=messages,
                max_tokens=request.max_tokens or 200,
                temperature=request.temperature or 0.7,
                top_p=request.top_p or 0.9,
                stream=True  # Always streaming
            ):
                print(token)
                yield f"data: {token}\n\n"
            yield "data: [END]\n\n"

        return StreamingResponse(sse_wrapper(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))