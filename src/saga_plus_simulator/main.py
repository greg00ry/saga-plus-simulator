from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from saga_plus_simulator.database import get_db
from saga_plus_simulator.models import Reservation
from saga_plus_simulator.schemas import ReservationOut, ReservationCreate



app = FastAPI()

class Item(BaseModel):
    name: str
    quantity: int

@app.post("/items")
def create_item(item: Item):
    return {"received": item.name, "quantity": item.quantity}


@app.post("/reservations", response_model=ReservationOut)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    reservation = Reservation(
        order_id=payload.order_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation

@app.post("/reservations/{reservation_id}/release", response_model=ReservationOut)
def release_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.get(Reservation, reservation_id)

    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = "released"
    db.commit()
    db.refresh(reservation)
    return reservation
