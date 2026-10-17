from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from saga_plus_simulator.database import get_db
from saga_plus_simulator.models import Order, Payment, Product, Reservation, Shipment
from saga_plus_simulator.schemas import PaymentOut, ReservationCreate, ReservationOut, ShipmentOut

app = FastAPI()


@app.post("/reservations", response_model=ReservationOut)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)) -> Reservation:

    reservation = Reservation(
        order_id=payload.order_id,
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


@app.post("/payments/{reservation_id}/pay", response_model=PaymentOut)
def create_payment(reservation_id: int, db: Session = Depends(get_db)) -> Payment:

    reservation = db.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.status == "released":
        raise HTTPException(status_code=404, detail="Reservation already released")

    order = db.get(Order, reservation.order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    product = db.get(Product, order.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    payment = Payment(
        order_id=reservation.order_id,
        amount=reservation.quantity * product.price,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment

@app.post("/payments/{payment_id}/refund", response_model=PaymentOut)
def refund(paymanent_id: int, db: Session = Depends(get_db)) -> Payment:
    payment = db.get(Payment, paymanent_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "refund"

    db.commit()
    db.refresh(payment)

    return payment


@app.post("/shipping/{payment_id}/ship", response_model=ShipmentOut)
def create_shipping(payment_id: int, db: Session = Depends(get_db)) -> Shipment:

    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != "paid":
        raise HTTPException(status_code=404, detail="Payment already paid")

    shipment = Shipment(
        order_id=payment.order_id,
    )

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    return shipment

@app.post("/shipping/{shipment_id}/cancel", response_model=PaymentOut)
def refund(shipment_id: int, db: Session = Depends(get_db)) -> Shipment:
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    shipment.status = "cancelled"

    db.commit()
    db.refresh(shipment)

    return shipment