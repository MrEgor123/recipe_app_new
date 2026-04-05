import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.recipe import Recipe
from app.utils.images import save_base64_image


async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Recipe))
        recipes = result.scalars().all()

        updated = 0

        for recipe in recipes:
            if recipe.image and recipe.image.startswith("data:image/"):
                try:
                    new_path = save_base64_image(recipe.image, subdir="recipes")
                    recipe.image = new_path
                    updated += 1
                    print(f"converted recipe {recipe.id} -> {new_path}")
                except Exception as e:
                    print(f"failed recipe {recipe.id}: {e}")

        await session.commit()
        print(f"done; updated: {updated}")


if __name__ == "__main__":
    asyncio.run(main())