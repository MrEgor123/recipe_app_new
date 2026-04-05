from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, PositiveInt, condecimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user_token, get_optional_user_token
from app.core.security import create_access_token, hash_password, verify_password
from app.models.favorite import Favorite
from app.models.recipe import Recipe
from app.models.shopping_cart import ShoppingCartItem
from app.repositories.ingredients import IngredientRepository
from app.repositories.recipes import RecipeRepository
from app.repositories.short_links import ShortLinkRepository
from app.repositories.subscriptions import SubscriptionRepository
from app.repositories.tags import TagRepository
from app.repositories.users import UserRepository
from app.schemas.recipes import RecipeCreate, RecipeIngredientIn, RecipeStepIn, RecipeUpdate
from app.utils.images import save_base64_image, delete_image_file

router = APIRouter(prefix="/api")

users_repo = UserRepository()
tags_repo = TagRepository()
ingredients_repo = IngredientRepository()
recipes_repo = RecipeRepository()
subs_repo = SubscriptionRepository()
short_links_repo = ShortLinkRepository()

MAX_LIMIT = 1000


class FoodgramIngredientIn(BaseModel):
    id: int
    amount: condecimal(gt=0, max_digits=10, decimal_places=2)


class FoodgramStepIn(BaseModel):
    position: PositiveInt
    text: str = Field(min_length=1, max_length=5000)
    duration_sec: Optional[PositiveInt] = None


class FoodgramRecipeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    text: str = Field(min_length=1, max_length=5000)
    cooking_time: PositiveInt
    tags: List[int] = Field(default_factory=list)
    ingredients: List[FoodgramIngredientIn] = Field(default_factory=list)
    steps: List[FoodgramStepIn] = Field(default_factory=list)
    image: Optional[str] = None


class FoodgramRecipeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    text: Optional[str] = Field(default=None, min_length=1, max_length=5000)
    cooking_time: Optional[PositiveInt] = None
    tags: Optional[List[int]] = None
    ingredients: Optional[List[FoodgramIngredientIn]] = None
    steps: Optional[List[FoodgramStepIn]] = None
    image: Optional[str] = None


class FoodgramTagOut(BaseModel):
    id: int
    name: str
    slug: str
    color: str


class FoodgramIngredientOut(BaseModel):
    id: int
    name: str
    measurement_unit: str
    amount: float


class FoodgramUserOut(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    avatar: Optional[str] = None
    is_subscribed: bool


class FoodgramStepOut(BaseModel):
    position: int
    text: str
    duration_sec: Optional[int] = None


class FoodgramRecipeOut(BaseModel):
    id: int
    name: str
    text: str
    image: Optional[str] = None
    cooking_time: int
    tags: List[FoodgramTagOut]
    ingredients: List[FoodgramIngredientOut]
    author: FoodgramUserOut
    is_favorited: bool
    is_in_shopping_cart: bool
    steps: List[FoodgramStepOut] = Field(default_factory=list)


def clamp_limit(limit: int) -> int:
    return max(1, min(limit, MAX_LIMIT))


def _page_meta(count: int, page: int, limit: int, request: Request) -> dict:
    base = str(request.url).split("?")[0]

    def make_url(p: int) -> str:
        q = dict(request.query_params)
        q["page"] = str(p)
        q["limit"] = str(limit)
        from urllib.parse import urlencode
        return f"{base}?{urlencode(q, doseq=True)}"

    pages = (count + limit - 1) // limit if limit > 0 else 1
    next_url = make_url(page + 1) if page < pages else None
    prev_url = make_url(page - 1) if page > 1 else None
    return {"count": count, "next": next_url, "previous": prev_url}


def _absolute_media_url(request: Request, image_path: str | None) -> str | None:
    if not image_path:
        return None

    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path

    base = str(request.base_url).rstrip("/")
    return f"{base}{image_path}"


async def _user_to_foodgram(session: AsyncSession, user, current_user_id: int | None, request: Request | None = None) -> dict:
    is_subscribed = False
    if current_user_id is not None and user.id != current_user_id:
        is_subscribed = await subs_repo.is_subscribed(session, user_id=current_user_id, author_id=user.id)

    avatar = user.avatar
    if request is not None and avatar and avatar.startswith("/media/"):
        avatar = _absolute_media_url(request, avatar)

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": avatar,
        "is_subscribed": is_subscribed,
    }


