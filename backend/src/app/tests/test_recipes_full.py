from conftest import (
    assert_status,
    assert_status_in,
    get_json,
    make_bearer_header,
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
    assert len(token) > 20

    return token


def get_first_tag_id(client):
    response = client.get("/tags")
    assert_status(response, 200)

    tags = get_json(response)
    assert tags, "Для тестов рецептов нужен хотя бы один тег в БД"

    return tags[0]["id"]


def get_first_ingredient_id(client):
    response = client.get("/ingredients")
    assert_status(response, 200)

    ingredients = get_json(response)
    assert ingredients, "Для тестов рецептов нужен хотя бы один ингредиент в БД"

    return ingredients[0]["id"]


def make_recipe_payload(client, title="Тестовый овощной салат"):
    tag_id = get_first_tag_id(client)
    ingredient_id = get_first_ingredient_id(client)

    return {
        "title": title,
        "description": (
            "Огурцы и помидоры нарезать, добавить соль, масло, зелень "
            "и перемешать до готовности."
        ),
        "cooking_time_minutes": 15,
        "base_servings": 2,
        "tag_ids": [tag_id],
        "ingredients": [
            {
                "ingredient_id": ingredient_id,
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
                "text": "Добавить соль, масло и перемешать.",
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


def test_create_recipe_success(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client, title="Тестовый салат с овощами")

    response = create_recipe(client, token, payload)

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["moderation_status"] in {"approved", "pending", "rejected"}

    assert data["moderation_status"] == "approved"
    assert data["is_published"] is True


def test_create_recipe_without_auth_rejected(client):
    payload = make_recipe_payload(client)

    response = client.post("/recipes", json=payload)

    assert_status_in(response, {401, 403})


def test_create_recipe_empty_title_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client)
    payload["title"] = ""

    response = create_recipe(client, token, payload)

    assert_status(response, 422)


def test_create_recipe_too_short_title_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client)
    payload["title"] = "А"

    response = create_recipe(client, token, payload)

    assert_status(response, 422)


def test_create_recipe_too_long_title_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client)
    payload["title"] = "А" * 121

    response = create_recipe(client, token, payload)

    assert_status(response, 422)


def test_create_recipe_empty_description_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client)
    payload["description"] = ""

    response = create_recipe(client, token, payload)

    assert_status(response, 422)


def test_create_recipe_invalid_cooking_time_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client)
    payload["cooking_time_minutes"] = 0

    response = create_recipe(client, token, payload)

    assert_status(response, 422)


def test_create_recipe_invalid_base_servings_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client)
    payload["base_servings"] = 0

    response = create_recipe(client, token, payload)

    assert_status(response, 422)


def test_create_recipe_invalid_ingredient_amount_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    payload = make_recipe_payload(client)
    payload["ingredients"][0]["amount"] = 0

    response = create_recipe(client, token, payload)

    assert_status(response, 422)


def test_create_recipe_rejected_by_moderation(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    payload = {
        "title": "Цементный раствор",
        "description": "Смешать цемент, бетон и песок. Это строительная смесь, а не еда.",
        "cooking_time_minutes": 15,
        "base_servings": 1,
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
                "text": "Перемешать строительные материалы.",
                "duration_sec": 60,
            }
        ],
    }

    response = create_recipe(client, token, payload)

    assert_status(response, 201)
    data = get_json(response)

    assert data["moderation_status"] == "rejected"
    assert data["is_published"] is False


def test_rejected_recipe_not_available_publicly(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    payload = {
        "title": "Бетонная смесь",
        "description": "Добавить бетон, цемент и песок. Это не кулинарный рецепт.",
        "cooking_time_minutes": 10,
        "base_servings": 1,
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
                "text": "Смешать некулинарные материалы.",
                "duration_sec": 60,
            }
        ],
    }

    create_response = create_recipe(client, token, payload)
    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}")

    assert_status(response, 404)


def test_get_recipe_detail_after_create(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}")

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == recipe_id
    assert data["title"] == "Тестовый овощной салат"
    assert data["description"]
    assert data["cooking_time_minutes"] == 15
    assert data["base_servings"] == 2
    assert data["selected_servings"] == 2
    assert isinstance(data["tags"], list)
    assert isinstance(data["ingredients"], list)
    assert isinstance(data["steps"], list)
    assert "nutrition_total" in data
    assert "nutrition_per_serving" in data


def test_get_recipe_detail_with_servings_scales_ingredients(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}", params={"servings": 4})

    assert_status(response, 200)
    data = get_json(response)

    assert data["selected_servings"] == 4

    if data["ingredients"]:
        ingredient = data["ingredients"][0]
        assert ingredient["amount"] == ingredient["base_amount"] * 2


