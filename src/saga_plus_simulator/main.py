from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from saga_plus_simulator.database import get_db
from saga_plus_simulator.generate_idempotency_key import get_cached_response, save_response
from saga_plus_simulator.models import Order, Payment, Product, Reservation, Shipment
from saga_plus_simulator.schemas import PaymentOut, ReservationCreate, ReservationOut, ShipmentOut

app = FastAPI()


@app.post("/reservations", response_model=ReservationOut)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)) -> Reservation | dict[str, Any]:

    cached = get_cached_response(str(payload.order_id), "create_reservation", db)
    if cached is not None:
        return cached
    reservation = Reservation(
        order_id=payload.order_id,
        quantity=payload.quantity,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    response_data = ReservationOut.model_validate(reservation).model_dump()
    save_response(
        str(payload.order_id),
        "create_reservation",
        "/reservations",
        response_data,
        200,
        db
    )
    return reservation



@app.post("/reservations/{reservation_id}/release", response_model=ReservationOut)
def release_reservation(reservation_id: int, db: Session = Depends(get_db)) -> Reservation | dict[str, Any]:

    cached = get_cached_response(str(reservation_id), "release_reservation", db)
    if cached is not None:
        return cached


    reservation = db.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = "released"

    db.commit()
    db.refresh(reservation)

    response_data = ReservationOut.model_validate(reservation).model_dump()
    save_response(
        str(reservation_id),
        "release_reservation",
        f"/reservations/{reservation_id}/release",
        response_data,
        200,
        db
    )

    return reservation


@app.post("/payments/{reservation_id}/pay", response_model=PaymentOut)
def create_payment(reservation_id: int, db: Session = Depends(get_db)) -> Payment | dict[str, Any]:

    cached = get_cached_response(str(reservation_id), "create_payment", db)
    if cached is not None:
        return cached

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

    response_data = PaymentOut.model_validate(payment).model_dump()
    save_response(
        str(reservation_id),
        "create_payment",
        f"/payments/{reservation_id}/pay",
        response_data,
        200,
        db
    )

    return payment

@app.post("/payments/{payment_id}/refund", response_model=PaymentOut)
def refund(payment_id: int, db: Session = Depends(get_db)) -> Payment | dict[str, Any]:

    cached = get_cached_response(str(payment_id), "refund", db)
    if cached is not None:
        return cached

    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "refund"

    db.commit()
    db.refresh(payment)

    response_data = PaymentOut.model_validate(payment).model_dump()
    save_response(
        str(payment_id),
        "refund",
        f"/payments/{payment_id}/refund",
        response_data,
        200,
        db
    )

    return payment


@app.post("/shipping/{payment_id}/ship", response_model=ShipmentOut)
def create_shipping(payment_id: int, db: Session = Depends(get_db)) -> Shipment | dict[str, Any]:

    cached = get_cached_response(str(payment_id), "create_shipping", db)
    if cached is not None:
        return cached

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

    response_data = ShipmentOut.model_validate(shipment).model_dump()
    save_response(
        str(payment_id),
        "create_shipping",
        f"/shipping/{payment_id}/ship",
        response_data,
        200,
        db
    )

    return shipment

@app.post("/shipping/{shipment_id}/cancel", response_model=ShipmentOut)
def cancel_shipment(shipment_id: int, db: Session = Depends(get_db)) -> Shipment | dict[str, Any]:

    cached = get_cached_response(str(shipment_id), "cancel_shipment", db)
    if cached is not None:
        return cached

    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipment.status = "cancelled"

    db.commit()
    db.refresh(shipment)

    response_data = ShipmentOut.model_validate(shipment).model_dump()
    save_response(
        str(shipment_id),
        "cancel_shipment",
        f"/shipping/{shipment_id}/cancel",
        response_data,
        200,
        db
    )

    return shipment