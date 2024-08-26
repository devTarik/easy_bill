from urllib.parse import urlparse, urlunparse

import asyncpg
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

TEST_DATABASE_URL = settings.test_database_url

test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


def get_asyncpg_url(database_url: str) -> str:
    parsed_url = urlparse(database_url)
    new_scheme = parsed_url.scheme.replace("postgresql+asyncpg", "postgresql")
    asyncpg_url = urlunparse(parsed_url._replace(scheme=new_scheme))  # noqa
    return asyncpg_url


async def async_database_exists(database_url: str) -> bool:
    postgres_url = get_asyncpg_url(database_url)

    db_name = urlparse(database_url).path.lstrip("/")
    conn = await asyncpg.connect(postgres_url.replace(db_name, "postgres"))
    exists = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    await conn.close()
    return exists is not None


async def create_database(conn: asyncpg.Connection, test_db_name: str):
    await conn.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{test_db_name}'
        AND pid <> pg_backend_pid();
        """)
    await conn.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    await conn.execute(f"CREATE DATABASE {test_db_name}")
    await conn.close()


async def drop_database(conn: asyncpg.Connection, test_db_name: str) -> None:
    await conn.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    await conn.close()


async def create_user_and_get_token(http_client: AsyncClient) -> str:
    payload = {
        "full_name": "test_full_name",
        "username": "test_username",
        "password": "test_password",
    }
    response = await http_client.post("/user/registry", json=payload)
    user = response.json()
    token_type = user.get("token_type")
    access_token = user.get("access_token")
    return f"{token_type} {access_token}"
