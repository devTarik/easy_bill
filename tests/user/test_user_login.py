from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.helper import create_user_and_get_token


@pytest.mark.asyncio
async def test__user_login__success(http_client: AsyncClient):
    await create_user_and_get_token(http_client)

    payload = {
        "username": "test_username",
        "password": "test_password",
    }
    response = await http_client.post("/user/token", json=payload)
    assert response.status_code == HTTPStatus.OK
    access_token = response.json().get("access_token")
    token_type = response.json().get("token_type")

    headers = {
        "Authorization": f"{token_type} {access_token}",
    }
    response = await http_client.get("/user/me", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json().get("full_name") == "test_full_name"


@pytest.mark.asyncio
async def test__user_login__failed__invalid_password(http_client: AsyncClient):
    await create_user_and_get_token(http_client)

    payload = {
        "username": "test_username",
        "password": "fake_test_password",
    }
    response = await http_client.post("/user/token", json=payload)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test__user_login__failed__invalid_username(http_client: AsyncClient):
    await create_user_and_get_token(http_client)

    payload = {
        "username": "fake_test_username",
        "password": "test_password",
    }
    response = await http_client.post("/user/token", json=payload)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test__user_login__failed__invalid_token(http_client: AsyncClient):
    await create_user_and_get_token(http_client)

    headers = {
        "Authorization": "Bearer fake123token",
    }
    response = await http_client.get("/user/me", headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token"
