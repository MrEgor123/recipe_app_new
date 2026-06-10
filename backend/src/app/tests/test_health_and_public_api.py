from conftest import assert_status, assert_status_in, get_json


def test_health_endpoint(client):
    response = client.get("/health")

    assert_status(response, 200)
    data = get_json(response)

    assert data == {"status": "ok"}


def test_public_tags_new_api(client):
    response = client.get("/tags")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)

    if data:
        tag = data[0]
        assert "id" in tag
        assert "name" in tag
        assert "slug" in tag


def test_public_tags_foodgram_api(client):
    response = client.get("/api/tags/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)

    if data:
        tag = data[0]
        assert "id" in tag
        assert "name" in tag
        assert "slug" in tag


def test_public_ingredients_new_api(client):
    response = client.get("/ingredients")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)

    if data:
        ingredient = data[0]
        assert "id" in ingredient
        assert "name" in ingredient


def test_public_ingredients_foodgram_api(client):
    response = client.get("/api/ingredients/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)

    if data:
        ingredient = data[0]
        assert "id" in ingredient
        assert "name" in ingredient


def test_public_ingredients_search_foodgram_api(client):
    response = client.get("/api/ingredients/", params={"name": "соль"})

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_public_recipes_new_api(client):
    response = client.get("/recipes")

    assert_status(response, 200)
    data = get_json(response)

    assert "items" in data
    assert "page" in data
    assert "size" in data
    assert "total" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


def test_public_recipes_new_api_with_pagination(client):
    response = client.get("/recipes", params={"page": 1, "size": 6})

    assert_status(response, 200)
    data = get_json(response)

    assert data["page"] == 1
    assert data["size"] == 6
    assert isinstance(data["items"], list)


def test_public_recipes_foodgram_api(client):
    response = client.get("/api/recipes/", params={"page": 1, "limit": 6})

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, dict)
    assert "results" in data or "items" in data or "count" in data


def test_public_recipe_detail_for_existing_recipe_if_any(client):
    list_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(list_response, 200)

    list_data = get_json(list_response)
    items = list_data.get("items", [])

    if not items:
        return

    recipe_id = items[0]["id"]

    response = client.get(f"/recipes/{recipe_id}")

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == recipe_id
    assert "title" in data
    assert "description" in data
    assert "cooking_time_minutes" in data
    assert "ingredients" in data
    assert "nutrition_total" in data
    assert "nutrition_per_serving" in data


def test_public_recipe_detail_with_servings_if_any(client):
    list_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(list_response, 200)

    list_data = get_json(list_response)
    items = list_data.get("items", [])

    if not items:
        return

    recipe_id = items[0]["id"]

    response = client.get(f"/recipes/{recipe_id}", params={"servings": 4})

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == recipe_id
    assert data["selected_servings"] == 4


def test_public_not_found_recipe_new_api(client):
    response = client.get("/recipes/999999999")

    assert_status_in(response, {404})


def test_public_profile_for_existing_author_if_any(client):
    list_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(list_response, 200)

    list_data = get_json(list_response)
    items = list_data.get("items", [])

    if not items:
        return

    recipe_id = items[0]["id"]
    recipe_response = client.get(f"/api/recipes/{recipe_id}/")
    assert_status_in(recipe_response, {200, 404})

    if recipe_response.status_code == 404:
        return

    recipe_data = get_json(recipe_response)
    author = recipe_data.get("author") or {}

    author_id = author.get("id")
    if not author_id:
        return

    response = client.get(f"/users/{author_id}/profile/")

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == author_id
    assert "username" in data
    assert "stats" in data
    assert "recipes" in data


def test_public_user_collections_for_existing_author_if_any(client):
    list_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(list_response, 200)

    list_data = get_json(list_response)
    items = list_data.get("items", [])

    if not items:
        return

    recipe_id = items[0]["id"]
    recipe_response = client.get(f"/api/recipes/{recipe_id}/")
    assert_status_in(recipe_response, {200, 404})

    if recipe_response.status_code == 404:
        return

    recipe_data = get_json(recipe_response)
    author = recipe_data.get("author") or {}

    author_id = author.get("id")
    if not author_id:
        return

    response = client.get(f"/users/{author_id}/collections/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_public_user_comments_for_existing_author_if_any(client):
    list_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(list_response, 200)

    list_data = get_json(list_response)
    items = list_data.get("items", [])

    if not items:
        return

    recipe_id = items[0]["id"]
    recipe_response = client.get(f"/api/recipes/{recipe_id}/")
    assert_status_in(recipe_response, {200, 404})

    if recipe_response.status_code == 404:
        return

    recipe_data = get_json(recipe_response)
    author = recipe_data.get("author") or {}

    author_id = author.get("id")
    if not author_id:
        return

    response = client.get(f"/users/{author_id}/comments/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_public_comments_for_existing_recipe_if_any(client):
    list_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(list_response, 200)

    list_data = get_json(list_response)
    items = list_data.get("items", [])

    if not items:
        return

    recipe_id = items[0]["id"]

    response = client.get(f"/api/recipes/{recipe_id}/comments/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_public_comments_for_missing_recipe(client):
    response = client.get("/api/recipes/999999999/comments/")

    assert_status(response, 404)


def test_protected_collections_without_auth(client):
    response = client.get("/collections/")

    assert_status_in(response, {401, 403})


def test_protected_favorites_without_auth(client):
    response = client.get("/favorites")

    assert_status_in(response, {401, 403})


def test_protected_shopping_cart_without_auth(client):
    response = client.get("/shopping-cart")

    assert_status_in(response, {401, 403})


def test_protected_subscriptions_without_auth(client):
    response = client.get("/subscriptions")

    assert_status_in(response, {401, 403, 404})


def test_create_recipe_without_auth_new_api(client, sample_recipe_payload):
    response = client.post("/recipes", json=sample_recipe_payload)

    assert_status_in(response, {401, 403})


def test_create_comment_without_auth_if_recipe_exists(client):
    list_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(list_response, 200)

    list_data = get_json(list_response)
    items = list_data.get("items", [])

    if not items:
        return

    recipe_id = items[0]["id"]

    response = client.post(
        f"/api/recipes/{recipe_id}/comments/",
        json={"text": "Комментарий без авторизации", "parent_id": None},
    )

    assert_status(response, 401)


def test_public_unknown_route_returns_404(client):
    response = client.get("/definitely-unknown-route-for-pytest")

    assert_status(response, 404)
