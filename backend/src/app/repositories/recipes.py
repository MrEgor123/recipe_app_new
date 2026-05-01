from typing import List, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite
from app.models.recipe import Recipe
from app.models.recipe_step import RecipeStep
from app.models.recipe_tag import RecipeTag
from app.models.shopping_cart import ShoppingCartItem
from app.schemas.recipes import RecipeCreate, RecipeUpdate
from app.models.ingredient import Ingredient
from app.models.recipe_ingredient import RecipeIngredient
from app.utils.moderation import moderate_recipe_full


class RecipeRepository:
    async def get(self, session: AsyncSession, recipe_id: int) -> Recipe | None:
        result = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
        return result.scalars().first()

    async def create(self, session: AsyncSession, payload: RecipeCreate, *, author_id: int) -> Recipe:
        status = await moderate_recipe_full(payload.title, payload.description)

        recipe = Recipe(
            author_id=author_id,
            title=payload.title,
            description=payload.description,
            cooking_time_minutes=payload.cooking_time_minutes,
            base_servings=payload.base_servings,
            moderation_status=status,
            is_published=status == "approved",
        )

        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)

        await self._replace_tags(session, recipe.id, payload.tag_ids)
        await self._replace_ingredients(session, recipe.id, payload.ingredients)
        await self._replace_steps(session, recipe.id, payload.steps)

        return recipe

    async def update(self, session: AsyncSession, recipe: Recipe, payload: RecipeUpdate) -> Recipe:
        data = payload.model_dump(exclude_unset=True)

        if "title" in data:
            recipe.title = data["title"]
        if "description" in data:
            recipe.description = data["description"]
        if "cooking_time_minutes" in data:
            recipe.cooking_time_minutes = data["cooking_time_minutes"]
        if "base_servings" in data:
            recipe.base_servings = data["base_servings"]

        status = await moderate_recipe_full(recipe.title, recipe.description)
        recipe.moderation_status = status
        recipe.is_published = status == "approved"

        await session.commit()
        await session.refresh(recipe)

        if "tag_ids" in data and data["tag_ids"] is not None:
            await self._replace_tags(session, recipe.id, data["tag_ids"])

        if "ingredients" in data and data["ingredients"] is not None:
            await self._replace_ingredients(session, recipe.id, data["ingredients"])

        if "steps" in data and data["steps"] is not None:
            await self._replace_steps(session, recipe.id, data["steps"])

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
        stmt = select(Recipe).where(Recipe.is_published.is_(True))

        if author_id is not None:
            stmt = stmt.where(Recipe.author_id == author_id)

        if tag_ids:
            stmt = (
                stmt.join(RecipeTag, RecipeTag.recipe_id == Recipe.id)
                .where(RecipeTag.tag_id.in_(tag_ids))
                .distinct()
            )

        if is_favorited and user_id is not None:
            stmt = (
                stmt.join(Favorite, Favorite.recipe_id == Recipe.id)
                .where(Favorite.user_id == user_id)
                .distinct()
            )

        if is_in_shopping_cart and user_id is not None:
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
        stmt = select(func.count(func.distinct(Recipe.id))).select_from(Recipe).where(
            Recipe.is_published.is_(True)
        )

        if tag_ids:
            stmt = stmt.join(RecipeTag, RecipeTag.recipe_id == Recipe.id).where(
                RecipeTag.tag_id.in_(tag_ids)
            )

        if is_favorited and user_id is not None:
            stmt = stmt.join(Favorite, Favorite.recipe_id == Recipe.id).where(
                Favorite.user_id == user_id
            )

        if is_in_shopping_cart and user_id is not None:
            stmt = stmt.join(ShoppingCartItem, ShoppingCartItem.recipe_id == Recipe.id).where(
                ShoppingCartItem.user_id == user_id
            )

        if author_id is not None:
            stmt = stmt.where(Recipe.author_id == author_id)

        result = await session.execute(stmt)
        return int(result.scalar_one())

    async def _replace_tags(self, session: AsyncSession, recipe_id: int, tag_ids: List[int]) -> None:
        await session.execute(delete(RecipeTag).where(RecipeTag.recipe_id == recipe_id))
        if tag_ids:
            session.add_all([RecipeTag(recipe_id=recipe_id, tag_id=tid) for tid in tag_ids])
        await session.commit()

    async def _replace_ingredients(self, session: AsyncSession, recipe_id: int, ingredients_in) -> None:
        await session.execute(delete(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id))

        if ingredients_in:
            normalized = []
            for item in ingredients_in:
                if isinstance(item, dict):
                    ingredient_id = int(item.get("ingredient_id") or item.get("id"))
                    amount = float(item.get("amount"))
                else:
                    ingredient_id = int(item.ingredient_id)
                    amount = float(item.amount)
                normalized.append((ingredient_id, amount))

            session.add_all(
                [
                    RecipeIngredient(
                        recipe_id=recipe_id,
                        ingredient_id=ingredient_id,
                        amount=amount,
                    )
                    for ingredient_id, amount in normalized
                ]
            )

        await session.commit()

    async def _replace_steps(self, session: AsyncSession, recipe_id: int, steps_in) -> None:
        await session.execute(delete(RecipeStep).where(RecipeStep.recipe_id == recipe_id))

        if steps_in:
            normalized = []
            for item in steps_in:
                if isinstance(item, dict):
                    position = int(item["position"])
                    text = str(item["text"])
                    duration_sec = item.get("duration_sec")
                    duration_sec = int(duration_sec) if duration_sec is not None else None
                else:
                    position = int(item.position)
                    text = str(item.text)
                    duration_sec = int(item.duration_sec) if item.duration_sec is not None else None

                normalized.append((position, text, duration_sec))

            normalized.sort(key=lambda x: x[0])

            session.add_all(
                [
                    RecipeStep(
                        recipe_id=recipe_id,
                        position=pos,
                        text=text,
                        duration_sec=dur,
                    )
                    for pos, text, dur in normalized
                ]
            )

        await session.commit()

    async def get_recipe_tags(self, session: AsyncSession, recipe_id: int):
        from app.models.tag import Tag

        stmt = (
            select(Tag)
            .join(RecipeTag, RecipeTag.tag_id == Tag.id)
            .where(RecipeTag.recipe_id == recipe_id)
            .order_by(Tag.id.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_recipe_ingredients(self, session: AsyncSession, recipe_id: int):
        stmt = (
            select(
                Ingredient.id,
                Ingredient.name,
                Ingredient.unit,
                RecipeIngredient.amount,
                Ingredient.calories_per_100g,
                Ingredient.protein_per_100g,
                Ingredient.fat_per_100g,
                Ingredient.carbs_per_100g,
            )
            .join(RecipeIngredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .where(RecipeIngredient.recipe_id == recipe_id)
            .order_by(Ingredient.name.asc())
        )
        result = await session.execute(stmt)
        return list(result.all())

    async def get_recipe_steps(self, session: AsyncSession, recipe_id: int) -> List[RecipeStep]:
        stmt = (
            select(RecipeStep)
            .where(RecipeStep.recipe_id == recipe_id)
            .order_by(RecipeStep.position.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())