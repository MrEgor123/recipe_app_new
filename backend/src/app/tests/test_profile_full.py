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


def get_current_user_foodgram(client, token: str):
    response = client.get(
        "/api/users/me/",
        headers=make_token_header(token),
    )
    assert_status(response, 200)
    return get_json(response)


def get_existing_recipe_author_id(client):
    response = client.get("/api/recipes/", params={"page": 1, "limit": 1})
    assert_status(response, 200)

    data = get_json(response)
    results = data.get("results") or data.get("items") or []

    assert results, "Для тестов профиля нужен хотя бы один опубликованный рецепт"

    author = results[0].get("author") or {}
    author_id = author.get("id")

    assert author_id, "У рецепта должен быть автор"

    return author_id


def test_get_my_profile_success(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)

    response = client.get(
        "/users/me/profile/",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert "id" in data
    assert data["email"] == test_user_payload["email"]
    assert data["username"] == test_user_payload["username"]
    assert data["is_owner"] is True
    assert "stats" in data
    assert "recipes" in data


def test_get_my_profile_without_auth_rejected(client):
    response = client.get("/users/me/profile/")

    assert_status_in(response, {401, 403})


def test_update_my_profile_success(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)

    response = client.patch(
        "/users/me/profile/",
        headers=make_bearer_header(bearer_token),
        json={
            "status": "Готовлю и тестирую рецепты",
            "bio": "Профиль обновлен автоматическим pytest-тестом.",
            "cover_image": "/media/test-cover.jpg",
        },
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["status"] == "Готовлю и тестирую рецепты"
    assert data["bio"] == "Профиль обновлен автоматическим pytest-тестом."
    assert data["cover_image"].endswith("/media/test-cover.jpg")


def test_update_my_profile_without_auth_rejected(client):
    response = client.patch(
        "/users/me/profile/",
        json={
            "status": "Без авторизации",
            "bio": "Попытка обновления без авторизации",
        },
    )

    assert_status_in(response, {401, 403})


def test_update_my_profile_too_long_status_rejected(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)

    response = client.patch(
        "/users/me/profile/",
        headers=make_bearer_header(bearer_token),
        json={
            "status": "А" * 121,
        },
    )

    assert_status(response, 422)


def test_update_my_profile_too_long_bio_rejected(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)

    response = client.patch(
        "/users/me/profile/",
        headers=make_bearer_header(bearer_token),
        json={
            "bio": "А" * 2001,
        },
    )

    assert_status(response, 422)


def test_get_user_profile_public_success(client):
    author_id = get_existing_recipe_author_id(client)

    response = client.get(f"/users/{author_id}/profile/")

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == author_id
    assert "username" in data
    assert "stats" in data
    assert "recipes" in data
    assert data["is_owner"] is False


def test_get_user_profile_with_auth_success(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    author_id = get_existing_recipe_author_id(client)

    response = client.get(
        f"/users/{author_id}/profile/",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == author_id
    assert "is_subscribed" in data
    assert "is_owner" in data
    assert "stats" in data


def test_get_missing_user_profile_rejected(client):
    response = client.get("/users/999999999/profile/")

    assert_status(response, 404)


def test_get_my_profile_collections_success(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)

    response = client.get(
        "/users/me/collections/",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_get_my_profile_collections_without_auth_rejected(client):
    response = client.get("/users/me/collections/")

    assert_status_in(response, {401, 403})


def test_get_user_profile_collections_public_success(client):
    author_id = get_existing_recipe_author_id(client)

    response = client.get(f"/users/{author_id}/collections/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_get_missing_user_profile_collections_rejected(client):
    response = client.get("/users/999999999/collections/")

    assert_status(response, 404)


def test_get_my_profile_comments_success(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)

    response = client.get(
        "/users/me/comments/",
        headers=make_bearer_header(bearer_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_get_my_profile_comments_without_auth_rejected(client):
    response = client.get("/users/me/comments/")

    assert_status_in(response, {401, 403})


def test_get_user_profile_comments_public_success(client):
    author_id = get_existing_recipe_author_id(client)

    response = client.get(f"/users/{author_id}/comments/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_get_missing_user_profile_comments_rejected(client):
    response = client.get("/users/999999999/comments/")

    assert_status(response, 404)


def test_foodgram_get_current_user_success(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)

    response = client.get(
        "/api/users/me/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["email"] == test_user_payload["email"]
    assert data["username"] == test_user_payload["username"]


def test_foodgram_get_current_user_without_auth_rejected(client):
    response = client.get("/api/users/me/")

    assert_status(response, 401)


def test_foodgram_get_user_by_id_success(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)
    current_user = get_current_user_foodgram(client, token)

    response = client.get(
        f"/api/users/{current_user['id']}/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == current_user["id"]
    assert data["email"] == test_user_payload["email"]


def test_foodgram_get_missing_user_by_id_rejected(client):
    response = client.get("/api/users/999999999/")

    assert_status(response, 404)


def test_foodgram_get_users_list_success(client):
    response = client.get("/api/users/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, dict)
    assert "results" in data or "items" in data or "count" in data


def test_foodgram_set_password_without_auth_rejected(client):
    response = client.post(
        "/api/users/set_password/",
        json={
            "current_password": "StrongPass12345",
            "new_password": "NewStrongPass12345",
        },
    )

    assert_status(response, 401)


def test_foodgram_set_password_success(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)

    response = client.post(
        "/api/users/set_password/",
        headers=make_token_header(token),
        json={
            "current_password": test_user_payload["password"],
            "new_password": "NewStrongPass12345",
        },
    )

    assert_status(response, 204)


def test_foodgram_set_password_wrong_current_password_rejected(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)

    response = client.post(
        "/api/users/set_password/",
        headers=make_token_header(token),
        json={
            "current_password": "WrongPassword12345",
            "new_password": "NewStrongPass12345",
        },
    )

    assert_status_in(response, {400, 401})


def test_foodgram_set_avatar_without_auth_rejected(client):
    response = client.put(
        "/api/users/me/avatar/",
        json={"avatar": "data:image/png;base64,AAAA"},
    )

    assert_status(response, 401)


def test_foodgram_set_avatar_success_or_validation_error(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)

    response = client.put(
        "/api/users/me/avatar/",
        headers=make_token_header(token),
        json={"avatar": "data:image/png;base64,AAAA"},
    )

    assert_status_in(response, {200, 400, 422})


def test_foodgram_delete_avatar_without_auth_rejected(client):
    response = client.delete("/api/users/me/avatar/")

    assert_status(response, 401)


def test_foodgram_delete_avatar_success(client, test_user_payload):
    token = get_token_auth(client, test_user_payload)

    response = client.delete(
        "/api/users/me/avatar/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_report_user_success(client, test_user_payload, second_test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    second_token = get_token_auth(client, second_test_user_payload)
    target_user = get_current_user_foodgram(client, second_token)

    response = client.post(
        f"/users/{target_user['id']}/report/",
        headers=make_bearer_header(bearer_token),
        json={
            "reason": "Некорректное поведение",
            "comment": "Жалоба создана автоматическим pytest-тестом.",
        },
    )

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["reason"] == "Некорректное поведение"
    assert data["status"]


def test_report_user_without_auth_rejected(client, second_test_user_payload):
    second_token = get_token_auth(client, second_test_user_payload)
    target_user = get_current_user_foodgram(client, second_token)

    response = client.post(
        f"/users/{target_user['id']}/report/",
        json={
            "reason": "Некорректное поведение",
            "comment": "Жалоба без авторизации.",
        },
    )

    assert_status_in(response, {401, 403})


def test_report_missing_user_rejected(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)

    response = client.post(
        "/users/999999999/report/",
        headers=make_bearer_header(bearer_token),
        json={
            "reason": "Некорректное поведение",
            "comment": "Жалоба на несуществующего пользователя.",
        },
    )

    assert_status(response, 404)


def test_report_self_rejected(client, test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    token = get_token_auth(client, test_user_payload)
    current_user = get_current_user_foodgram(client, token)

    response = client.post(
        f"/users/{current_user['id']}/report/",
        headers=make_bearer_header(bearer_token),
        json={
            "reason": "Саможалоба",
            "comment": "Нельзя жаловаться на себя.",
        },
    )

    assert_status(response, 400)


def test_report_user_duplicate_rejected(client, test_user_payload, second_test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    second_token = get_token_auth(client, second_test_user_payload)
    target_user = get_current_user_foodgram(client, second_token)

    first_response = client.post(
        f"/users/{target_user['id']}/report/",
        headers=make_bearer_header(bearer_token),
        json={
            "reason": "Некорректное поведение",
            "comment": "Первая жалоба.",
        },
    )
    assert_status(first_response, 201)

    second_response = client.post(
        f"/users/{target_user['id']}/report/",
        headers=make_bearer_header(bearer_token),
        json={
            "reason": "Некорректное поведение",
            "comment": "Повторная жалоба.",
        },
    )

    assert_status(second_response, 400)


def test_report_user_short_reason_rejected(client, test_user_payload, second_test_user_payload):
    bearer_token = get_bearer_token(client, test_user_payload)
    second_token = get_token_auth(client, second_test_user_payload)
    target_user = get_current_user_foodgram(client, second_token)

    response = client.post(
        f"/users/{target_user['id']}/report/",
        headers=make_bearer_header(bearer_token),
        json={
            "reason": "а",
            "comment": "Слишком короткая причина.",
        },
    )

    assert_status(response, 422)