from conftest import (
    assert_status,
    assert_status_in,
    get_json,
    make_bearer_header,
    make_token_header,
)


def register_user_new_api(client, payload):
    return client.post(
        "/auth/register",
        json={
            "email": payload["email"],
            "username": payload["username"],
            "password": payload["password"],
        },
    )


def login_user_new_api(client, username: str, password: str):
    return client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )


def register_user_foodgram(client, payload):
    return client.post(
        "/api/users/",
        json={
            "email": payload["email"],
            "username": payload["username"],
            "first_name": payload["first_name"],
            "last_name": payload["last_name"],
            "password": payload["password"],
        },
    )


def login_user_foodgram(client, email: str, password: str):
    return client.post(
        "/api/auth/token/login/",
        json={
            "email": email,
            "password": password,
        },
    )


def get_bearer_token(client, payload):
    register_response = register_user_new_api(client, payload)
    assert_status_in(register_response, {201, 400})

    login_response = login_user_new_api(
        client,
        username=payload["username"],
        password=payload["password"],
    )
    assert_status(login_response, 200)

    token = get_json(login_response).get("access_token")

    assert token
    assert isinstance(token, str)

    return token


def get_token_auth(client, payload):
    register_response = register_user_foodgram(client, payload)
    assert_status_in(register_response, {201, 400})

    login_response = login_user_foodgram(
        client,
        email=payload["email"],
        password=payload["password"],
    )
    assert_status(login_response, 200)

    token = get_json(login_response).get("auth_token")

    assert token
    assert isinstance(token, str)

    return token


def get_first_tag_id(client):
    response = client.get("/tags")
    assert_status(response, 200)

    tags = get_json(response)
    assert tags, "Для тестов нужен хотя бы один тег в БД"

    return tags[0]["id"]


def get_first_ingredient_id(client):
    response = client.get("/ingredients")
    assert_status(response, 200)

    ingredients = get_json(response)
    assert ingredients, "Для тестов нужен хотя бы один ингредиент в БД"

    return ingredients[0]["id"]


def make_recipe_payload(client, title="Тестовый рецепт целостности"):
    return {
        "title": title,
        "description": (
            "Овощи нарезать, добавить соль, масло и аккуратно перемешать. "
            "Это нормальный тестовый рецепт для проверки связей."
        ),
        "cooking_time_minutes": 15,
        "base_servings": 2,
        "tag_ids": [get_first_tag_id(client)],
        "ingredients": [
            {
                "ingredient_id": get_first_ingredient_id(client),
                "amount": 100,
            }
        ],
        "steps": [
            {
                "position": 1,
                "text": "Нарезать овощи.",
                "duration_sec": 300,
            },
            {
                "position": 2,
                "text": "Добавить соль и масло.",
                "duration_sec": 120,
            },
        ],
    }


def create_recipe(client, token: str, payload: dict | None = None):
    if payload is None:
        payload = make_recipe_payload(client)

    return client.post(
        "/recipes",
        headers=make_bearer_header(token),
        json=payload,
    )


def create_comment(client, recipe_id: int, token: str, text: str, parent_id=None):
    return client.post(
        f"/api/recipes/{recipe_id}/comments/",
        headers=make_token_header(token),
        json={
            "text": text,
            "parent_id": parent_id,
        },
    )


def create_collection(client, token: str, name: str, description: str | None = None):
    return client.post(
        "/collections/",
        headers=make_bearer_header(token),
        json={
            "name": name,
            "description": description,
        },
    )


def test_user_email_uniqueness(client, test_user_payload):
    first_response = register_user_new_api(client, test_user_payload)
    assert_status(first_response, 201)

    second_payload = {
        **test_user_payload,
        "username": f"{test_user_payload['username']}_other",
    }

    second_response = register_user_new_api(client, second_payload)

    assert_status_in(second_response, {400, 409})


def test_user_username_uniqueness(client, test_user_payload, unique_suffix):
    first_response = register_user_new_api(client, test_user_payload)
    assert_status(first_response, 201)

    second_payload = {
        **test_user_payload,
        "email": f"other_username_{unique_suffix}@example.com",
    }

    second_response = register_user_new_api(client, second_payload)

    assert_status_in(second_response, {400, 409})


def test_same_user_can_login_after_duplicate_register_attempt(client, test_user_payload):
    first_response = register_user_new_api(client, test_user_payload)
    assert_status(first_response, 201)

    duplicate_response = register_user_new_api(client, test_user_payload)
    assert_status_in(duplicate_response, {400, 409})

    login_response = login_user_new_api(
        client,
        username=test_user_payload["username"],
        password=test_user_payload["password"],
    )

    assert_status(login_response, 200)
    data = get_json(login_response)

    assert "access_token" in data


