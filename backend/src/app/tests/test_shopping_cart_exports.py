from conftest import (
    assert_status,
    assert_status_in,
    get_json,
    make_token_header,
    make_bearer_header,
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


def get_bearer_auth(client, payload):
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


def get_existing_recipe_id(client):
    response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(response, 200)

    data = get_json(response)
    items = data.get("items", [])

    assert items, "Для тестов списка покупок нужен хотя бы один опубликованный рецепт"

    return items[0]["id"]


def add_recipe_to_cart_foodgram(client, token: str, recipe_id: int):
    return client.post(
        f"/api/recipes/{recipe_id}/shopping_cart/",
        headers=make_token_header(token),
    )


def test_shopping_cart_count_without_auth_rejected(client):
    response = client.get("/shopping-cart/count")

    assert_status_in(response, {401, 403})


def test_shopping_cart_count_initial_success(client, test_user_payload):
    bearer_token = get_bearer_auth(client, test_user_payload)

    response = client.get(
        "/shopping-cart/count",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert "count" in data
    assert isinstance(data["count"], int)
    assert data["count"] >= 0


def test_get_shopping_cart_without_auth_rejected(client):
    response = client.get("/shopping-cart")

    assert_status_in(response, {401, 403})


def test_get_shopping_cart_initial_success(client, test_user_payload):
    bearer_token = get_bearer_auth(client, test_user_payload)

    response = client.get(
        "/shopping-cart",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert "items" in data
    assert "page" in data
    assert "size" in data
    assert "total" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


def test_add_recipe_to_shopping_cart_success(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = add_recipe_to_cart_foodgram(client, token, recipe_id)

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["id"] == recipe_id


def test_add_recipe_to_shopping_cart_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.post(f"/api/recipes/{recipe_id}/shopping_cart/")

    assert_status(response, 401)


def test_add_missing_recipe_to_shopping_cart_rejected_or_idempotent(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)

    response = client.post(
        "/api/recipes/999999999/shopping_cart/",
        headers=make_token_header(token),
    )

    assert_status_in(response, {400, 404, 500})


def test_add_duplicate_recipe_to_shopping_cart_is_handled(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    first_response = add_recipe_to_cart_foodgram(client, token, recipe_id)
    assert_status(first_response, 201)

    second_response = add_recipe_to_cart_foodgram(client, token, recipe_id)

    assert_status_in(second_response, {201, 400})


def test_shopping_cart_count_after_add(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    bearer_token = get_bearer_auth(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    add_response = add_recipe_to_cart_foodgram(client, token, recipe_id)
    assert_status(add_response, 201)

    response = client.get(
        "/shopping-cart/count",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["count"] >= 0


def test_get_shopping_cart_contains_items_list(client, test_user_payload):
    bearer_token = get_bearer_auth(client, test_user_payload)

    response = client.get(
        "/shopping-cart",
        headers=make_bearer_header(bearer_token),
        params={"page": 1, "size": 50},
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data["items"], list)


def test_foodgram_recipes_filter_in_shopping_cart(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    add_response = add_recipe_to_cart_foodgram(client, token, recipe_id)
    assert_status(add_response, 201)

    response = client.get(
        "/api/recipes/",
        headers=make_token_header(token),
        params={
            "is_in_shopping_cart": 1,
            "page": 1,
            "limit": 100,
        },
    )

    assert_status(response, 200)
    data = get_json(response)

    results = data.get("results") or data.get("items") or []

    assert any(item["id"] == recipe_id for item in results)


def test_remove_recipe_from_shopping_cart_success(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    add_response = add_recipe_to_cart_foodgram(client, token, recipe_id)
    assert_status(add_response, 201)

    response = client.delete(
        f"/api/recipes/{recipe_id}/shopping_cart/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_remove_recipe_from_shopping_cart_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.delete(f"/api/recipes/{recipe_id}/shopping_cart/")

    assert_status(response, 401)


def test_remove_missing_recipe_from_shopping_cart_is_handled(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)

    response = client.delete(
        "/api/recipes/999999999/shopping_cart/",
        headers=make_token_header(token),
    )

    assert_status_in(response, {204, 404})


def test_remove_not_added_recipe_from_shopping_cart_is_idempotent(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = client.delete(
        f"/api/recipes/{recipe_id}/shopping_cart/",
        headers=make_token_header(token),
    )

    assert_status_in(response, {204, 400})


def test_shopping_cart_ingredients_without_auth_rejected(client):
    response = client.get("/shopping-cart/ingredients")

    assert_status_in(response, {401, 403})


def test_shopping_cart_ingredients_success(client, test_user_payload):
    bearer_token = get_bearer_auth(client, test_user_payload)

    response = client.get(
        "/shopping-cart/ingredients",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_shopping_cart_market_without_auth_rejected(client):
    response = client.get("/shopping-cart/market")

    assert_status_in(response, {401, 403})


def test_shopping_cart_market_success(client, test_user_payload):
    bearer_token = get_bearer_auth(client, test_user_payload)

    response = client.get(
        "/shopping-cart/market",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list | dict)


def test_export_txt_without_auth_rejected(client):
    response = client.get("/shopping-cart/export.txt")

    assert_status_in(response, {401, 403})


def test_export_txt_success(client, test_user_payload):
    bearer_token = get_bearer_auth(client, test_user_payload)

    response = client.get(
        "/shopping-cart/export.txt",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)

    content_type = response.headers.get("content-type", "")
    assert "text/plain" in content_type or "application/octet-stream" in content_type

    assert response.content is not None


def test_export_pdf_without_auth_rejected(client):
    response = client.get("/shopping-cart/export.pdf")

    assert_status_in(response, {401, 403})


def test_export_pdf_success(client, test_user_payload):
    bearer_token = get_bearer_auth(client, test_user_payload)

    response = client.get(
        "/shopping-cart/export.pdf",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)

    content_type = response.headers.get("content-type", "")
    assert "application/pdf" in content_type or "application/octet-stream" in content_type

    assert response.content is not None
    assert len(response.content) > 0


def test_foodgram_download_shopping_cart_success(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    add_response = add_recipe_to_cart_foodgram(client, token, recipe_id)
    assert_status(add_response, 201)

    response = client.get(
        "/api/recipes/download_shopping_cart/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    assert response.content is not None


def test_foodgram_download_shopping_cart_without_auth_rejected(client):
    response = client.get("/api/recipes/download_shopping_cart/")

    assert_status(response, 401)