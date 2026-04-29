from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.models.collection_recipe import CollectionRecipe
from app.models.recipe import Recipe


class CollectionRepository:
    async def create_collection(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        name: str,
        description: str | None = None,
    ) -> Collection:
        collection = Collection(
            user_id=user_id,
            name=name.strip(),
            description=description.strip() if description else None,
        )
        session.add(collection)
        await session.commit()
        await session.refresh(collection)
        return collection

    async def get_user_collections(
        self,
        session: AsyncSession,
        *,
        user_id: int,
    ) -> list[tuple[Collection, int]]:
        stmt = (
            select(
                Collection,
                func.count(CollectionRecipe.id).label("recipes_count"),
            )
            .outerjoin(CollectionRecipe, CollectionRecipe.collection_id == Collection.id)
            .where(Collection.user_id == user_id)
            .group_by(Collection.id)
            .order_by(Collection.created_at.desc(), Collection.id.desc())
        )
        result = await session.execute(stmt)
        return list(result.all())

    async def get_collection(
        self,
        session: AsyncSession,
        *,
        collection_id: int,
    ) -> Collection | None:
        result = await session.execute(
            select(Collection).where(Collection.id == collection_id)
        )
        return result.scalars().first()

    async def get_user_collection(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        collection_id: int,
    ) -> Collection | None:
        result = await session.execute(
            select(Collection).where(
                Collection.id == collection_id,
                Collection.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def get_user_collection_with_count(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        collection_id: int,
    ) -> tuple[Collection, int] | None:
        stmt = (
            select(
                Collection,
                func.count(CollectionRecipe.id).label("recipes_count"),
            )
            .outerjoin(CollectionRecipe, CollectionRecipe.collection_id == Collection.id)
            .where(
                Collection.id == collection_id,
                Collection.user_id == user_id,
            )
            .group_by(Collection.id)
        )
        result = await session.execute(stmt)
        row = result.first()
        return row if row else None

    async def update_collection(
        self,
        session: AsyncSession,
        *,
        collection: Collection,
        name: str | None = None,
        description: str | None = None,
    ) -> Collection:
        if name is not None:
            collection.name = name.strip()
        if description is not None:
            collection.description = description.strip() if description else None

        await session.commit()
        await session.refresh(collection)
        return collection

    async def delete_collection(
        self,
        session: AsyncSession,
        *,
        collection: Collection,
    ) -> None:
        await session.delete(collection)
        await session.commit()

    async def get_collection_recipes(
        self,
        session: AsyncSession,
        *,
        collection_id: int,
    ) -> list[Recipe]:
        stmt = (
            select(Recipe)
            .join(CollectionRecipe, CollectionRecipe.recipe_id == Recipe.id)
            .where(CollectionRecipe.collection_id == collection_id)
            .order_by(CollectionRecipe.created_at.desc(), Recipe.id.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def add_recipe_to_collection(
        self,
        session: AsyncSession,
        *,
        collection_id: int,
        recipe_id: int,
    ) -> CollectionRecipe:
        link = CollectionRecipe(
            collection_id=collection_id,
            recipe_id=recipe_id,
        )
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

    async def remove_recipe_from_collection(
        self,
        session: AsyncSession,
        *,
        collection_id: int,
        recipe_id: int,
    ) -> None:
        await session.execute(
            delete(CollectionRecipe).where(
                CollectionRecipe.collection_id == collection_id,
                CollectionRecipe.recipe_id == recipe_id,
            )
        )
        await session.commit()

    async def collection_has_recipe(
        self,
        session: AsyncSession,
        *,
        collection_id: int,
        recipe_id: int,
    ) -> bool:
        result = await session.execute(
            select(CollectionRecipe.id).where(
                CollectionRecipe.collection_id == collection_id,
                CollectionRecipe.recipe_id == recipe_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_recipe_collection_ids_for_user(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        recipe_id: int,
    ) -> list[int]:
        stmt = (
            select(Collection.id)
            .join(CollectionRecipe, CollectionRecipe.collection_id == Collection.id)
            .where(
                Collection.user_id == user_id,
                CollectionRecipe.recipe_id == recipe_id,
            )
            .order_by(Collection.id.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def replace_recipe_collections_for_user(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        recipe_id: int,
        collection_ids: list[int],
    ) -> list[int]:
        allowed_stmt = select(Collection.id).where(
            Collection.user_id == user_id,
            Collection.id.in_(collection_ids) if collection_ids else False,
        )
        allowed_result = await session.execute(allowed_stmt)
        allowed_ids = list(allowed_result.scalars().all())

        user_collections_stmt = select(Collection.id).where(Collection.user_id == user_id)
        user_collections_result = await session.execute(user_collections_stmt)
        user_collection_ids = list(user_collections_result.scalars().all())

        if user_collection_ids:
            await session.execute(
                delete(CollectionRecipe).where(
                    CollectionRecipe.recipe_id == recipe_id,
                    CollectionRecipe.collection_id.in_(user_collection_ids),
                )
            )

        if allowed_ids:
            session.add_all(
                [
                    CollectionRecipe(collection_id=collection_id, recipe_id=recipe_id)
                    for collection_id in allowed_ids
                ]
            )

        await session.commit()
        return allowed_ids