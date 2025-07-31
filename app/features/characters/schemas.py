from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
class VoteCounts(BaseModel):
    thumbs_up_count: int = 0
    thumbs_down_count: int = 0

class FavouriteCounts(BaseModel):
    favourites_count: int = 0

class CharacterExtensions(BaseModel):
    rating: Literal["SFW", "NSFW"] = "SFW"
    avatar: Optional[str] = None
    background_image: Optional[str] = None
    gallery: Optional[List[str]] = None
    visibility: Literal["Public", "Private"] = "Private"
    publish_mode: Literal["Author", "Anonymous"] = "Author"
    votes: VoteCounts = VoteCounts()
    favourites: FavouriteCounts = FavouriteCounts()

class CharacterModel(BaseModel):
    name: str
    description: str
    personality: str
    scenario: str
    first_mes: str
    mes_example: str
    creator_notes: Optional[str] = None
    system_prompt: Optional[str] = None
    alternate_greetings: List[str] = []
    tags: List[str] = []
    creator: Optional[str] = None
    character_version: Optional[str] = "2.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    extensions: CharacterExtensions = CharacterExtensions()
    author_notes: Optional[str] = None

    class Config:
        orm_mode = True
