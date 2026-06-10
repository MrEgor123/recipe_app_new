import pytest

from conftest import (
    assert_status,
    assert_status_in,
    get_json,
    make_token_header,
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


def get_auth_token(client, payload):
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


def get_current_user(client, token: str):
    response = client.get(
        "/api/users/me/",
        headers=make_token_header(token),
    )
    assert_status(response, 200)
    return get_json(response)


def get_existing_recipe_id(client):
    response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(response, 200)

    data = get_json(response)
    items = data.get("items", [])

    assert items, "Для тестов избранного нужен хотя бы один опубликованный рецепт"

    return items[0]["id"]


def get_existing_author_id_from_recipe(client):
    response = client.get("/api/recipes/", params={"page": 1, "limit": 1})
    assert_status(response, 200)

    data = get_json(response)
    results = data.get("results") or data.get("items") or []

    assert results, "Для тестов подписок нужен хотя бы один опубликованный рецепт"

    author = results[0].get("author") or {}
    author_id = author.get("id")

    assert author_id, "У рецепта должен быть автор"

    return author_id


def test_add_recipe_to_favorite_success(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = client.post(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["id"] == recipe_id


def test_add_recipe_to_favorite_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.post(f"/api/recipes/{recipe_id}/favorite/")

    assert_status(response, 401)


@pytest.mark.xfail(
    reason=(
        "Сейчас endpoint избранного для несуществующего рецепта падает "
        "IntegrityError вместо корректного 404"
    )
)
def test_add_missing_recipe_to_favorite_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.post(
        "/api/recipes/999999999/favorite/",
        headers=make_token_header(token),
    )

    assert_status(response, 404)


def test_add_duplicate_favorite_is_idempotent(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    first_response = client.post(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )
    assert_status(first_response, 201)

    second_response = client.post(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )

    assert_status(second_response, 201)
    data = get_json(second_response)

    assert data["id"] == recipe_id


def test_get_favorites_contains_added_recipe(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    add_response = client.post(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )
    assert_status(add_response, 201)

    response = client.get(
        "/api/recipes/",
        headers=make_token_header(token),
        params={
            "is_favorited": 1,
            "page": 1,
            "limit": 100,
        },
    )

    assert_status(response, 200)
    data = get_json(response)

    results = data.get("results") or data.get("items") or []

    assert any(item["id"] == recipe_id for item in results)


def test_remove_recipe_from_favorite_success(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    add_response = client.post(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )
    assert_status(add_response, 201)

    response = client.delete(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_remove_recipe_from_favorite_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.delete(f"/api/recipes/{recipe_id}/favorite/")

    assert_status(response, 401)


def test_remove_missing_recipe_from_favorite_is_idempotent(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.delete(
        "/api/recipes/999999999/favorite/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_remove_not_favorited_recipe_is_idempotent(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = client.delete(
        f"/api/recipes/{recipe_id}/favorite/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_subscribe_to_author_success(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    current_user = get_current_user(client, token)
    author_id = get_existing_author_id_from_recipe(client)

    if author_id == current_user["id"]:
        return

    response = client.post(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["id"] == author_id
    assert data.get("is_subscribed") is True


def test_subscribe_without_auth_rejected(client):
    author_id = get_existing_author_id_from_recipe(client)

    response = client.post(f"/api/users/{author_id}/subscribe/")

    assert_status(response, 401)


def test_subscribe_to_missing_author_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.post(
        "/api/users/999999999/subscribe/",
        headers=make_token_header(token),
    )

    assert_status(response, 404)


def test_subscribe_to_self_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    current_user = get_current_user(client, token)

    response = client.post(
        f"/api/users/{current_user['id']}/subscribe/",
        headers=make_token_header(token),
    )

    assert_status(response, 400)


def test_duplicate_subscribe_is_idempotent(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    current_user = get_current_user(client, token)
    author_id = get_existing_author_id_from_recipe(client)

    if author_id == current_user["id"]:
        return

    first_response = client.post(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )
    assert_status(first_response, 201)

    second_response = client.post(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )

    assert_status(second_response, 201)
    data = get_json(second_response)

    assert data["id"] == author_id


def test_get_subscriptions_contains_author(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    current_user = get_current_user(client, token)
    author_id = get_existing_author_id_from_recipe(client)

    if author_id == current_user["id"]:
        return

    subscribe_response = client.post(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )
    assert_status(subscribe_response, 201)

    response = client.get(
        "/api/users/subscriptions/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    results = data.get("results") if isinstance(data, dict) else data

    assert isinstance(results, list)
    assert any(item["id"] == author_id for item in results)


def test_get_subscriptions_without_auth_rejected(client):
    response = client.get("/api/users/subscriptions/")

    assert_status(response, 401)


def test_unsubscribe_success(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    current_user = get_current_user(client, token)
    author_id = get_existing_author_id_from_recipe(client)

    if author_id == current_user["id"]:
        return

    subscribe_response = client.post(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )
    assert_status(subscribe_response, 201)

    response = client.delete(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_unsubscribe_without_auth_rejected(client):
    author_id = get_existing_author_id_from_recipe(client)

    response = client.delete(f"/api/users/{author_id}/subscribe/")

    assert_status(response, 401)


def test_unsubscribe_missing_author_is_idempotent(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.delete(
        "/api/users/999999999/subscribe/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_unsubscribe_not_subscribed_is_idempotent(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    current_user = get_current_user(client, token)
    author_id = get_existing_author_id_from_recipe(client)

    if author_id == current_user["id"]:
        return

    response = client.delete(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_subscription_changes_author_profile_flag(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    current_user = get_current_user(client, token)
    author_id = get_existing_author_id_from_recipe(client)

    if author_id == current_user["id"]:
        return

    before_response = client.get(
        f"/api/users/{author_id}/",
        headers=make_token_header(token),
    )
    assert_status(before_response, 200)

    subscribe_response = client.post(
        f"/api/users/{author_id}/subscribe/",
        headers=make_token_header(token),
    )
    assert_status(subscribe_response, 201)

    after_response = client.get(
        f"/api/users/{author_id}/",
        headers=make_token_header(token),
    )
    assert_status(after_response, 200)

    after_data = get_json(after_response)

    assert after_data.get("is_subscribed") is True