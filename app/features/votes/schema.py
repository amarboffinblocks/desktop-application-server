from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Literal

class VoteModel(BaseModel):
    user_id: str                                        
    character_id: str                                        
    vote_type: Literal[1, -1]                                
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
