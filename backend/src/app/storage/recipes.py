import asyncio
from typing import List, Dict
from app.schemas.recipes import RecipeCreate, RecipeRead, RecipeUpdate


class RecipeStore:
    def __init__(self) -> None:
        self._data: Dict[int, RecipeRead] = {}
        self._seq: int = 0

    async def list(self) -> List[RecipeRead]:
        await asyncio.sleep(0)
        return list(self._data.values())
    
    async def get(self, recipe_id: int) -> RecipeRead | None:
        await asyncio.sleep(0)
        return self._data.get(recipe_id)
    
    async def create(self, payload: RecipeCreate) -> RecipeRead:
        await asyncio.sleep(0)
        self._seq += 1
        recipe = RecipeRead(
            id=self._seq,
            title=payload.title,
            description=payload.description,
            cooking_time_minutes=payload.cooking_time_minutes,
            tags=payload.tags,
            ingredients=payload.ingredients,
        )
        self._data[recipe.id] = recipe
        return recipe
    
    async def update(self, recipe_id: int, payload: RecipeUpdate) -> RecipeRead | None:
        await asyncio.sleep(0)
        existing = self._data.get(recipe_id)
        if existing is None:
            return None

        updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
        self._data[recipe_id] = updated
        return updated
    
    async def delete(self, recipe_id: int) -> bool:
        await asyncio.sleep(0)
        return self._data.pop(recipe_id, None) is not None


store = RecipeStore()