async def _recipe_to_foodgram(
    session: AsyncSession,
    recipe: Recipe,
    current_user_id: int | None,
    request: Request,
) -> dict:
    tags = await recipes_repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await recipes_repo.get_recipe_ingredients(session, recipe.id)
    steps = await recipes_repo.get_recipe_steps(session, recipe.id)

    author = await users_repo.get_by_id(session, recipe.author_id)
    if author is None:
        raise HTTPException(status_code=500, detail="Recipe author not found")

    is_favorited = False
    is_in_shopping_cart = False

    if current_user_id is not None:
        fav_stmt = select(Favorite.id).where(Favorite.user_id == current_user_id, Favorite.recipe_id == recipe.id)
        is_favorited = (await session.execute(fav_stmt)).first() is not None

        cart_stmt = select(ShoppingCartItem.id).where(
            ShoppingCartItem.user_id == current_user_id,
            ShoppingCartItem.recipe_id == recipe.id,
        )
        is_in_shopping_cart = (await session.execute(cart_stmt)).first() is not None

    return {
        "id": recipe.id,
        "name": recipe.title,
        "text": recipe.description,
        "image": _absolute_media_url(request, recipe.image),
        "cooking_time": recipe.cooking_time_minutes,
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in tags],
        "ingredients": [
            {"id": row.id, "name": row.name, "measurement_unit": row.unit, "amount": float(row.amount)}
            for row in ingredients_rows
        ],
        "author": await _user_to_foodgram(session, author, current_user_id, request),
        "is_favorited": is_favorited,
        "is_in_shopping_cart": is_in_shopping_cart,
        "steps": [{"position": s.position, "text": s.text, "duration_sec": s.duration_sec} for s in steps],
    }


@router.post("/auth/token/login/", status_code=status.HTTP_200_OK)
async def token_login(payload: dict, session: AsyncSession = Depends(get_db_session)):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password required")

    user = await users_repo.get_by_email(session, str(email))
    if not user or not verify_password(str(password), user.password_hash):
        return JSONResponse(status_code=400, content={"non_field_errors": ["Unable to log in with provided credentials"]})

    return {"auth_token": create_access_token(user.id)}


