import json
import uuid
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.receipt.schemas import PaymentTypeEnum
from tests.factories import PaymentFactory, ReceiptFactory
from tests.helper import create_user_and_get_token


@pytest.mark.asyncio
async def test__receipt__success__get_public_receipt__with_auth(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    receipt_create_response = await http_client.post("/receipt", headers=headers, json=payload)
    assert receipt_create_response.status_code == HTTPStatus.OK

    # get receipts by filter
    receipt_id = receipt_create_response.json().get("id")

    response = await http_client.get(f"/receipt/{receipt_id}/public", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test__receipt__success__get_public_receipt__without_auth(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    receipt_create_response = await http_client.post("/receipt", headers=headers, json=payload)
    assert receipt_create_response.status_code == HTTPStatus.OK

    # get receipts by filter
    receipt_id = receipt_create_response.json().get("id")

    response = await http_client.get(f"/receipt/{receipt_id}/public")
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test__receipt__success__get_public_receipt__by_public_url(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    receipt_create_response = await http_client.post("/receipt", headers=headers, json=payload)
    assert receipt_create_response.status_code == HTTPStatus.OK

    # get receipts by filter
    receipt_public_url = receipt_create_response.json().get("public_url")

    response = await http_client.get(receipt_public_url)
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.text, str)


@pytest.mark.asyncio
async def test__receipt__fails__receipt_not_found(http_client: AsyncClient):
    response = await http_client.get(f"/receipt/{uuid.uuid4()}/public")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Receipt not found"
