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
