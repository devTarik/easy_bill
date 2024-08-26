from datetime import datetime, timedelta
from typing import Union
from uuid import UUID

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from zoneinfo import ZoneInfo

from src.config import settings
from src.user.models import RefreshToken, User
from src.user.schemas import CreateUser, RefreshTokenSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
utc = ZoneInfo("UTC")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def verify_refresh_token(db: AsyncSession, token: str) -> RefreshToken:
    result = await db.scalars(
        select(RefreshToken).options(joinedload(RefreshToken.user)).filter(RefreshToken.token == token)
    )
    refresh_token = result.first()
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return refresh_token


async def create_user_in_db(db: AsyncSession, user: CreateUser) -> User:
    db_user = User(
        full_name=user.full_name,
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_current_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.scalars(select(User).filter(User.id == user_id))
    user = result.first()
    return user


def get_token_data(user: User) -> dict:
    return {
        "user_id": str(user.id),
        "sub": user.username,
    }


async def refresh_user_token(db: AsyncSession, token: RefreshTokenSchema) -> tuple[str, str]:
    refresh_token = await verify_refresh_token(db, token.refresh_token)
    token_data = refresh_token.user.get_token_data()

    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.jwt_refresh_token_expire_days)

    new_access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token(data=token_data, expires_delta=refresh_token_expires)
    await db.delete(refresh_token)

    new_refresh_token_record = RefreshToken(token=new_refresh_token, user_id=refresh_token.user_id)
    db.add(new_refresh_token_record)
    await db.commit()

    return new_access_token, new_refresh_token


async def create_user_token(db: AsyncSession, user: User):
    token_data = user.get_token_data()

    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.jwt_refresh_token_expire_days)

    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data=token_data, expires_delta=refresh_token_expires)

    new_refresh_token_record = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(new_refresh_token_record)
    await db.commit()

    return access_token, refresh_token