def test_recipe_ingredients_and_steps_are_persisted(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_recipe(client, token)
    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}")
    assert_status(response, 200)

    data = get_json(response)

    assert len(data["ingredients"]) == 1
    assert len(data["steps"]) == 2
    assert data["ingredients"][0]["amount"] == 100
    assert data["steps"][0]["position"] == 1
    assert data["steps"][1]["position"] == 2


def test_recipe_update_replaces_ingredients(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_recipe(client, token)
    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]
    ingredient_id = get_first_ingredient_id(client)

    update_response = client.patch(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(token),
        json={
            "ingredients": [
                {
                    "ingredient_id": ingredient_id,
                    "amount": 250,
                }
            ],
        },
    )
    assert_status(update_response, 200)

    data = get_json(update_response)

    assert len(data["ingredients"]) == 1
    assert data["ingredients"][0]["id"] == ingredient_id
    assert data["ingredients"][0]["base_amount"] == 250


def test_recipe_update_replaces_steps(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_recipe(client, token)
    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    update_response = client.patch(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(token),
        json={
            "steps": [
                {
                    "position": 1,
                    "text": "Новый первый шаг приготовления.",
                    "duration_sec": 60,
                }
            ],
        },
    )
    assert_status(update_response, 200)

    data = get_json(update_response)

    assert len(data["steps"]) == 1
    assert data["steps"][0]["text"] == "Новый первый шаг приготовления."


def test_recipe_delete_removes_public_access(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_recipe(client, token)
    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    delete_response = client.delete(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(token),
    )
    assert_status(delete_response, 204)

    get_response = client.get(f"/recipes/{recipe_id}")
    assert_status(get_response, 404)


def test_recipe_delete_cascades_comments(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    token = get_token_auth(client, test_user_payload)

    create_recipe_response = create_recipe(client, bearer_token)
    assert_status(create_recipe_response, 201)

    recipe_id = get_json(create_recipe_response)["id"]

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Очень вкусный рецепт для проверки каскадного удаления комментария",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    delete_recipe_response = client.delete(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(bearer_token),
    )
    assert_status(delete_recipe_response, 204)

    like_deleted_comment_response = client.post(
        f"/api/comments/{comment_id}/like/",
        headers=make_token_header(token),
    )

    assert_status(like_deleted_comment_response, 404)


def test_comment_delete_removes_comment_from_list(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    token = get_token_auth(client, test_user_payload)

    create_recipe_response = create_recipe(client, bearer_token)
    assert_status(create_recipe_response, 201)

    recipe_id = get_json(create_recipe_response)["id"]

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Комментарий для проверки удаления из списка",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    delete_response = client.delete(
        f"/api/comments/{comment_id}/",
        headers=make_token_header(token),
    )
    assert_status(delete_response, 204)

    list_response = client.get(f"/api/recipes/{recipe_id}/comments/")
    assert_status(list_response, 200)

    comments = get_json(list_response)

    assert all(comment["id"] != comment_id for comment in comments)


def test_comment_delete_cascades_reply(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    token = get_token_auth(client, test_user_payload)

    create_recipe_response = create_recipe(client, bearer_token)
    assert_status(create_recipe_response, 201)

    recipe_id = get_json(create_recipe_response)["id"]

    parent_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Родительский комментарий для проверки каскада ответов",
    )
    assert_status(parent_response, 201)

    parent_id = get_json(parent_response)["id"]

    import time
    time.sleep(16)

    reply_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Ответ на родительский комментарий для проверки удаления",
        parent_id=parent_id,
    )
    assert_status(reply_response, 201)

    reply_id = get_json(reply_response)["id"]

    delete_response = client.delete(
        f"/api/comments/{parent_id}/",
        headers=make_token_header(token),
    )
    assert_status(delete_response, 204)

    like_reply_response = client.post(
        f"/api/comments/{reply_id}/like/",
        headers=make_token_header(token),
    )

    assert_status(like_reply_response, 404)


def test_comment_like_is_unique_for_user(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    token = get_token_auth(client, test_user_payload)

    create_recipe_response = create_recipe(client, bearer_token)
    assert_status(create_recipe_response, 201)

    recipe_id = get_json(create_recipe_response)["id"]

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Комментарий для проверки уникальности лайка",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    first_like_response = client.post(
        f"/api/comments/{comment_id}/like/",
        headers=make_token_header(token),
    )
    assert_status(first_like_response, 200)

    second_like_response = client.post(
        f"/api/comments/{comment_id}/like/",
        headers=make_token_header(token),
    )
    assert_status(second_like_response, 200)

    first_data = get_json(first_like_response)
    second_data = get_json(second_like_response)

    assert second_data["likes_count"] == first_data["likes_count"]


def test_collection_name_unique_per_user(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    name = f"Уникальная подборка {unique_suffix}"

    first_response = create_collection(
        client,
        token=token,
        name=name,
        description="Первая подборка",
    )
    assert_status(first_response, 201)

    second_response = create_collection(
        client,
        token=token,
        name=name,
        description="Повторная подборка",
    )

    assert_status(second_response, 400)


def test_collection_same_name_allowed_for_different_users(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    first_token = get_bearer_token(client, test_user_payload)
    second_token = get_bearer_token(client, second_test_user_payload)

    name = f"Одинаковое название подборки {unique_suffix}"

    first_response = create_collection(
        client,
        token=first_token,
        name=name,
        description="Первая подборка",
    )
    assert_status(first_response, 201)

    second_response = create_collection(
        client,
        token=second_token,
        name=name,
        description="Вторая подборка",
    )
    assert_status(second_response, 201)


def test_collection_delete_removes_collection_access(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка для удаления связи {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    delete_response = client.delete(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(delete_response, 204)

    get_response = client.get(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(get_response, 404)


def test_collection_recipe_relation_add_and_remove(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_recipe_response = create_recipe(client, token)
    assert_status(create_recipe_response, 201)

    recipe_id = get_json(create_recipe_response)["id"]

    create_collection_response = create_collection(
        client,
        token=token,
        name=f"Подборка связь рецепт {unique_suffix}",
        description="Описание",
    )
    assert_status(create_collection_response, 201)

    collection_id = get_json(create_collection_response)["id"]

    add_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(add_response, 201)

    recipes_response = client.get(
        f"/collections/{collection_id}/recipes/",
        headers=make_bearer_header(token),
    )
    assert_status(recipes_response, 200)

    recipes = get_json(recipes_response)
    assert any(recipe["id"] == recipe_id for recipe in recipes)

    remove_response = client.delete(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(remove_response, 204)

    recipes_after_remove_response = client.get(
        f"/collections/{collection_id}/recipes/",
        headers=make_bearer_header(token),
    )
    assert_status(recipes_after_remove_response, 200)

    recipes_after_remove = get_json(recipes_after_remove_response)
    assert all(recipe["id"] != recipe_id for recipe in recipes_after_remove)


def test_favorite_delete_after_recipe_delete_is_safe(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    token = get_token_auth(client, test_user_payload)

    create_recipe_response = create_recipe(client, bearer_token)
    assert_status(create_recipe_response, 201)

    recipe_id = get_json(create_recipe_response)["id"]

    favorite_response = client.post(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )
    assert_status(favorite_response, 201)

    delete_recipe_response = client.delete(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(bearer_token),
    )
    assert_status(delete_recipe_response, 204)

    delete_favorite_response = client.delete(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )

    assert_status_in(delete_favorite_response, {204, 404})


def test_shopping_cart_delete_after_recipe_delete_is_safe(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    token = get_token_auth(client, test_user_payload)

    create_recipe_response = create_recipe(client, bearer_token)
    assert_status(create_recipe_response, 201)

    recipe_id = get_json(create_recipe_response)["id"]

    cart_response = client.post(
        f"/api/recipes/{recipe_id}/shopping_cart/",
        headers=make_token_header(token),
    )
    assert_status(cart_response, 201)

    delete_recipe_response = client.delete(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(bearer_token),
    )
    assert_status(delete_recipe_response, 204)

    delete_cart_response = client.delete(
        f"/api/recipes/{recipe_id}/shopping_cart/",
        headers=make_token_header(token),
    )

    assert_status_in(delete_cart_response, {204, 404})


def test_public_lists_remain_available_after_many_mutations(client, test_user_payload, unique_suffix):
    bearer_token = get_bearer_token(client, test_user_payload)

    for index in range(3):
        payload = make_recipe_payload(
            client,
            title=f"Рецепт после мутаций {unique_suffix} {index}",
        )
        create_response = create_recipe(client, bearer_token, payload)
        assert_status(create_response, 201)

    recipes_response = client.get("/recipes", params={"page": 1, "size": 10})
    assert_status(recipes_response, 200)

    tags_response = client.get("/tags")
    assert_status(tags_response, 200)

    ingredients_response = client.get("/ingredients")
    assert_status(ingredients_response, 200)

    assert isinstance(get_json(recipes_response)["items"], list)
    assert isinstance(get_json(tags_response), list)
    assert isinstance(get_json(ingredients_response), list)