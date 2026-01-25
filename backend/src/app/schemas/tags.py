from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    slug: str = Field(min_length=2, max_length=50)
    color: str = Field(pattern="^#([A-Fa-f0-9]{6})$")


class TagUpdate(BaseModel):
    name: str | None = Field(min_length=2, max_length=50)
    slug: str | None = Field(min_length=2, max_length=50)
    color: str | None = Field(pattern="^#([A-Fa-f0-9]{6})$")


class TagRead(TagCreate):
    id: int
    name: str
    slug: str
    color: str
