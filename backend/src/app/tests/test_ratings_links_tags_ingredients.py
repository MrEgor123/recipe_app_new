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


def get_existing_recipe_id(client):
    response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(response, 200)

    data = get_json(response)
    items = data.get("items", [])

    assert items, "Для тестов нужен хотя бы один опубликованный рецепт"

    return items[0]["id"]


def get_existing_tag_id(client):
    response = client.get("/tags")
    assert_status(response, 200)

    data = get_json(response)

    assert isinstance(data, list)
    assert data, "Для тестов нужен хотя бы один тег"

    return data[0]["id"]


def get_existing_ingredient_id(client):
    response = client.get("/ingredients")
    assert_status(response, 200)

    data = get_json(response)

    assert isinstance(data, list)
    assert data, "Для тестов нужен хотя бы один ингредиент"

    return data[0]["id"]


def get_short_link_value(data: dict) -> str:
    if "short-link" in data:
        return data["short-link"]

    if "url" in data:
        return data["url"]

    return ""


def get_short_link_code(data: dict) -> str:
    if "code" in data:
        return data["code"]

    link = get_short_link_value(data)
    return link.rstrip("/").split("/")[-1] if link else ""


def test_rate_recipe_success(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
        json={"rating": 5},
    )

    assert_status(response, 200)
    data = get_json(response)

    assert "rating_avg" in data
    assert "rating_count" in data
    assert "user_rating" in data
    assert data["user_rating"] == 5


def test_rate_recipe_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        json={"rating": 5},
    )

    assert_status(response, 401)


def test_rate_missing_recipe_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.post(
        "/api/recipes/999999999/rating/",
        headers=make_token_header(token),
        json={"rating": 5},
    )

    assert_status(response, 404)


def test_rate_recipe_invalid_low_value_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
        json={"rating": 0},
    )

    assert_status_in(response, {400, 422})


def test_rate_recipe_invalid_high_value_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
        json={"rating": 6},
    )

    assert_status_in(response, {400, 422})


def test_update_recipe_rating_success(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    first_response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
        json={"rating": 3},
    )
    assert_status(first_response, 200)

    second_response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
        json={"rating": 4},
    )

    assert_status(second_response, 200)
    data = get_json(second_response)

    assert data["user_rating"] == 4


def test_delete_recipe_rating_success(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    rate_response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
        json={"rating": 5},
    )
    assert_status(rate_response, 200)

    response = client.delete(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_delete_recipe_rating_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.delete(f"/api/recipes/{recipe_id}/rating/")

    assert_status(response, 401)


def test_delete_missing_recipe_rating_is_idempotent(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.delete(
        "/api/recipes/999999999/rating/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_delete_not_existing_rating_is_handled(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = client.delete(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
    )

    assert_status_in(response, {204, 400, 404})


def test_recipe_detail_contains_rating_fields(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    rate_response = client.post(
        f"/api/recipes/{recipe_id}/rating/",
        headers=make_token_header(token),
        json={"rating": 5},
    )
    assert_status(rate_response, 200)

    response = client.get(
        f"/api/recipes/{recipe_id}/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert "rating_avg" in data
    assert "rating_count" in data
    assert "user_rating" in data


def test_create_short_link_success(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.post(f"/recipes/{recipe_id}/short-link")

    assert_status(response, 200)
    data = get_json(response)

    assert "code" in data or "short-link" in data or "url" in data
    assert get_short_link_value(data) or data.get("code")


def test_create_short_link_for_missing_recipe_rejected(client):
    response = client.post("/recipes/999999999/short-link")

    assert_status(response, 404)


def test_foodgram_get_recipe_link_success(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.get(f"/api/recipes/{recipe_id}/get-link/")

    assert_status(response, 200)
    data = get_json(response)

    assert "short-link" in data
    assert data["short-link"]


def test_foodgram_get_recipe_link_missing_recipe_rejected(client):
    response = client.get("/api/recipes/999999999/get-link/")

    assert_status(response, 404)


def test_redirect_short_link_or_not_found(client):
    recipe_id = get_existing_recipe_id(client)

    create_response = client.post(f"/recipes/{recipe_id}/short-link")
    assert_status(create_response, 200)

    data = get_json(create_response)
    code = get_short_link_code(data)

    assert code

    response = client.get(f"/s/{code}", follow_redirects=False)

    assert_status_in(response, {307, 308, 404})


def test_redirect_unknown_short_link_rejected(client):
    response = client.get("/s/unknown-code-for-tests", follow_redirects=False)

    assert_status(response, 404)


def test_get_tags_list_success(client):
    response = client.get("/tags")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_get_tag_by_id_success(client):
    tag_id = get_existing_tag_id(client)

    response = client.get(f"/tags/{tag_id}")

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == tag_id
    assert "name" in data
    assert "slug" in data


def test_get_missing_tag_rejected(client):
    response = client.get("/tags/999999999")

    assert_status(response, 404)


def test_foodgram_tags_list_success(client):
    response = client.get("/api/tags/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_get_ingredients_list_success(client):
    response = client.get("/ingredients")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_get_ingredient_by_id_success(client):
    ingredient_id = get_existing_ingredient_id(client)

    response = client.get(f"/ingredients/{ingredient_id}")

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == ingredient_id
    assert "name" in data


def test_get_missing_ingredient_rejected(client):
    response = client.get("/ingredients/999999999")

    assert_status(response, 404)


def test_foodgram_ingredients_list_success(client):
    response = client.get("/api/ingredients/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_foodgram_ingredients_search_success(client):
    response = client.get("/api/ingredients/", params={"name": "соль"})

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_foodgram_ingredients_search_empty_success(client):
    response = client.get(
        "/api/ingredients/",
        params={"name": "несуществующийингредиентpytest"},
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_filter_recipes_by_tag_success(client):
    tag_id = get_existing_tag_id(client)

    response = client.get("/recipes", params={"tag_ids": tag_id})

    assert_status(response, 200)
    data = get_json(response)

    assert "items" in data
    assert isinstance(data["items"], list)


def test_filter_foodgram_recipes_by_tag_success(client):
    tags_response = client.get("/api/tags/")
    assert_status(tags_response, 200)

    tags = get_json(tags_response)
    assert tags, "Для теста фильтрации нужен хотя бы один тег"

    tag_slug = tags[0]["slug"]

    response = client.get("/api/recipes/", params={"tags": tag_slug})

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, dict)
    assert "results" in data or "items" in data or "count" in data