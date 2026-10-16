from pydantic import BaseModel


class ReservationCreate(BaseModel):
    order_id: int
    quantity: int


class ReservationOut(BaseModel):
    id: int
    order_id: int
    quantity: int
    status: str

    model_config = {"from_attributes": True}


class PaymentOut(BaseModel):
    id: int
    order_id: int
    status: str
    amount: float

    model_config = {"from_attributes": True}


class ShipmentCreate(BaseModel):
    order_id: int
    payment_id: int


class ShipmentOut(BaseModel):
    id: int
    order_id: int
    status: str

    model_config = {"from_attributes": True}
