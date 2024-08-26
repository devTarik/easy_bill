from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__user_register__success(http_client: AsyncClient):
    payload = {
        "full_name": "test_full_name",
        "username": "test_username",
        "password": "test_password",
    }
    response = await http_client.post("/user/registry", json=payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json().get("access_token")
    assert response.json().get("refresh_token")
    assert response.json().get("token_type")


@pytest.mark.asyncio
async def test__user_register__failed__user_exist(http_client: AsyncClient):
    payload = {
        "full_name": "test_full_name",
        "username": "test_username",
        "password": "test_password",
    }
    response = await http_client.post("/user/registry", json=payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json().get("access_token")
    assert response.json().get("refresh_token")
    assert response.json().get("token_type")

    response = await http_client.post("/user/registry", json=payload)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["detail"] == "Username already registered"
