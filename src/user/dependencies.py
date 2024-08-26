import jwt
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db import db_session
from src.user.exceptions import UserDisable, UserNotFound
from src.user.models import User
from src.user.schemas import CurrentUserSchema, UserLoginSchema
from src.user.utils import get_current_user_by_id, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def validate_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(db_session),
) -> CurrentUserSchema:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        username = payload.get("sub")

        current_user = await get_current_user_by_id(db, user_id)
        if not current_user:
            raise UserNotFound()
        if not current_user.active:
            raise UserDisable()

        return CurrentUserSchema(
            id=user_id,
            full_name=current_user.full_name,
            username=username,
            active=current_user.active,
        )
    except (UserNotFound, UserDisable, ValidationError, jwt.PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_user_by_username(
    data: UserLoginSchema,
    db: AsyncSession = Depends(db_session),
) -> CurrentUserSchema:
    result = await db.scalars(select(User).filter(User.username == data.username))
    user = result.first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return user
