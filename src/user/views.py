from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import db_session
from src.receipt.schemas import ExceptionSchema
from src.user.dependencies import get_user_by_username, validate_user
from src.user.models import User
from src.user.schemas import (
    AccessTokenSchema,
    CreateUser,
    CurrentUserSchema,
    RefreshTokenSchema,
    UserResponse,
)
from src.user.utils import (
    create_user_in_db,
    create_user_token,
    refresh_user_token,
)

router = APIRouter()


@router.get(
    "/me",
    response_model=CurrentUserSchema,
    responses={
        401: {"model": ExceptionSchema, "description": "Invalid token"},
    },
)
async def user_me(user: UserResponse = Depends(validate_user)) -> CurrentUserSchema:
    return CurrentUserSchema(**user.model_dump())


@router.post(
    "/registry",
    response_model=AccessTokenSchema,
    responses={
        403: {"model": ExceptionSchema, "description": "Username already registered"},
    },
)
async def user_registry(
    user: CreateUser,
    db: AsyncSession = Depends(db_session),
) -> AccessTokenSchema:
    try:
        db_user = await create_user_in_db(db, user)
        access_token, refresh_token = await create_user_token(db, db_user)
        return AccessTokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Username already registered",
        )


@router.post(
    "/token",
    response_model=AccessTokenSchema,
    responses={
        403: {"model": ExceptionSchema, "description": "Username already registered"},
    },
)
async def user_login(
    db: AsyncSession = Depends(db_session),
    user: User = Depends(get_user_by_username),
) -> AccessTokenSchema:
    access_token, refresh_token = await create_user_token(db, user)
    return AccessTokenSchema(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/token/refresh",
    response_model=AccessTokenSchema,
    responses={
        401: {"model": ExceptionSchema, "description": "Invalid token"},
    },
)
async def refresh_token(
    token: RefreshTokenSchema,
    db: AsyncSession = Depends(db_session),
) -> AccessTokenSchema:
    new_access_token, new_refresh_token = await refresh_user_token(db, token)
    return AccessTokenSchema(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
