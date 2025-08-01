from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4


# ---------- Content ----------
class MessageContent(BaseModel):
    type: Literal["text", "image", "file", "audio", "data"]
    value: Any
    description: Optional[str] = None

    class Config:
        orm_mode = True


# ---------- Message ----------
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: Literal["user", "assistant", "system"]
    content: MessageContent
    created_at: datetime
    tokens_used: Optional[int] = None

    class Config:
        orm_mode = True


# ---------- Chat Session ----------
class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    user_id: str
    created_at: Optional[datetime]
    model: Optional[str] = None
    character_id: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)

    class Config:
        orm_mode = True


# ---------- Chat Request ----------
class ChatRequest(BaseModel):
    prompt: Optional[str] = None
    stream: Optional[bool] = True
    max_tokens: Optional[int] = 200
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    chat_id: str 
    character_id: Optional[str] = None
    attachments: Optional[List[MessageContent]] = None

    class Config:
        orm_mode = True


# ---------- Stream Chunk ----------
class StreamChunk(BaseModel):
    data: str

    class Config:
        orm_mode = True


# ---------- Non-Stream Response ----------
class ChatResponse(BaseModel):
    chat_id: str
    message: ChatMessage
    model: str

    class Config:
        orm_mode = True
