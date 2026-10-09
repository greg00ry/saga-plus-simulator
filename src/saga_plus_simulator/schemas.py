from pydantic import BaseModel



class ReservationCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int

class ReservationOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    status: str

    model_config = {"from_attributes": True}
