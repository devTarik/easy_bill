import datetime
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.user.models import Base


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(128))
    price: Mapped[Decimal] = mapped_column(DECIMAL)


class Receipt(Base):
    __tablename__ = "receipts"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(DECIMAL)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="receipts")
    products = relationship("ReceiptProduct", back_populates="receipt")
    payment = relationship("Payment", uselist=False, back_populates="receipt")


class ReceiptProduct(Base):
    __tablename__ = "receipt_products"

    receipt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("receipts.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    quantity: Mapped[Decimal]
    total: Mapped[Decimal] = mapped_column(DECIMAL)

    receipt = relationship("Receipt", back_populates="products")
    product = relationship("Product")


class Payment(Base):
    __tablename__ = "payments"

    receipt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("receipts.id"))
    type: Mapped[str] = mapped_column(String(32))
    amount: Mapped[Decimal] = mapped_column(DECIMAL)
    rest: Mapped[Decimal] = mapped_column(DECIMAL)

    receipt = relationship("Receipt", back_populates="payment")
