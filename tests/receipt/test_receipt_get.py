import json
import uuid
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.receipt.schemas import PaymentTypeEnum
from tests.factories import PaymentFactory, ReceiptFactory
from tests.helper import create_user_and_get_token


@pytest.mark.asyncio
async def test__receipt__success__get_receipts(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    # create receipt with cash
    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # create receipt with card
    payment = PaymentFactory(type=PaymentTypeEnum.CARD.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # get receipts by filter
    response = await http_client.get("/receipt", headers=headers)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert len(response_json) == 2


@pytest.mark.asyncio
async def test__receipt__success__get_single_receipt(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    # create receipt with cash
    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response_1 = await http_client.post("/receipt", headers=headers, json=payload)
    assert response_1.status_code == HTTPStatus.OK

    # create receipt with card
    payment = PaymentFactory(type=PaymentTypeEnum.CARD.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response_2 = await http_client.post("/receipt", headers=headers, json=payload)
    assert response_2.status_code == HTTPStatus.OK

    # get receipts by filter
    receipt_id = response_1.json().get("id")
    response = await http_client.get(f"/receipt/{receipt_id}", headers=headers)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_1.json()["id"] == response_json["id"]
    assert response_1.json()["total"] == response_json["total"]


@pytest.mark.asyncio
async def test__receipt__fails__receipt_not_found(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    response = await http_client.get(f"/receipt/{uuid.uuid4()}", headers=headers)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test__receipt__fails__not_authenticated(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": f"{token}fake",
    }

    response = await http_client.get("/receipt/5", headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test__receipt__success__get_receipts_by_payment_type(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    # create receipt with cash
    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # create receipt with card
    payment = PaymentFactory(type=PaymentTypeEnum.CARD.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # get receipts by filter
    params = {
        "payment_type": PaymentTypeEnum.CASH.value,
    }
    response = await http_client.get("/receipt", headers=headers, params=params)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["payment"]["type"] == PaymentTypeEnum.CASH.value


@pytest.mark.asyncio
async def test__receipt__success__get_receipts_by_total_amount(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    # create receipt with cash
    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # create receipt with card
    payment = PaymentFactory(type=PaymentTypeEnum.CARD.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # get receipts by filter
    params = {
        "max_total": 10,
    }
    response = await http_client.get("/receipt", headers=headers, params=params)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert len(response_json) == 0


@pytest.mark.asyncio
async def test__receipt__success__get_receipts_with_pagination(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)
    headers = {
        "Authorization": token,
    }

    # create receipt with cash
    payment = PaymentFactory(type=PaymentTypeEnum.CASH.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # create receipt with card
    payment = PaymentFactory(type=PaymentTypeEnum.CARD.value)
    receipt = ReceiptFactory(payment=payment)
    payload = json.loads(receipt.model_dump_json())

    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    # get receipts by filter
    params = {
        "page": 1,
        "page_size": 1,
    }
    response = await http_client.get("/receipt", headers=headers, params=params)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert len(response_json) == 1

    params = {
        "page": 1,
    }
    response = await http_client.get("/receipt", headers=headers, params=params)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert len(response_json) == 2
