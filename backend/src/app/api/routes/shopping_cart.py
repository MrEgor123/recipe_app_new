from io import BytesIO

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from reportlab.pdfgen import canvas

from app.core.db import get_db_session
from app.core.deps import get_current_user
from app.core.pagination import calc_offset, calc_pages, clamp_size
from app.core.errors import not_found
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.shopping_cart import ShoppingCartItem
from app.repositories.recipes import RecipeRepository
from app.repositories.shopping_cart import ShoppingCartRepository
from app.schemas.recipes import RecipeIngredientOut, RecipeRead, RecipeTagOut
from app.schemas.recipes_list import RecipeListResponse

router = APIRouter(tags=["shopping-cart"])
recipe_repo = RecipeRepository()
shopping_cart_repo = ShoppingCartRepository()


async def _to_read(session: AsyncSession, recipe: Recipe) -> RecipeRead:
    tags = await recipe_repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await recipe_repo.get_recipe_ingredients(session, recipe.id)
    return RecipeRead(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        cooking_time_minutes=recipe.cooking_time_minutes,
        tags=[RecipeTagOut(id=t.id, name=t.name, slug=t.slug, color=t.color) for t in tags],
        ingredients=[
            RecipeIngredientOut(id=row.id, name=row.name, unit=row.unit, amount=float(row.amount))
            for row in ingredients_rows
        ],
    )


@router.get("/shopping-cart/count")
async def get_cart_count(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    count = await shopping_cart_repo.get_count(session, user_id=user.id)
    return {"count": count}


@router.get("/shopping-cart", response_model=RecipeListResponse)
async def get_cart(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
):
    size = clamp_size(size)
    offset = calc_offset(page, size)

    total = await shopping_cart_repo.get_count(session, user_id=user.id)
    pages = calc_pages(total, size)

    stmt = (
        select(Recipe)
        .join(ShoppingCartItem, ShoppingCartItem.recipe_id == Recipe.id)
        .where(ShoppingCartItem.user_id == user.id)
        .order_by(Recipe.id.desc())
        .limit(size)
        .offset(offset)
    )
    recipes = (await session.execute(stmt)).scalars().all()
    items = [await _to_read(session, r) for r in recipes]

    return RecipeListResponse(items=items, page=page, size=size, total=total, pages=pages)


@router.post("/recipes/{recipe_id}/shopping-cart", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    recipe = await recipe_repo.get(session, recipe_id)
    if recipe is None:
        raise not_found("recipe", recipe_id)

    exists = await shopping_cart_repo.is_in_cart(
        session,
        user_id=user.id,
        recipe_id=recipe_id,
    )
    if exists:
        return {"status": "already_in_cart"}

    await shopping_cart_repo.add(
        session,
        user_id=user.id,
        recipe_id=recipe_id,
    )
    return {"status": "added"}


@router.delete("/recipes/{recipe_id}/shopping-cart", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    await shopping_cart_repo.remove(
        session,
        user_id=user.id,
        recipe_id=recipe_id,
    )
    return None


@router.get("/shopping-cart/ingredients")
async def aggregated_ingredients(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    recipe_ids = await shopping_cart_repo.list_recipe_ids(session, user_id=user.id)
    if not recipe_ids:
        return []

    stmt = (
        select(
            Ingredient.id.label("id"),
            Ingredient.name.label("name"),
            Ingredient.unit.label("unit"),
            func.sum(RecipeIngredient.amount).label("amount"),
        )
        .join(RecipeIngredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .where(RecipeIngredient.recipe_id.in_(recipe_ids))
        .group_by(Ingredient.id, Ingredient.name, Ingredient.unit)
        .order_by(Ingredient.name.asc())
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "unit": r.unit,
            "amount": float(r.amount),
        }
        for r in rows
    ]


@router.get("/shopping-cart/export.txt")
async def export_shopping_list_txt(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    items = await aggregated_ingredients(session=session, user=user)
    lines = [f"{it['name']} - {it['amount']} {it['unit']}" for it in items]
    content = "\n".join(lines) + "\n"
    return StreamingResponse(
        BytesIO(content.encode("utf-8")),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="shopping_list.txt"'},
    )


@router.get("/shopping-cart/export.pdf")
async def export_shopping_list_pdf(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    items = await aggregated_ingredients(session=session, user=user)

    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setTitle("Shopping List")

    y = 800
    c.setFont("Helvetica", 14)
    c.drawString(50, y, "Shopping list")
    y -= 30

    c.setFont("Helvetica", 12)
    for it in items:
        line = f"{it['name']} - {it['amount']} {it['unit']}"
        c.drawString(50, y, line)
        y -= 18
        if y < 50:
            c.showPage()
            y = 800
            c.setFont("Helvetica", 12)

    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="shopping_list.pdf"'},
    )