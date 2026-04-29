from datetime import datetime

from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CollectionOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    recipes_count: int = 0
    created_at: datetime


class CollectionRecipeIdsOut(BaseModel):
    collection_ids: list[int]


class RecipeCollectionsUpdate(BaseModel):
    collection_ids: list[int]


class CollectionRecipeCardOut(BaseModel):
    id: int
    title: str
    image: str | None = None
    cooking_time_minutes: int
    rating_avg: float = 0
    rating_count: int = 0