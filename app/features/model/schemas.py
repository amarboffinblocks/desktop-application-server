from pydantic import BaseModel
from typing import Optional

class ModelSelectRequest(BaseModel):
    model_name: str = "mistral-7b-instruct-v0.2.Q8_0.gguf"
    model_type: Optional[str]  = "gguf"


class ModelStatusResponse(BaseModel):
    loaded: bool
    loading: bool
    progress: int
    current_model: Optional[str]
    model_type: Optional[str]
    load_time: float


