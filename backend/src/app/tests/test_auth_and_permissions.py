from conftest import (
    assert_status,
    assert_status_in,
    get_json,
    make_token_header,
    make_bearer_header,
)


def register_user_foodgram(client, payload):
    response = client.post(
        "/api/users/",
        json={
            "email": payload["email"],
            "username": payload["username"],
            "first_name": payload["first_name"],
            "last_name": payload["last_name"],
            "password": payload["password"],
        },
    )
    return response


def login_user_foodgram(client, email: str, password: str):
    response = client.post(
        "/api/auth/token/login/",
        json={
            "email": email,
            "password": password,
        },
    )
    return response


def get_auth_token(client, payload):
    register_response = register_user_foodgram(client, payload)
    assert_status_in(register_response, {201, 400})

    login_response = login_user_foodgram(
        client,
        email=payload["email"],
        password=payload["password"],
    )
    assert_status(login_response, 200)

    data = get_json(login_response)
    token = data.get("auth_token")

    assert token
    assert isinstance(token, str)
    assert len(token) > 20

    return token


def test_register_user_foodgram_success(client, test_user_payload):
    response = register_user_foodgram(client, test_user_payload)

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["email"] == test_user_payload["email"]
    assert data["username"] == test_user_payload["username"]
    assert data["first_name"] == test_user_payload["first_name"]
    assert data["last_name"] == test_user_payload["last_name"]
    assert "password" not in data


def test_register_duplicate_email_or_username_rejected(client, test_user_payload):
    first_response = register_user_foodgram(client, test_user_payload)
    assert_status(first_response, 201)

    second_response = register_user_foodgram(client, test_user_payload)
    assert_status_in(second_response, {400, 409})


def test_login_foodgram_success(client, test_user_payload):
    register_response = register_user_foodgram(client, test_user_payload)
    assert_status(register_response, 201)

    login_response = login_user_foodgram(
        client,
        email=test_user_payload["email"],
        password=test_user_payload["password"],
    )

    assert_status(login_response, 200)
    data = get_json(login_response)

    assert "auth_token" in data
    assert isinstance(data["auth_token"], str)
    assert len(data["auth_token"]) > 20


def test_login_foodgram_wrong_password_rejected(client, test_user_payload):
    register_response = register_user_foodgram(client, test_user_payload)
    assert_status(register_response, 201)

    response = login_user_foodgram(
        client,
        email=test_user_payload["email"],
        password="WrongPassword12345",
    )

    assert_status_in(response, {400, 401})


def test_login_foodgram_unknown_email_rejected(client, unique_suffix):
    response = login_user_foodgram(
        client,
        email=f"unknown_{unique_suffix}@example.com",
        password="StrongPass12345",
    )

    assert_status_in(response, {400, 401})