def test_list_recipes_contains_created_recipe(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get("/recipes", params={"page": 1, "size": 50})

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data["items"], list)
    assert any(item["id"] == recipe_id for item in data["items"])


def test_list_recipes_pagination_fields(client):
    response = client.get("/recipes", params={"page": 1, "size": 6})

    assert_status(response, 200)
    data = get_json(response)

    assert data["page"] == 1
    assert data["size"] == 6
    assert "total" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


def test_list_recipes_invalid_page_rejected(client):
    response = client.get("/recipes", params={"page": 0, "size": 6})

    assert_status(response, 422)


def test_list_recipes_invalid_size_rejected(client):
    response = client.get("/recipes", params={"page": 1, "size": 0})

    assert_status(response, 422)


def test_update_own_recipe_success(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.patch(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(token),
        json={
            "title": "Обновленный овощной салат",
            "description": "Овощи нарезать, добавить масло, соль и перемешать.",
            "cooking_time_minutes": 20,
            "base_servings": 3,
        },
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == recipe_id
    assert data["title"] == "Обновленный овощной салат"
    assert data["cooking_time_minutes"] == 20
    assert data["base_servings"] == 3


def test_update_recipe_without_auth_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.patch(
        f"/recipes/{recipe_id}",
        json={
            "title": "Попытка изменения без авторизации",
        },
    )

    assert_status_in(response, {401, 403})


def test_update_foreign_recipe_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
):
    owner_token = get_bearer_token(client, test_user_payload)
    other_token = get_bearer_token(client, second_test_user_payload)

    create_response = create_recipe(client, owner_token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.patch(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(other_token),
        json={
            "title": "Попытка изменить чужой рецепт",
        },
    )

    assert_status(response, 403)


def test_update_missing_recipe_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    response = client.patch(
        "/recipes/999999999",
        headers=make_bearer_header(token),
        json={
            "title": "Несуществующий рецепт",
        },
    )

    assert_status(response, 404)


def test_delete_own_recipe_success(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.delete(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(token),
    )

    assert_status(response, 204)

    get_response = client.get(f"/recipes/{recipe_id}")

    assert_status(get_response, 404)


def test_delete_recipe_without_auth_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.delete(f"/recipes/{recipe_id}")

    assert_status_in(response, {401, 403})


def test_delete_foreign_recipe_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
):
    owner_token = get_bearer_token(client, test_user_payload)
    other_token = get_bearer_token(client, second_test_user_payload)

    create_response = create_recipe(client, owner_token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.delete(
        f"/recipes/{recipe_id}",
        headers=make_bearer_header(other_token),
    )

    assert_status(response, 403)


def test_delete_missing_recipe_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    response = client.delete(
        "/recipes/999999999",
        headers=make_bearer_header(token),
    )

    assert_status(response, 404)


def test_nutrition_fields_have_expected_shape(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}")

    assert_status(response, 200)
    data = get_json(response)

    for block_name in ("nutrition_total", "nutrition_per_serving"):
        block = data[block_name]

        assert "calories" in block
        assert "protein" in block
        assert "fat" in block
        assert "carbs" in block

        assert isinstance(block["calories"], int | float)
        assert isinstance(block["protein"], int | float)
        assert isinstance(block["fat"], int | float)
        assert isinstance(block["carbs"], int | float)


def test_steps_are_returned_in_recipe_detail(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    create_response = create_recipe(client, token)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}")

    assert_status(response, 200)
    data = get_json(response)

    assert len(data["steps"]) == 2
    assert data["steps"][0]["position"] == 1
    assert data["steps"][1]["position"] == 2


def test_tags_are_returned_in_recipe_detail(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    tag_id = get_first_tag_id(client)

    payload = make_recipe_payload(client)
    payload["tag_ids"] = [tag_id]

    create_response = create_recipe(client, token, payload)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}")

    assert_status(response, 200)
    data = get_json(response)

    assert any(tag["id"] == tag_id for tag in data["tags"])


def test_ingredients_are_returned_in_recipe_detail(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)
    ingredient_id = get_first_ingredient_id(client)

    payload = make_recipe_payload(client)
    payload["ingredients"] = [
        {
            "ingredient_id": ingredient_id,
            "amount": 150,
        }
    ]

    create_response = create_recipe(client, token, payload)

    assert_status(create_response, 201)

    recipe_id = get_json(create_response)["id"]

    response = client.get(f"/recipes/{recipe_id}")

    assert_status(response, 200)
    data = get_json(response)

    assert any(ingredient["id"] == ingredient_id for ingredient in data["ingredients"])