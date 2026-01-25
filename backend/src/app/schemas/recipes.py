from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, condecimal


class RecipeIngredientIn(BaseModel):
    ingredient_id: int
    amount: condecimal(gt=0, max_digits=10, decimal_places=2)


class RecipeIngredientOut(BaseModel):
    id: int
    name: str
    unit: str
    amount: float


class RecipeCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=1, max_length=5000)
    cooking_time_minutes: PositiveInt
    tag_ids: List[int] = Field(default_factory=list)
    ingredients: List[RecipeIngredientIn] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, min_length=1, max_length=5000)
    cooking_time_minutes: Optional[PositiveInt] = None
    tag_ids: Optional[List[int]] = None
    ingredients: Optional[List[RecipeIngredientIn]] = None


class RecipeTagOut(BaseModel):
    id: int
    name: str
    slug: str
    color: str


class RecipeRead(BaseModel):
    id: int
    title: str
    description: str
    cooking_time_minutes: int
    tags: List[RecipeTagOut]
    ingredients: List[RecipeIngredientOut]
