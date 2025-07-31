from pydantic import BaseModel, Field
from datetime import datetime, timezone

class TagModel(BaseModel):
    name: str                                  # e.g., "marvel", "superhero"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
