from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from saga_plus_simulator.database import get_db
from saga_plus_simulator.models import Reservation
from saga_plus_simulator.schemas import ReservationCreate, ReservationOut

app = FastAPI()

@app.post("/reservations", response_model=ReservationOut)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)) -> Reservation:
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
def release_reservation(reservation_id: int, db: Session = Depends(get_db)) -> Reservation:
    reservation = db.get(Reservation, reservation_id)

    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = "released"
    db.commit()
    db.refresh(reservation)
    return reservation
