import time

from conftest import assert_status, assert_status_in, get_json, make_token_header


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

    assert items, "Для тестов комментариев нужен хотя бы один опубликованный рецепт"

    return items[0]["id"]


def create_comment(client, recipe_id: int, token: str, text: str, parent_id=None):
    return client.post(
        f"/api/recipes/{recipe_id}/comments/",
        headers=make_token_header(token),
        json={
            "text": text,
            "parent_id": parent_id,
        },
    )


def test_create_comment_success(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Очень вкусный рецепт, спасибо за подробное описание {unique_suffix}",
    )

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["text"].startswith("Очень вкусный рецепт")
    assert data["parent_id"] is None
    assert data["likes_count"] == 0
    assert data["is_liked"] is False
    assert "author" in data
    assert data["author"]["email"] if "email" in data["author"] else True


def test_list_comments_for_recipe(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    create_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий для проверки списка {unique_suffix}",
    )
    assert_status(create_response, 201)

    response = client.get(f"/api/recipes/{recipe_id}/comments/")

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)
    assert any(item["id"] == get_json(create_response)["id"] for item in data)


def test_create_comment_without_auth_rejected(client):
    recipe_id = get_existing_recipe_id(client)

    response = client.post(
        f"/api/recipes/{recipe_id}/comments/",
        json={
            "text": "Комментарий без авторизации",
            "parent_id": None,
        },
    )

    assert_status(response, 401)


def test_create_comment_for_missing_recipe_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = create_comment(
        client,
        recipe_id=999999999,
        token=token,
        text="Нормальный комментарий к несуществующему рецепту",
    )

    assert_status(response, 404)


def test_create_empty_comment_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="   ",
    )

    assert_status(response, 400)


def test_create_too_long_comment_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="а" * 2001,
    )

    assert_status(response, 422)


def test_comment_moderation_blocks_advertising(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Очень вкусно, переходите в t.me/testchannel за лучшими рецептами",
    )

    assert_status(response, 400)


def test_comment_moderation_blocks_garbage(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="аааааааааааааааааааааааааааааа",
    )

    assert_status(response, 400)


def test_comment_antispam_fast_repeat_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    first_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Очень вкусный рецепт спасибо автору за понятное описание",
    )
    assert_status(first_response, 201)

    second_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text="Спасибо за рецепт получилось вкусно и достаточно просто",
    )

    assert_status(second_response, 429)


def test_create_reply_success(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    parent_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Родительский комментарий для ответа {unique_suffix}",
    )
    assert_status(parent_response, 201)

    parent_id = get_json(parent_response)["id"]

    time.sleep(16)

    reply_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Ответ на комментарий, рецепт действительно хороший {unique_suffix}",
        parent_id=parent_id,
    )

    assert_status(reply_response, 201)
    reply_data = get_json(reply_response)

    assert reply_data["parent_id"] == parent_id


def test_create_reply_to_missing_parent_rejected(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Ответ на несуществующий комментарий {unique_suffix}",
        parent_id=999999999,
    )

    assert_status(response, 404)


def test_comments_tree_contains_reply(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    parent_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий с будущим ответом {unique_suffix}",
    )
    assert_status(parent_response, 201)

    parent_id = get_json(parent_response)["id"]

    time.sleep(16)

    reply_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Тестовый ответ в дереве комментариев {unique_suffix}",
        parent_id=parent_id,
    )
    assert_status(reply_response, 201)

    response = client.get(f"/api/recipes/{recipe_id}/comments/")
    assert_status(response, 200)

    comments = get_json(response)

    parent = next((item for item in comments if item["id"] == parent_id), None)

    assert parent is not None
    assert "replies" in parent
    assert any(reply["id"] == get_json(reply_response)["id"] for reply in parent["replies"])


def test_like_comment_success(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий для лайка {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.post(
        f"/api/comments/{comment_id}/like/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == comment_id
    assert data["is_liked"] is True
    assert data["likes_count"] >= 1


def test_unlike_comment_success(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий для удаления лайка {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    like_response = client.post(
        f"/api/comments/{comment_id}/like/",
        headers=make_token_header(token),
    )
    assert_status(like_response, 200)

    unlike_response = client.delete(
        f"/api/comments/{comment_id}/like/",
        headers=make_token_header(token),
    )

    assert_status(unlike_response, 200)
    data = get_json(unlike_response)

    assert data["id"] == comment_id
    assert data["is_liked"] is False


def test_like_comment_without_auth_rejected(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий для проверки лайка без авторизации {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.post(f"/api/comments/{comment_id}/like/")

    assert_status(response, 401)


def test_like_missing_comment_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.post(
        "/api/comments/999999999/like/",
        headers=make_token_header(token),
    )

    assert_status(response, 404)


def test_update_own_comment_success(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий до редактирования {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.patch(
        f"/api/comments/{comment_id}/",
        headers=make_token_header(token),
        json={"text": f"Комментарий после редактирования {unique_suffix}"},
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["id"] == comment_id
    assert data["text"].startswith("Комментарий после редактирования")


def test_update_comment_with_bad_text_rejected(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий перед плохим редактированием {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.patch(
        f"/api/comments/{comment_id}/",
        headers=make_token_header(token),
        json={"text": "аааааааааааааааааааааааааааааа"},
    )

    assert_status(response, 400)


def test_update_comment_without_auth_rejected(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий для проверки редактирования без авторизации {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.patch(
        f"/api/comments/{comment_id}/",
        json={"text": "Попытка редактирования без авторизации"},
    )

    assert_status(response, 401)


def test_update_foreign_comment_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    owner_token = get_auth_token(client, test_user_payload)
    other_token = get_auth_token(client, second_test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=owner_token,
        text=f"Чужой комментарий для проверки прав {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.patch(
        f"/api/comments/{comment_id}/",
        headers=make_token_header(other_token),
        json={"text": "Попытка изменить чужой комментарий"},
    )

    assert_status(response, 403)


def test_delete_own_comment_success(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий для удаления {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.delete(
        f"/api/comments/{comment_id}/",
        headers=make_token_header(token),
    )

    assert_status(response, 204)


def test_delete_comment_without_auth_rejected(client, test_user_payload, unique_suffix):
    token = get_auth_token(client, test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=token,
        text=f"Комментарий для удаления без авторизации {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.delete(f"/api/comments/{comment_id}/")

    assert_status(response, 401)


def test_delete_foreign_comment_rejected(
    client,
    test_user_payload,
    second_test_user_payload,
    unique_suffix,
):
    owner_token = get_auth_token(client, test_user_payload)
    other_token = get_auth_token(client, second_test_user_payload)
    recipe_id = get_existing_recipe_id(client)

    comment_response = create_comment(
        client,
        recipe_id=recipe_id,
        token=owner_token,
        text=f"Чужой комментарий для удаления {unique_suffix}",
    )
    assert_status(comment_response, 201)

    comment_id = get_json(comment_response)["id"]

    response = client.delete(
        f"/api/comments/{comment_id}/",
        headers=make_token_header(other_token),
    )

    assert_status(response, 403)


def test_delete_missing_comment_rejected(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.delete(
        "/api/comments/999999999/",
        headers=make_token_header(token),
    )

    assert_status(response, 404)