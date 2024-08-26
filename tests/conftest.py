import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator
from urllib.parse import urlparse

import asyncpg
import pytest
from httpx import AsyncClient

from app import app
from src.config import settings
from src.db import Base
from tests.helper import (
    create_database,
    drop_database,
    get_asyncpg_url,
    test_engine,
)


@pytest.fixture(scope="session", autouse=True)
async def setup_database(default_db_url: str, test_db_name: str):
    default_conn = await asyncpg.connect(default_db_url)
    await create_database(default_conn, test_db_name)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await drop_database(default_conn, test_db_name)


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> Generator["AbstractEventLoop", None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_url() -> str:
    return settings.test_database_url


@pytest.fixture(scope="session")
async def test_db_name() -> str:
    return settings.db_name + "_tests"


@pytest.fixture(scope="session")
async def default_db_url(test_db_name: str) -> str:
    postgres_url = get_asyncpg_url(settings.database_url)
    db_name = urlparse(postgres_url).path.lstrip("/")
    return postgres_url.replace(db_name, "postgres")


@pytest.fixture(scope="session")
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="https://test.easy_bill.io/") as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
async def clear_db():
    yield

    db_url = get_asyncpg_url(settings.database_url)
    conn = await asyncpg.connect(db_url)
    for table in reversed(Base.metadata.sorted_tables):
        await conn.execute(f"TRUNCATE TABLE {table.name} CASCADE;")
    await conn.close()
