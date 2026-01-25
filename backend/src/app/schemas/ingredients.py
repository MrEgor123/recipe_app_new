from pydantic import BaseModel, Field


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    unit: str = Field(min_length=1, max_length=32)


class IngredientUpdate(BaseModel):
    name: str | None = Field(min_length=1, max_length=120)
    unit: str | None = Field(min_length=1, max_length=32)


class IngredientRead(BaseModel):
    id: int
    name: str
    unit: str
