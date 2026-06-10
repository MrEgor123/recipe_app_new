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

    data = get_json(login_response)
    token = data.get("access_token")

    assert token
    assert isinstance(token, str)
    assert len(token) > 20

    return token


def get_existing_recipe_id(client):
    response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(response, 200)

    data = get_json(response)
    items = data.get("items", [])

    assert items, "Для тестов подборок нужен хотя бы один опубликованный рецепт"

    return items[0]["id"]


def create_collection(client, token: str, name: str, description: str | None = None):
    return client.post(
        "/collections/",
        headers=make_bearer_header(token),
        json={
            "name": name,
            "description": description,
        },
    )


def test_create_collection_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    response = create_collection(
        client,
        token=token,
        name=f"Тестовая подборка {unique_suffix}",
        description="Описание тестовой подборки",
    )

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["name"].startswith("Тестовая подборка")
    assert data["description"] == "Описание тестовой подборки"
    assert data["recipes_count"] == 0
    assert data["is_owner"] is True
    assert "user_id" in data
    assert "created_at" in data


def test_create_collection_without_auth_rejected(client, unique_suffix):
    response = client.post(
        "/collections/",
        json={
            "name": f"Подборка без авторизации {unique_suffix}",
            "description": "Описание",
        },
    )

    assert_status_in(response, {401, 403})


def test_create_collection_empty_name_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    response = create_collection(
        client,
        token=token,
        name="",
        description="Описание",
    )

    assert_status(response, 422)


def test_create_collection_too_long_name_rejected(client, test_user_payload):
    token = get_bearer_token(client, test_user_payload)

    response = create_collection(
        client,
        token=token,
        name="А" * 101,
        description="Описание",
    )

    assert_status(response, 422)


