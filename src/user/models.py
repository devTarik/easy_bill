import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(128))
    username: Mapped[str] = mapped_column(String(128), unique=True)
    hashed_password: Mapped[str] = mapped_column(String())
    active: Mapped[bool] = mapped_column(default=True)

    refresh_tokens = relationship("RefreshToken", back_populates="user", lazy="selectin")
    receipts = relationship("Receipt", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"User(id={self.id}, full_name={self.full_name})"

    def get_token_data(self) -> dict:
        return {
            "user_id": str(self.id),
            "sub": self.username,
        }


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(unique=True, index=True)

    user = relationship("User", back_populates="refresh_tokens", lazy="selectin")

    def __repr__(self) -> str:
        return f"RefreshToken(id={self.id!r}, user_id={self.user_id!r})"
