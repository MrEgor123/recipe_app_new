from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite
from app.models.recipe import Recipe
from app.models.recipe_tag import RecipeTag
from app.models.shopping_cart import ShoppingCartItem
from app.schemas.recipes import RecipeCreate, RecipeUpdate


class RecipeRepository:
    async def get(self, session: AsyncSession, recipe_id: int) -> Recipe | None:
        result = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
        return result.scalars().first()

    async def create(self, session: AsyncSession, payload: RecipeCreate, *, author_id: int) -> Recipe:
        recipe = Recipe(
            author_id=author_id,
            title=payload.title,
            description=payload.description,
            cooking_time_minutes=payload.cooking_time_minutes,
        )
        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)

        await self._replace_tags(session, recipe.id, payload.tag_ids)
        await self._replace_ingredients(session, recipe.id, payload.ingredients)
        return recipe

    async def update(self, session: AsyncSession, recipe: Recipe, payload: RecipeUpdate) -> Recipe:
        data = payload.model_dump(exclude_unset=True)

        if "title" in data:
            recipe.title = data["title"]
        if "description" in data:
            recipe.description = data["description"]
        if "cooking_time_minutes" in data:
            recipe.cooking_time_minutes = data["cooking_time_minutes"]

        await session.commit()
        await session.refresh(recipe)

        if "tag_ids" in data:
            await self._replace_tags(session, recipe.id, data["tag_ids"])
        if "ingredients" in data:
            await self._replace_ingredients(session, recipe.id, data["ingredients"])

        return recipe

    async def delete(self, session: AsyncSession, recipe: Recipe) -> None:
        await session.delete(recipe)
        await session.commit()

    async def list_filtered(
        self,
        session: AsyncSession,
        *,
        author_id: Optional[int],
        tag_ids: Optional[List[int]],
        limit: int,
        offset: int,
        user_id: Optional[int],
        is_favorited: bool,
        is_in_shopping_cart: bool,
    ) -> List[Recipe]:
        stmt = select(Recipe)

        if author_id is not None:
            stmt = stmt.where(Recipe.author_id == author_id)

        if tag_ids:
            stmt = (
                stmt.join(RecipeTag, RecipeTag.recipe_id == Recipe.id)
                .where(RecipeTag.tag_id.in_(tag_ids))
                .distinct()
            )

        if is_favorited:
            stmt = (
                stmt.join(Favorite, Favorite.recipe_id == Recipe.id)
                .where(Favorite.user_id == user_id)
                .distinct()
            )

        if is_in_shopping_cart:
            stmt = (
                stmt.join(ShoppingCartItem, ShoppingCartItem.recipe_id == Recipe.id)
                .where(ShoppingCartItem.user_id == user_id)
                .distinct()
            )

        stmt = stmt.order_by(Recipe.id.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        session: AsyncSession,
        *,
        author_id: Optional[int],
        tag_ids: Optional[List[int]],
        user_id: Optional[int],
        is_favorited: bool,
        is_in_shopping_cart: bool,
    ) -> int:
        stmt = select(func.count(func.distinct(Recipe.id))).select_from(Recipe)

        if tag_ids:
            stmt = stmt.join(RecipeTag, RecipeTag.recipe_id == Recipe.id).where(RecipeTag.tag_id.in_(tag_ids))

        if is_favorited:
            stmt = stmt.join(Favorite, Favorite.recipe_id == Recipe.id).where(Favorite.user_id == user_id)

        if is_in_shopping_cart:
            stmt = stmt.join(ShoppingCartItem, ShoppingCartItem.recipe_id == Recipe.id).where(
                ShoppingCartItem.user_id == user_id
            )

        if author_id is not None:
            stmt = stmt.where(Recipe.author_id == author_id)

        result = await session.execute(stmt)
        return int(result.scalar_one())

    async def _replace_tags(self, session: AsyncSession, recipe_id: int, tag_ids: List[int]) -> None:
        from sqlalchemy import delete
        from app.models.recipe_tag import RecipeTag

        await session.execute(delete(RecipeTag).where(RecipeTag.recipe_id == recipe_id))
        if tag_ids:
            session.add_all([RecipeTag(recipe_id=recipe_id, tag_id=tid) for tid in tag_ids])
        await session.commit()

    async def _replace_ingredients(self, session: AsyncSession, recipe_id: int, ingredients_in) -> None:
        from sqlalchemy import delete
        from app.models.recipe_ingredient import RecipeIngredient

        await session.execute(delete(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id))
        if ingredients_in:
            session.add_all(
                [
                    RecipeIngredient(
                        recipe_id=recipe_id,
                        ingredient_id=item.ingredient_id,
                        amount=float(item.amount),
                    )
                    for item in ingredients_in
                ]
            )
        await session.commit()

    async def get_recipe_tags(self, session: AsyncSession, recipe_id: int):
        from sqlalchemy import select
        from app.models.tag import Tag
        from app.models.recipe_tag import RecipeTag

        stmt = (
            select(Tag)
            .join(RecipeTag, RecipeTag.tag_id == Tag.id)
            .where(RecipeTag.recipe_id == recipe_id)
            .order_by(Tag.id.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_recipe_ingredients(self, session: AsyncSession, recipe_id: int):
        from sqlalchemy import select
        from app.models.ingredient import Ingredient
        from app.models.recipe_ingredient import RecipeIngredient

        stmt = (
            select(Ingredient.id, Ingredient.name, Ingredient.unit, RecipeIngredient.amount)
            .join(RecipeIngredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .where(RecipeIngredient.recipe_id == recipe_id)
            .order_by(Ingredient.name.asc())
        )
        result = await session.execute(stmt)
        return list(result.all())
