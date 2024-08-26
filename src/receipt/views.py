from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.exc import MultipleResultsFound

from src.config import settings
from src.db import db_session
from src.receipt.dependencies import filter_recept, paginate
from src.receipt.models import Receipt, ReceiptProduct
from src.receipt.receipt_constructor import ReceiptConstructor
from src.receipt.schemas import ExceptionSchema, PaymentSchema, ReceiptRequestSchema, ReceiptResponseSchema
from src.receipt.utils import create_receipt_in_db, get_single_receipt_response
from src.user.dependencies import validate_user
from src.user.schemas import CurrentUserSchema

router = APIRouter()


@router.post(
    "",
    response_model=ReceiptResponseSchema,
    responses={
        400: {"model": ExceptionSchema, "description": "Error creating product"},
        401: {"model": ExceptionSchema, "description": "Invalid token"},
    },
)
async def create_receipt(
    request: Request,
    request_data: ReceiptRequestSchema,
    db: AsyncSession = Depends(db_session),
    user: CurrentUserSchema = Depends(validate_user),
):
    user_id = str(user.id)
    products_data = request_data.products
    payment_data = request_data.payment

    receipt, payment = await create_receipt_in_db(db, user_id, products_data, payment_data)
    payment_schema = PaymentSchema(**payment.to_dict())

    receipt_response = ReceiptResponseSchema(
        id=receipt.id,
        products=products_data,
        payment=payment_schema,
        total=receipt.total,
        rest=payment.rest,
        created_at=receipt.created_at,
    )
    receipt_response.set_receipt_url(f"{request.base_url}receipt/{receipt.id}/public")
    return receipt_response


@router.get(
    "",
    response_model=List[ReceiptResponseSchema],
    responses={
        401: {"model": ExceptionSchema, "description": "Invalid token"},
        404: {"model": ExceptionSchema, "description": "Payment for receipt 'receipt.id' not found"},
    },
)
async def get_receipts(
    request: Request,
    db: AsyncSession = Depends(db_session),
    user: CurrentUserSchema = Depends(validate_user),
    filtered_query: select = Depends(filter_recept),
    query: select = Depends(paginate),
):
    result = await db.scalars(query)
    receipts = result.all()
    if not receipts:
        return []

    receipts_response = [await get_single_receipt_response(db, receipt, request.base_url) for receipt in receipts]
    return receipts_response


@router.get(
    "/{id}",
    response_model=ReceiptResponseSchema,
    responses={
        400: {"model": ExceptionSchema, "description": "Error getting receipt"},
        401: {"model": ExceptionSchema, "description": "Invalid token"},
        404: {"model": ExceptionSchema, "description": "Receipt not found"},
    },
)
async def get_receipt(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(db_session),
    user: CurrentUserSchema = Depends(validate_user),
):
    result = await db.scalars(select(Receipt).filter(Receipt.user_id == user.id, Receipt.id == id))
    try:
        receipt = result.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail="Error getting receipt")

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    receipt_response = await get_single_receipt_response(db, receipt, request.base_url)
    return receipt_response


@router.get(
    "/{id}/public",
    response_class=PlainTextResponse,
    responses={
        400: {"model": ExceptionSchema, "description": "Error getting receipt"},
        404: {"model": ExceptionSchema, "description": "Receipt not found"},
    },
)
async def get_public_receipt(
    id: UUID,
    db: AsyncSession = Depends(db_session),
):
    stmt = (
        select(Receipt)
        .options(
            selectinload(Receipt.user),
            selectinload(Receipt.products).selectinload(ReceiptProduct.product),
            selectinload(Receipt.payment),
        )
        .filter(Receipt.id == id)
    )
    try:
        result = await db.execute(stmt)
        receipt = result.scalars().unique().first()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail="Error getting receipt")

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    receipt_constructor = ReceiptConstructor(
        store_name=settings.receipt_shop_name,
        receipt=receipt,
        row_length=settings.receipt_row_length,
    )
    text = receipt_constructor.create()
    return text
