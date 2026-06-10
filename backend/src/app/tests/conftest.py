import time
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    """
    Общий тестовый клиент FastAPI.

    Тесты работают через внутренний TestClient, поэтому не требуют запущенного nginx.
    При этом приложение использует те же роуты и зависимости, что и в обычном запуске.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def unique_suffix():
    """
    Уникальный суффикс для тестовых email, username, названий рецептов,
    подборок и других сущностей.
    """
    return f"{int(time.time())}_{uuid4().hex[:10]}"


def assert_status(response, expected_status: int):
    """
    Удобная проверка статуса с выводом тела ответа при ошибке.
    """
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response body: {response.text}"
    )


def assert_status_in(response, expected_statuses: set[int] | tuple[int, ...] | list[int]):
    """
    Проверка, что статус входит в набор допустимых.
    Полезно для endpoint-ов, где корректным может быть 200/201 или 401/403.
    """
    assert response.status_code in expected_statuses, (
        f"Expected status in {expected_statuses}, got {response.status_code}. "
        f"Response body: {response.text}"
    )


def get_json(response):
    """
    Безопасное получение JSON с понятной ошибкой.
    """
    try:
        return response.json()
    except Exception as exc:
        raise AssertionError(
            f"Response is not valid JSON. Status: {response.status_code}. "
            f"Body: {response.text}"
        ) from exc


def make_auth_header(token: str, scheme: str = "Token") -> dict[str, str]:
    """
    Заголовок авторизации.

    В проекте поддерживаются схемы Token и Bearer.
    Для foodgram-совместимых endpoint-ов чаще используется Token.
    """
    return {"Authorization": f"{scheme} {token}"}


def make_bearer_header(token: str) -> dict[str, str]:
    return make_auth_header(token, scheme="Bearer")


def make_token_header(token: str) -> dict[str, str]:
    return make_auth_header(token, scheme="Token")


@pytest.fixture()
def test_user_payload(unique_suffix):
    """
    Базовые данные пользователя для будущих тестов регистрации/авторизации.
    """
    return {
        "email": f"pytest_{unique_suffix}@example.com",
        "username": f"pytest_{unique_suffix}",
        "first_name": "Pytest",
        "last_name": "User",
        "password": "StrongPass12345",
    }


@pytest.fixture()
def second_test_user_payload(unique_suffix):
    """
    Второй пользователь для тестов прав доступа:
    чужой профиль, чужой рецепт, чужой комментарий, подписки.
    """
    return {
        "email": f"pytest_second_{unique_suffix}@example.com",
        "username": f"pytest_second_{unique_suffix}",
        "first_name": "Second",
        "last_name": "User",
        "password": "StrongPass12345",
    }


@pytest.fixture()
def sample_comment_text(unique_suffix):
    return f"Очень вкусный и полезный рецепт, тестовый комментарий {unique_suffix}"


@pytest.fixture()
def sample_collection_payload(unique_suffix):
    return {
        "name": f"Тестовая подборка {unique_suffix}",
        "description": "Подборка создана автоматическим pytest-тестом",
    }


@pytest.fixture()
def sample_recipe_payload():
    """
    Базовая структура рецепта для новых API /recipes.

    В конкретных тестах ingredient_id и tag_ids будут подставляться
    после получения существующих ингредиентов и тегов из БД.
    """
    return {
        "title": "Тестовый овощной салат",
        "description": (
            "Огурцы и помидоры нарезать, добавить соль, масло, зелень "
            "и перемешать до готовности."
        ),
        "cooking_time_minutes": 15,
        "base_servings": 2,
        "tag_ids": [],
        "ingredients": [],
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
