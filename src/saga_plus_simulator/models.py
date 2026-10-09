from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    order_id: Mapped[int]
    product_id: Mapped[int]
    quantity: Mapped[int]
    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)
    status: Mapped[str] = mapped_column(default="reserved")