@router.post("/auth/token/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def token_logout():
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(payload: dict, session: AsyncSession = Depends(get_db_session)):
    email = payload.get("email")
    password = payload.get("password")
    username = payload.get("username")
    first_name = payload.get("first_name", "")
    last_name = payload.get("last_name", "")
    if not email or not password or not username:
        return JSONResponse(status_code=400, content={"non_field_errors": ["email, username and password required"]})

    if await users_repo.get_by_email(session, str(email)):
        return JSONResponse(status_code=400, content={"email": ["User with this email already exists"]})
    if await users_repo.get_by_username(session, str(username)):
        return JSONResponse(status_code=400, content={"username": ["User with this username already exists"]})

    user = await users_repo.create(
        session,
        email=str(email),
        username=str(username),
        first_name=str(first_name or ""),
        last_name=str(last_name or ""),
        password_hash=hash_password(str(password)),
        is_admin=False,
    )
    return await _user_to_foodgram(session, user, None)


@router.get("/users/me/")
async def users_me(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    return await _user_to_foodgram(session, user, user.id, request)


@router.get("/users/subscriptions/")
async def list_subscriptions(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=6, ge=1),
    recipes_limit: int = Query(default=3, ge=0),
):
    limit = clamp_limit(limit)
    recipes_limit = min(recipes_limit, 100)

    author_ids = await subs_repo.list_author_ids(session, user_id=user.id)
    count = len(author_ids)
    offset = (page - 1) * limit
    paged_ids = author_ids[offset: offset + limit]
    results: List[dict] = []

    for author_id in paged_ids:
        author = await users_repo.get_by_id(session, author_id)
        if not author:
            continue

        stmt = select(Recipe).where(Recipe.author_id == author_id).order_by(Recipe.id.desc())
        author_recipes = list((await session.execute(stmt)).scalars().all())
        recipes_count = len(author_recipes)
        author_recipes = author_recipes[:recipes_limit] if recipes_limit else []
        recipes_short = [
            {
                "id": r.id,
                "name": r.title,
                "image": _absolute_media_url(request, r.image),
                "cooking_time": r.cooking_time_minutes,
            }
            for r in author_recipes
        ]

        results.append({
            **(await _user_to_foodgram(session, author, user.id, request)),
            "recipes": recipes_short,
            "recipes_count": recipes_count,
        })

    meta = _page_meta(count, page, limit, request)
    return {**meta, "results": results}


@router.get("/users/{user_id}/")
async def get_user(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_optional_user_token),
):
    user = await users_repo.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    current_user_id = current_user.id if current_user else None
    return await _user_to_foodgram(session, user, current_user_id, request)


@router.get("/users/")
async def list_users(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_optional_user_token),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=6, ge=1),
):
    limit = clamp_limit(limit)
    count = await users_repo.count(session)
    offset = (page - 1) * limit
    users = await users_repo.list(session, limit=limit, offset=offset)
    current_user_id = current_user.id if current_user else None
    results = [await _user_to_foodgram(session, u, current_user_id, request) for u in users]
    meta = _page_meta(count, page, limit, request)
    return {**meta, "results": results}


@router.post("/users/set_password/", status_code=status.HTTP_204_NO_CONTENT)
async def set_password(
    payload: dict,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="current_password and new_password required")
    if not verify_password(str(current_password), user.password_hash):
        return JSONResponse(status_code=400, content={"current_password": ["Wrong password"]})
    await users_repo.update_password_hash(session, user=user, password_hash=hash_password(str(new_password)))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/users/me/avatar/")