def test_get_current_user_foodgram_with_token(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.get(
        "/api/users/me/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert data["email"] == test_user_payload["email"]
    assert data["username"] == test_user_payload["username"]


def test_get_current_user_foodgram_without_token_rejected(client):
    response = client.get("/api/users/me/")

    assert_status(response, 401)


def test_get_current_user_foodgram_with_invalid_token_rejected(client):
    response = client.get(
        "/api/users/me/",
        headers=make_token_header("invalid-token-value"),
    )

    assert_status(response, 401)


def test_logout_foodgram_with_token(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    response = client.post(
        "/api/auth/token/logout/",
        headers=make_token_header(token),
    )

    assert_status_in(response, {204, 200})


def test_logout_foodgram_without_token_is_idempotent(client):
    response = client.post("/api/auth/token/logout/")

    assert_status_in(response, {200, 204, 401})

def test_new_api_register_success(client, unique_suffix):
    payload = {
        "email": f"newapi_{unique_suffix}@example.com",
        "username": f"newapi_{unique_suffix}",
        "password": "StrongPass12345",
    }

    response = client.post("/auth/register", json=payload)

    assert_status(response, 201)
    data = get_json(response)

    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "password" not in data


def test_new_api_register_short_password_rejected(client, unique_suffix):
    payload = {
        "email": f"shortpass_{unique_suffix}@example.com",
        "username": f"shortpass_{unique_suffix}",
        "password": "123",
    }

    response = client.post("/auth/register", json=payload)

    assert_status(response, 422)


def test_new_api_login_success(client, unique_suffix):
    payload = {
        "email": f"newlogin_{unique_suffix}@example.com",
        "username": f"newlogin_{unique_suffix}",
        "password": "StrongPass12345",
    }

    register_response = client.post("/auth/register", json=payload)
    assert_status(register_response, 201)

    login_response = client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )

    assert_status(login_response, 200)
    data = get_json(login_response)

    assert "access_token" in data
    assert "refresh_token" in data
    assert data.get("token_type") == "bearer"


def test_new_api_login_wrong_password_rejected(client, unique_suffix):
    payload = {
        "email": f"newwrong_{unique_suffix}@example.com",
        "username": f"newwrong_{unique_suffix}",
        "password": "StrongPass12345",
    }

    register_response = client.post("/auth/register", json=payload)
    assert_status(register_response, 201)

    response = client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": "WrongPassword12345",
        },
    )

    assert_status_in(response, {400, 401})


def test_new_api_refresh_success(client, unique_suffix):
    payload = {
        "email": f"refresh_{unique_suffix}@example.com",
        "username": f"refresh_{unique_suffix}",
        "password": "StrongPass12345",
    }

    register_response = client.post("/auth/register", json=payload)
    assert_status(register_response, 201)

    login_response = client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )
    assert_status(login_response, 200)

    login_data = get_json(login_response)
    refresh_token = login_data["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert_status(response, 200)
    data = get_json(response)

    assert "access_token" in data
    assert "refresh_token" in data
    assert data.get("token_type") == "bearer"


def test_new_api_refresh_invalid_token_rejected(client):
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid-refresh-token"},
    )

    assert_status(response, 401)


def test_bearer_token_works_for_new_api_protected_endpoint(client, unique_suffix):
    payload = {
        "email": f"bearer_{unique_suffix}@example.com",
        "username": f"bearer_{unique_suffix}",
        "password": "StrongPass12345",
    }

    register_response = client.post("/auth/register", json=payload)
    assert_status(register_response, 201)

    login_response = client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )
    assert_status(login_response, 200)

    access_token = get_json(login_response)["access_token"]

    response = client.get(
        "/collections/",
        headers=make_bearer_header(access_token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_token_scheme_works_for_comments_endpoint_if_recipe_exists(client, test_user_payload):
    token = get_auth_token(client, test_user_payload)

    recipes_response = client.get("/recipes", params={"page": 1, "size": 1})
    assert_status(recipes_response, 200)

    recipes = get_json(recipes_response).get("items", [])
    if not recipes:
        return

    recipe_id = recipes[0]["id"]

    response = client.get(
        f"/api/recipes/{recipe_id}/comments/",
        headers=make_token_header(token),
    )

    assert_status(response, 200)
    data = get_json(response)

    assert isinstance(data, list)


def test_protected_endpoint_with_invalid_bearer_token_rejected(client):
    response = client.get(
        "/collections/",
        headers=make_bearer_header("invalid-token-value"),
    )

    assert_status(response, 401)


def test_protected_endpoint_with_invalid_token_scheme_rejected(client):
    response = client.get(
        "/api/users/me/",
        headers={"Authorization": "Basic invalid-token-value"},
    )

    assert_status(response, 401)


def test_set_password_without_auth_rejected(client):
    response = client.post(
        "/api/users/set_password/",
        json={
            "new_password": "NewStrongPass12345",
            "current_password": "StrongPass12345",
        },
    )

    assert_status(response, 401)


def test_reset_password_endpoint_available(client):
    response = client.post(
        "/api/users/reset_password/",
        json={"email": "nobody@example.com"},
    )

    assert_status_in(response, {204, 200, 400, 404, 422})