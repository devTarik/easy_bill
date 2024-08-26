from decimal import Decimal
from typing import List, Tuple
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.receipt.models import Payment, Product, Receipt, ReceiptProduct
from src.receipt.schemas import PaymentSchema, ProductSchema, ReceiptResponseSchema


async def get_or_create_product(db: AsyncSession, product_data: ProductSchema) -> Product:
    result = await db.scalars(select(Product).filter_by(name=product_data.name))
    product = result.first()

    if not product:
        product = Product(name=product_data.name, price=product_data.price)
        db.add(product)
        try:
            await db.flush()
            await db.refresh(product)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error creating product")

    return product


async def create_receipt_in_db(
    db: AsyncSession,
    user_id: UUID,
    products_data: List[ProductSchema],
    payment_data: PaymentSchema,
) -> Tuple[Receipt, Payment]:
    total_sum = Decimal(0)
    receipt = Receipt(user_id=user_id, total=total_sum)
    db.add(receipt)
    await db.flush()

    for product_data in products_data:
        product = await get_or_create_product(db, product_data)
        quantity = product_data.quantity
        total = product.price * quantity
        total_sum += total

        receipt_product = ReceiptProduct(
            receipt_id=receipt.id,
            product_id=product.id,
            quantity=quantity,
            total=total,
        )
        db.add(receipt_product)

    receipt.total = total_sum
    rest = payment_data.amount - total_sum

    payment = Payment(
        receipt_id=receipt.id,
        type=payment_data.type.value,
        amount=payment_data.amount,
        rest=rest,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(receipt)
    await db.refresh(payment)

    return receipt, payment


async def get_single_receipt_response(db: AsyncSession, receipt: Receipt, url: str) -> ReceiptResponseSchema:
    products_data = await db.scalars(
        select(ReceiptProduct)
        .options(joinedload(ReceiptProduct.product))
        .options(joinedload(ReceiptProduct.receipt))
        .filter(ReceiptProduct.receipt_id == receipt.id)
    )
    products = products_data.all()
    product_schemas = [
        ProductSchema(
            name=product.product.name,
            price=product.product.price,
            quantity=product.quantity,
            total=product.total,
        )
        for product in products
    ]

    payment_data = await db.scalars(
        select(Payment).options(joinedload(Payment.receipt)).filter(Payment.receipt_id == receipt.id)
    )
    payment = payment_data.first()
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment for receipt {receipt.id} not found")

    payment_schema = PaymentSchema(type=payment.type, amount=payment.amount)
    receipt_response = ReceiptResponseSchema(
        id=receipt.id,
        products=product_schemas,
        payment=payment_schema,
        total=receipt.total,
        rest=payment.rest,
        created_at=receipt.created_at,
    )
    receipt_response.set_receipt_url(f"{url}receipt/{receipt.id}/public")
    return receipt_response
