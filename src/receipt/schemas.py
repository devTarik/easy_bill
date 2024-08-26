from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel


class ExceptionSchema(BaseModel):
    detail: str


class DecimalBaseModel(BaseModel):
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v),
        }


class PaymentTypeEnum(Enum):
    CASH = "cash"
    CARD = "card"


class ProductSchema(DecimalBaseModel):
    name: str
    price: Decimal
    quantity: Decimal
    total: Decimal | None = None

    def __init__(self, **data):
        super().__init__(**data)
        self.total = self.calc_total()

    def calc_total(self):
        return self.price * self.quantity


class PaymentSchema(DecimalBaseModel):
    type: PaymentTypeEnum
    amount: Decimal


class ReceiptRequestSchema(DecimalBaseModel):
    products: List[ProductSchema]
    payment: PaymentSchema


class ReceiptResponseSchema(DecimalBaseModel):
    id: UUID
    products: List[ProductSchema]
    payment: PaymentSchema
    total: Decimal
    rest: Decimal
    created_at: datetime
    public_url: str | None = None

    def set_receipt_url(self, receipt_url: str) -> None:
        self.public_url = receipt_url


class ReceiptsListResponseSchema(DecimalBaseModel):
    receipts: List[ReceiptResponseSchema]
