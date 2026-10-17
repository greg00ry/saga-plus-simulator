from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Product(Base):
    __tablename__ = "products"

    price: Mapped[float]
    name: Mapped[str]
    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)


class Order(Base):
    __tablename__ = "orders"

    product_id: Mapped[int]
    quantity: Mapped[int]
    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)


class Reservation(Base):
    __tablename__ = "reservations"

    order_id: Mapped[int]
    quantity: Mapped[int]
    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)
    status: Mapped[str] = mapped_column(default="reserved")


class Payment(Base):
    __tablename__ = "payments"

    order_id: Mapped[int]
    amount: Mapped[float]
    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)
    status: Mapped[str] = mapped_column(default="paid")


class Shipment(Base):
    __tablename__ = "shipments"

    order_id: Mapped[int]
    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)
    status: Mapped[str] = mapped_column(default="package picked up")


class ProcessedRequests(Base):
    __tablename__ = "processed_requests"
    idempotency_key: Mapped[str] = mapped_column(primary_key=True)
    endpoint: Mapped[int]
    response_body: Mapped[dict[str, Any]] = mapped_column(JSON)
    response_status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)