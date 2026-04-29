from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentAuthorOut(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    avatar: str | None = None


class CommentOut(BaseModel):
    id: int
    text: str
    created_at: datetime
    parent_id: int | None = None
    likes_count: int = 0
    is_liked: bool = False
    author: CommentAuthorOut
    replies: list["CommentOut"] = []


class ProfileCommentRecipeOut(BaseModel):
    id: int
    title: str | None = None
    image: str | None = None


class ProfileCommentOut(BaseModel):
    id: int
    text: str
    created_at: datetime
    parent_id: int | None = None
    likes_count: int = 0
    is_liked: bool = False
    author: CommentAuthorOut
    recipe: ProfileCommentRecipeOut


CommentOut.model_rebuild()