async def set_avatar(
    request: Request,
    payload: dict,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    avatar = payload.get("avatar")
    saved_avatar = user.avatar

    if avatar:
        if user.avatar and user.avatar.startswith("/media/"):
            delete_image_file(user.avatar)
        saved_avatar = save_base64_image(avatar, subdir="avatars")

    await users_repo.update_avatar(session, user=user, avatar=saved_avatar)
    return {"avatar": _absolute_media_url(request, user.avatar)}


@router.delete("/users/me/avatar/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    if user.avatar and user.avatar.startswith("/media/"):
        delete_image_file(user.avatar)
    await users_repo.update_avatar(session, user=user, avatar=None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/reset_password/", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password():
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/{author_id}/subscribe/", status_code=status.HTTP_201_CREATED)
async def subscribe(
    request: Request,
    author_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    if author_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")
    author = await users_repo.get_by_id(session, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Not found")
    if not await subs_repo.is_subscribed(session, user_id=user.id, author_id=author_id):
        await subs_repo.add(session, user_id=user.id, author_id=author_id)
    return {**(await _user_to_foodgram(session, author, user.id, request)), "recipes": [], "recipes_count": 0}


@router.delete("/users/{author_id}/subscribe/", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
    author_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    await subs_repo.remove(session, user_id=user.id, author_id=author_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tags/")
async def list_tags(session: AsyncSession = Depends(get_db_session)):
    tags = await tags_repo.list(session)
    return [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in tags]


@router.get("/ingredients/")
async def list_ingredients(
    session: AsyncSession = Depends(get_db_session),
    name: str = Query(default="", alias="name"),
):
    items = await ingredients_repo.search(session, search=name)
    return [{"id": i.id, "name": i.name, "measurement_unit": i.unit} for i in items]


@router.get("/recipes/")
async def list_recipes(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_optional_user_token),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=6, ge=1),
    author: Optional[int] = Query(default=None),
    tags: Optional[List[str]] = Query(default=None),
    is_favorited: int = Query(default=0),
    is_in_shopping_cart: int = Query(default=0),
):
    limit = clamp_limit(limit)
    current_user_id = current_user.id if current_user else None
    if (is_favorited or is_in_shopping_cart) and current_user_id is None:
        return {"count": 0, "next": None, "previous": None, "results": []}

    tag_ids: Optional[List[int]] = None
    if tags:
        tag_objs = await tags_repo.get_by_slugs(session, slugs=tags)
        tag_ids = [t.id for t in tag_objs]

    offset = (page - 1) * limit
    total = await recipes_repo.count_filtered(
        session,
        author_id=author,
        tag_ids=tag_ids,
        user_id=current_user_id,
        is_favorited=bool(is_favorited),
        is_in_shopping_cart=bool(is_in_shopping_cart),
    )
    recipes = await recipes_repo.list_filtered(
        session,
        author_id=author,
        tag_ids=tag_ids,
        limit=limit,
        offset=offset,
        user_id=current_user_id,
        is_favorited=bool(is_favorited),
        is_in_shopping_cart=bool(is_in_shopping_cart),
    )
    results = [await _recipe_to_foodgram(session, r, current_user_id, request) for r in recipes]
    meta = _page_meta(total, page, limit, request)
    return {**meta, "results": results}


@router.get("/recipes/download_shopping_cart/")
async def download_shopping_cart(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    from app.api.routes.shopping_cart import aggregated_ingredients

    items = await aggregated_ingredients(session=session, user=user)
    lines = [f"{it['name']} - {it['amount']} {it['unit']}" for it in items]
    content = "\n".join(lines) + "\n"
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="shopping-list.txt"'},
    )


@router.get("/recipes/{recipe_id:int}/", response_model=FoodgramRecipeOut)
async def get_recipe(
    recipe_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_optional_user_token),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Not found")
    current_user_id = current_user.id if current_user else None
    return await _recipe_to_foodgram(session, recipe, current_user_id, request)


@router.post("/recipes/", status_code=status.HTTP_201_CREATED, response_model=FoodgramRecipeOut)
async def create_recipe(
    request: Request,
    payload: FoodgramRecipeCreate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    recipe_create = RecipeCreate(
        title=payload.name,
        description=payload.text,
        cooking_time_minutes=int(payload.cooking_time),
        tag_ids=[int(t) for t in (payload.tags or [])],
        ingredients=[
            RecipeIngredientIn(ingredient_id=int(i.id), amount=float(i.amount))
            for i in (payload.ingredients or [])
        ],
        steps=[
            RecipeStepIn(
                position=int(s.position),
                text=str(s.text),
                duration_sec=int(s.duration_sec) if s.duration_sec is not None else None,
            )
            for s in (payload.steps or [])
        ],
    )

    recipe = await recipes_repo.create(session, recipe_create, author_id=user.id)

    if payload.image:
        saved_path = save_base64_image(payload.image, subdir="recipes")
        print("DEBUG payload.image prefix =", payload.image[:30])
        print("DEBUG saved_path =", saved_path)

        recipe.image = saved_path
        print("DEBUG recipe.image after assign =", recipe.image)

        await session.flush()
        print("DEBUG recipe.image after flush =", recipe.image)

    await session.commit()
    await session.refresh(recipe)

    print("DEBUG recipe.image after refresh =", recipe.image)

    db_recipe = await recipes_repo.get(session, recipe.id)
    print("DEBUG image from db =", db_recipe.image)

    return await _recipe_to_foodgram(session, recipe, user.id, request)


@router.patch("/recipes/{recipe_id:int}/", response_model=FoodgramRecipeOut)
async def update_recipe(
    recipe_id: int,
    request: Request,
    payload: FoodgramRecipeUpdate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Not found")
    if recipe.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    data: dict[str, Any] = {}

    if payload.name is not None:
        data["title"] = payload.name
    if payload.text is not None:
        data["description"] = payload.text
    if payload.cooking_time is not None:
        data["cooking_time_minutes"] = int(payload.cooking_time)
    if payload.tags is not None:
        data["tag_ids"] = [int(t) for t in payload.tags]
    if payload.ingredients is not None:
        data["ingredients"] = [
            RecipeIngredientIn(ingredient_id=int(i.id), amount=float(i.amount))
            for i in payload.ingredients
        ]
    if payload.steps is not None:
        data["steps"] = [
            RecipeStepIn(
                position=int(s.position),
                text=str(s.text),
                duration_sec=int(s.duration_sec) if s.duration_sec is not None else None,
            )
            for s in payload.steps
        ]

    if data:
        upd = RecipeUpdate(**data)
        recipe = await recipes_repo.update(session, recipe, upd)

    if payload.image is not None:
        if recipe.image and recipe.image.startswith("/media/"):
            delete_image_file(recipe.image)
        recipe.image = save_base64_image(payload.image, subdir="recipes")

    await session.commit()
    await session.refresh(recipe)

    return await _recipe_to_foodgram(session, recipe, user.id, request)


@router.delete("/recipes/{recipe_id:int}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    if recipe.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if recipe.image and recipe.image.startswith("/media/"):
        delete_image_file(recipe.image)

    await recipes_repo.delete(session, recipe)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/recipes/{recipe_id:int}/favorite/", status_code=status.HTTP_201_CREATED)
async def add_favorite_foodgram(
    request: Request,
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    exists_stmt = select(Favorite.id).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    if (await session.execute(exists_stmt)).first() is None:
        session.add(Favorite(user_id=user.id, recipe_id=recipe_id))
        await session.commit()

    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": recipe.id,
        "name": recipe.title,
        "image": _absolute_media_url(request, recipe.image),
        "cooking_time": recipe.cooking_time_minutes,
    }


@router.delete("/recipes/{recipe_id:int}/favorite/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_foodgram(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    stmt = select(Favorite).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    fav = (await session.execute(stmt)).scalars().first()
    if fav is not None:
        await session.delete(fav)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/recipes/{recipe_id:int}/shopping_cart/", status_code=status.HTTP_201_CREATED)
async def add_to_cart_foodgram(
    request: Request,
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Not found")

    exists_stmt = select(ShoppingCartItem.id).where(
        ShoppingCartItem.user_id == user.id,
        ShoppingCartItem.recipe_id == recipe_id,
    )
    if (await session.execute(exists_stmt)).first() is None:
        session.add(ShoppingCartItem(user_id=user.id, recipe_id=recipe_id))
        await session.commit()

    return {
        "id": recipe.id,
        "name": recipe.title,
        "image": _absolute_media_url(request, recipe.image),
        "cooking_time": recipe.cooking_time_minutes,
    }


@router.delete("/recipes/{recipe_id:int}/shopping_cart/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart_foodgram(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    stmt = select(ShoppingCartItem).where(ShoppingCartItem.user_id == user.id, ShoppingCartItem.recipe_id == recipe_id)
    item = (await session.execute(stmt)).scalars().first()
    if item is not None:
        await session.delete(item)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/recipes/{recipe_id:int}/get-link/")
async def get_short_link(recipe_id: int, request: Request, session: AsyncSession = Depends(get_db_session)):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Not found")

    short = await short_links_repo.get_or_create(session, recipe_id=recipe_id)
    base = str(request.base_url).rstrip("/")
    return {"short-link": f"{base}/s/{short.code}"}