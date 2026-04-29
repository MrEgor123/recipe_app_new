from datetime import datetime

from pydantic import BaseModel, Field


class ProfileStatsOut(BaseModel):
    recipes_count: int
    followers_count: int
    following_count: int
    comments_count: int
    collections_count: int
    total_recipe_likes: int


class ProfileRecipeOut(BaseModel):
    id: int
    title: str
    image: str | None = None
    cooking_time_minutes: int
    rating_avg: float = 0
    rating_count: int = 0


class UserProfileOut(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    avatar: str | None = None
    cover_image: str | None = None
    status: str | None = None
    bio: str | None = None
    created_at: datetime
    is_subscribed: bool
    is_owner: bool
    stats: ProfileStatsOut
    recipes: list[ProfileRecipeOut] = []


class UserProfileUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=2000)
    cover_image: str | None = None