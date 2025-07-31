from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

class FavouriteModel(BaseModel):
    user_id: str                                               # Kis user ne favourite kiya
    character_id: str                                          # Kis character ko favourite kiya
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