def test_create_collection_too_long_description_rejected(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    response = create_collection(
        client,
        token=token,
        name=f"Подборка с длинным описанием {unique_suffix}",
        description="А" * 501,
    )

    assert_status(response, 422)


def test_get_my_collections_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Моя подборка {unique_suffix}",
        description="Описание моей подборки",
    )
    assert_status(create_response, 201)

    response = client.get(
        "/collections/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)
    assert any(item["id"] == get_json(create_response)["id"] for item in data)


def test_get_my_collections_without_auth_rejected(client):
    response = client.get("/collections/")

    assert_status_in(response, {401, 403})


def test_get_collection_by_id_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Открытие подборки {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.get(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == collection_id
    assert data["is_owner"] is True


def test_get_collection_by_id_without_auth_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Публичная подборка {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.get(f"/collections/{collection_id}/")

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == collection_id
    assert data["is_owner"] is False


def test_get_missing_collection_rejected(client):
    response = client.get("/collections/999999999/")

    assert_status(response, 404)


def test_update_collection_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка до изменения {unique_suffix}",
        description="Старое описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.patch(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(token),
        json={
            "name": f"Подборка после изменения {unique_suffix}",
            "description": "Новое описание",
        },
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == collection_id
    assert data["name"].startswith("Подборка после изменения")
    assert data["description"] == "Новое описание"
    assert data["is_owner"] is True


def test_update_collection_without_auth_rejected(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка для проверки auth {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.patch(
        f"/collections/{collection_id}/",
        json={
            "name": "Попытка изменения без авторизации",
            "description": "Описание",
        },
    )

    assert_status_in(response, {401, 403})


def test_update_foreign_collection_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    owner_token = get_bearer_token(client, test_user_payload)
    other_token = get_bearer_token(client, second_test_user_payload)

    create_response = create_collection(
        client,
        token=owner_token,
        name=f"Чужая подборка {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.patch(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(other_token),
        json={
            "name": "Попытка изменить чужую подборку",
            "description": "Описание",
        },
    )

    assert_status(response, 404)


def test_delete_collection_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка для удаления {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.delete(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 204)

    get_response = client.get(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(token),
    )

    assert_status(get_response, 404)


def test_delete_collection_without_auth_rejected(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка удалить без auth {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.delete(f"/collections/{collection_id}/")

    assert_status_in(response, {401, 403})


def test_delete_foreign_collection_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    owner_token = get_bearer_token(client, test_user_payload)
    other_token = get_bearer_token(client, second_test_user_payload)

    create_response = create_collection(
        client,
        token=owner_token,
        name=f"Чужая подборка для удаления {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.delete(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(other_token),
    )

    assert_status(response, 404)


def test_get_collection_recipes_empty_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    create_response = create_collection(
        client,
        token=token,
        name=f"Пустая подборка {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.get(
        f"/collections/{collection_id}/recipes/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)
    assert data == []


def test_add_recipe_to_collection_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка с рецептом {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 201)
    data = get_json(response)

    assert "detail" in data


def test_add_duplicate_recipe_to_collection_rejected(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка с дублем {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    first_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(first_response, 201)

    second_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )

    assert_status(second_response, 400)


def test_add_recipe_to_collection_without_auth_rejected(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка добавление без auth {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.post(f"/collections/{collection_id}/recipes/{recipe_id}/")

    assert_status_in(response, {401, 403})


def test_add_recipe_to_foreign_collection_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    owner_token = get_bearer_token(client, test_user_payload)
    other_token = get_bearer_token(client, second_test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=owner_token,
        name=f"Чужая подборка для рецепта {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(other_token),
    )

    assert_status(response, 404)


def test_get_collection_recipes_after_add(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка список рецептов {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    add_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(add_response, 201)

    response = client.get(
        f"/collections/{collection_id}/recipes/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)
    assert any(item["id"] == recipe_id for item in data)


def test_collection_recipes_count_after_add(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка count {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    add_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(add_response, 201)

    response = client.get(
        f"/collections/{collection_id}/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["recipes_count"] >= 1


def test_remove_recipe_from_collection_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка удалить рецепт {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    add_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(add_response, 201)

    response = client.delete(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )

    assert_status(response, 204)

    recipes_response = client.get(
        f"/collections/{collection_id}/recipes/",
        headers=make_bearer_header(token),
    )

    assert_status(recipes_response, 200)
    recipes = get_json(recipes_response)

    assert all(item["id"] != recipe_id for item in recipes)


def test_remove_recipe_from_collection_without_auth_rejected(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=token,
        name=f"Подборка удалить рецепт без auth {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    add_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(token),
    )
    assert_status(add_response, 201)

    response = client.delete(f"/collections/{collection_id}/recipes/{recipe_id}/")

    assert_status_in(response, {401, 403})


def test_remove_recipe_from_foreign_collection_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    owner_token = get_bearer_token(client, test_user_payload)
    other_token = get_bearer_token(client, second_test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_collection(
        client,
        token=owner_token,
        name=f"Чужая подборка удалить рецепт {unique_suffix}",
        description="Описание",
    )
    assert_status(create_response, 201)

    collection_id = get_json(create_response)["id"]

    add_response = client.post(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(owner_token),
    )
    assert_status(add_response, 201)

    response = client.delete(
        f"/collections/{collection_id}/recipes/{recipe_id}/",
        headers=make_bearer_header(other_token),
    )

    assert_status(response, 404)


def test_recipe_collections_get_and_update_success(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    first_collection_response = create_collection(
        client,
        token=token,
        name=f"Подборка recipe update 1 {unique_suffix}",
        description="Описание",
    )
    assert_status(first_collection_response, 201)

    second_collection_response = create_collection(
        client,
        token=token,
        name=f"Подборка recipe update 2 {unique_suffix}",
        description="Описание",
    )
    assert_status(second_collection_response, 201)

    first_id = get_json(first_collection_response)["id"]
    second_id = get_json(second_collection_response)["id"]

    update_response = client.put(
        f"/recipes/{recipe_id}/collections/",
        headers=make_bearer_header(token),
        json={"collection_ids": [first_id, second_id]},
    )

    assert_status_in(update_response, {200, 201})
    update_data = get_json(update_response)

    assert sorted(update_data["collection_ids"]) == sorted([first_id, second_id])

    get_response = client.get(
        f"/recipes/{recipe_id}/collections/",
        headers=make_bearer_header(token),
    )

    assert_status(get_response, 200)
    get_data = get_json(get_response)

    assert sorted(get_data["collection_ids"]) == sorted([first_id, second_id])


def test_recipe_collections_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.get(f"/recipes/{recipe_id}/collections/")

    assert_status_in(response, {401, 403})


def test_create_duplicate_collection_name_rejected(client, test_user_payload, unique_suffix):
    token = get_bearer_token(client, test_user_payload)

    name = f"Одинаковая подборка {unique_suffix}"

    first_response = create_collection(
        client,
        token=token,
        name=name,
        description="Описание",
    )
    assert_status(first_response, 201)

    second_response = create_collection(
        client,
        token=token,
        name=name,
        description="Описание",
    )

    assert_status(second_response, 400)


def test_different_users_can_have_same_collection_name(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    first_token = get_bearer_token(client, test_user_payload)
    second_token = get_bearer_token(client, second_test_user_payload)

    name = f"Общая по названию подборка {unique_suffix}"

    first_response = create_collection(
        client,
        token=first_token,
        name=name,
        description="Описание",
    )
    assert_status(first_response, 201)

    second_response = create_collection(
        client,
        token=second_token,
        name=name,
        description="Описание",
    )

    assert_status(second_response, 201)