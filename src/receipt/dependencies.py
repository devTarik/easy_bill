from datetime import datetime
from decimal import Decimal

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select

from src.receipt.models import Payment, Receipt
from src.user.dependencies import validate_user
from src.user.schemas import CurrentUserSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def filter_recept(
    user: CurrentUserSchema = Depends(validate_user),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    payment_type: str | None = Query(None),
    min_total: Decimal | None = Query(None),
    max_total: Decimal | None = Query(None),
) -> select:
    stmt = select(Receipt).filter(Receipt.user_id == user.id)

    if start_date:
        stmt = stmt.filter(Receipt.created_at >= start_date)
    if end_date:
        stmt = stmt.filter(Receipt.created_at <= end_date)
    if payment_type:
        stmt = stmt.join(Payment).filter(Payment.type == payment_type)
    if min_total is not None:
        stmt = stmt.filter(Receipt.total >= min_total)
    if max_total is not None:
        stmt = stmt.filter(Receipt.total <= max_total)

    return stmt


async def paginate(
    filtered_query: select = Depends(filter_recept),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> select:
    offset = (page - 1) * page_size
    stmt = filtered_query.offset(offset).limit(page_size)
    return stmt
