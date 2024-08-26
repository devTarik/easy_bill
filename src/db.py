import uuid

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

from src.config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL)
AsyncSession = async_sessionmaker(bind=engine, class_=AsyncSession, autocommit=False, autoflush=False)


async def dispose_engine():
    await engine.dispose()


async def db_session():
    async with AsyncSession() as session:
        yield session


class Base:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


Base = declarative_base(cls=Base)
