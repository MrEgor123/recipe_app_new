from io import BytesIO
from math import ceil
from urllib.parse import quote_plus

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
from app.models.market_product import MarketProduct
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


MARKETS = [
    {
        "id": "pyaterochka",
        "name": "Пятёрочка",
        "description": "поиск продуктов в Пятёрочке",
        "home_url": "https://5ka.ru/",
        "search_url": "https://yandex.ru/search/?text=site%3A5ka.ru+",
    },
    {
        "id": "magnit",
        "name": "Магнит",
        "description": "поиск продуктов в Магните",
        "home_url": "https://magnit.ru/",
        "search_url": "https://yandex.ru/search/?text=site%3Amagnit.ru+",
    },
    {
        "id": "yandex_eda",
        "name": "Яндекс Еда",
        "description": "поиск продуктов в Яндекс Еде",
        "home_url": "https://eda.yandex.ru/",
        "search_url": "https://yandex.ru/search/?text=site%3Aeda.yandex.ru+",
    },
    {
        "id": "samokat",
        "name": "Самокат",
        "description": "поиск продуктов в Самокате",
        "home_url": "https://samokat.ru/",
        "search_url": "https://yandex.ru/search/?text=site%3Asamokat.ru+",
    },
]


async def _to_read(session: AsyncSession, recipe: Recipe) -> RecipeRead:
    tags = await recipe_repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await recipe_repo.get_recipe_ingredients(session, recipe.id)

    return RecipeRead(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        cooking_time_minutes=recipe.cooking_time_minutes,
        tags=[
            RecipeTagOut(
                id=tag.id,
                name=tag.name,
                slug=tag.slug,
                color=tag.color,
            )
            for tag in tags
        ],
        ingredients=[
            RecipeIngredientOut(
                id=row.id,
                name=row.name,
                unit=row.unit,
                amount=float(row.amount),
            )
            for row in ingredients_rows
        ],
    )


def _format_amount(value: float) -> str:
    value = float(value)

    if value.is_integer():
        return str(int(value))

    return str(round(value, 2)).replace(".", ",")


def _format_price(value: float | None) -> str | None:
    if value is None:
        return None

    value = float(value)

    if value.is_integer():
        return str(int(value))

    return str(round(value, 2)).replace(".", ",")


def _build_market_links(name: str) -> dict:
    query = quote_plus(name)

    return {
        market["id"]: f"{market['search_url']}{query}"
        for market in MARKETS
    }


def _calc_product_estimate(amount: float, product: MarketProduct) -> dict:
    package_amount = float(product.package_amount)
    price = float(product.price)

    if package_amount <= 0:
        packages_count = 1
    else:
        packages_count = max(1, ceil(float(amount) / package_amount))

    estimated_price = packages_count * price

    return {
        "id": product.id,
        "market_id": product.market_id,
        "product_name": product.product_name,
        "product_url": product.product_url,
        "package_amount": package_amount,
        "package_amount_text": _format_amount(package_amount),
        "package_unit": product.package_unit,
        "price": price,
        "price_text": _format_price(price),
        "packages_count": packages_count,
        "estimated_price": estimated_price,
        "estimated_price_text": _format_price(estimated_price),
    }


async def _get_market_products_map(
    session: AsyncSession,
    ingredient_ids: list[int],
) -> dict[int, dict[str, dict]]:
    if not ingredient_ids:
        return {}

    stmt = (
        select(MarketProduct)
        .where(
            MarketProduct.ingredient_id.in_(ingredient_ids),
            MarketProduct.is_active.is_(True),
        )
        .order_by(MarketProduct.ingredient_id.asc(), MarketProduct.price.asc())
    )

    products = (await session.execute(stmt)).scalars().all()
    products_map: dict[int, dict[str, dict]] = {}

    for product in products:
        ingredient_products = products_map.setdefault(product.ingredient_id, {})

        if product.market_id not in ingredient_products:
            ingredient_products[product.market_id] = product

    return products_map


def _build_summary(
    ingredients: list[dict],
    products_map: dict[int, dict[str, MarketProduct]],
) -> dict:
    summary = {}

    for market in MARKETS:
        market_id = market["id"]
        estimated_total = 0
        priced_count = 0
        missing_count = 0

        for item in ingredients:
            product = products_map.get(item["id"], {}).get(market_id)

            if product is None:
                missing_count += 1
                continue

            estimate = _calc_product_estimate(item["amount"], product)
            estimated_total += estimate["estimated_price"]
            priced_count += 1

        summary[market_id] = {
            "market_id": market_id,
            "estimated_total": estimated_total,
            "estimated_total_text": _format_price(estimated_total),
            "priced_count": priced_count,
            "missing_count": missing_count,
            "total_count": len(ingredients),
        }

    return summary


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
    items = [await _to_read(session, recipe) for recipe in recipes]

    return RecipeListResponse(
        items=items,
        page=page,
        size=size,
        total=total,
        pages=pages,
    )


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
        session=session,
        user_id=user.id,
        recipe_id=recipe_id,
    )

    if exists:
        return {"status": "already_in_cart"}

    await shopping_cart_repo.add(
        session=session,
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
        session=session,
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
            "id": row.id,
            "name": row.name,
            "unit": row.unit,
            "amount": float(row.amount),
        }
        for row in rows
    ]


@router.get("/shopping-cart/market")
async def get_market_shopping_cart(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    ingredients = await aggregated_ingredients(session=session, user=user)
    ingredient_ids = [item["id"] for item in ingredients]
    products_map = await _get_market_products_map(
        session=session,
        ingredient_ids=ingredient_ids,
    )

    summary = _build_summary(
        ingredients=ingredients,
        products_map=products_map,
    )

    prepared_ingredients = []

    for item in ingredients:
        market_products = {}

        for market in MARKETS:
            market_id = market["id"]
            product = products_map.get(item["id"], {}).get(market_id)

            if product is None:
                market_products[market_id] = None
                continue

            market_products[market_id] = _calc_product_estimate(
                amount=item["amount"],
                product=product,
            )

        prepared_ingredients.append(
            {
                "id": item["id"],
                "name": item["name"],
                "unit": item["unit"],
                "amount": item["amount"],
                "amount_text": _format_amount(item["amount"]),
                "search_query": item["name"],
                "market_links": _build_market_links(item["name"]),
                "market_products": market_products,
            }
        )

    return {
        "markets": MARKETS,
        "summary": summary,
        "ingredients": prepared_ingredients,
    }


@router.get("/shopping-cart/export.txt")
async def export_shopping_list_txt(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    items = await aggregated_ingredients(session=session, user=user)

    lines = [
        f"{item['name']} - {_format_amount(item['amount'])} {item['unit']}"
        for item in items
    ]

    content = "\n".join(lines) + "\n"

    return StreamingResponse(
        BytesIO(content.encode("utf-8")),
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="shopping_list.txt"',
        },
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

    for item in items:
        line = f"{item['name']} - {_format_amount(item['amount'])} {item['unit']}"
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
        headers={
            "Content-Disposition": 'attachment; filename="shopping_list.pdf"',
        },
    )