import json
from decimal import Decimal
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.receipt.schemas import PaymentTypeEnum
from tests.factories import PaymentFactory, ProductFactory, ReceiptFactory
from tests.helper import create_user_and_get_token


@pytest.mark.asyncio
async def test__receipt__success__create_receipt(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)

    products = [
        ProductFactory(
            name="Apple",
            price="5",
            quantity="10",
        ),
        ProductFactory(
            name="Banana",
            price="13.5",
            quantity="3",
        ),
    ]
    payment = PaymentFactory(
        type=PaymentTypeEnum.CASH.value,
        amount="100",
    )
    receipt = ReceiptFactory(products=products, payment=payment)
    payload = json.loads(receipt.model_dump_json())

    headers = {
        "Authorization": token,
    }
    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.OK

    total = response.json().get("total")
    rest = response.json().get("rest")
    assert total == "90.5"
    assert rest == str(receipt.payment.amount - Decimal(total))


@pytest.mark.asyncio
async def test__receipt__fails__invalid_token(http_client: AsyncClient):
    token = await create_user_and_get_token(http_client)

    products = [
        ProductFactory(
            name="Apple",
            price="5",
            quantity="10",
        )
    ]
    payment = PaymentFactory(
        type=PaymentTypeEnum.CASH.value,
        amount="50",
    )
    receipt = ReceiptFactory(products=products, payment=payment)
    payload = json.loads(receipt.model_dump_json())

    headers = {
        "Authorization": f"{token}fake",
    }
    response = await http_client.post("/receipt", headers=headers, json=payload)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token"
