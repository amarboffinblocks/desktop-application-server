from pydantic import BaseModel
from typing import Optional
 
class ChatRequest(BaseModel):
    prompt: str = "Who won the world series in 2020?"
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 200
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9