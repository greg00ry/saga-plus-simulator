from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session

from saga_plus_simulator.database import get_db
from saga_plus_simulator.generate_idempotency_key import get_cached_response, save_response
from saga_plus_simulator.models import Order, Payment, Product, Reservation, Shipment
from saga_plus_simulator.schemas import PaymentOut, ReservationCreate, ReservationOut, ShipmentOut, OrderCreate, \
    OrderOut

app = FastAPI()

@app.post("/orders")
def create_order(
        payload: OrderCreate,
        idempotency_key: str = Header(),
        db: Session = Depends(get_db)
) -> Order | dict[str, Any]:
    cached = get_cached_response(idempotency_key, "create_order", db)
    if cached is not None:
        return cached

    order = Order(
        product_id=payload.product_id,
        quantity=payload.quantity,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    response_data = OrderOut.model_validate(order).model_dump()
    save_response(
        idempotency_key,
        "create_order",
        "/orders",
        response_data,
        200,
        db
    )

    return order

@app.post("/orders/{order_id}/release", response_model=OrderOut)
def release_order(
        order_id: int,
        db: Session = Depends(get_db),
        idempotency_key: str = Header()
) -> Order | dict[str, Any]:

    cached = get_cached_response(idempotency_key, "release_order", db)

    if cached is not None:
        return cached


    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "released"

    db.commit()
    db.refresh(order)

    response_data = OrderOut.model_validate(order).model_dump()
    save_response(
        idempotency_key,
        "release_order",
        f"/reservations/{order.id}/release",
        response_data,
        200,
        db
    )

    return order

@app.post("/reservations", response_model=ReservationOut)
def create_reservation(
        payload: ReservationCreate,
        db: Session = Depends(get_db),
        idempotency_key: str = Header()
                       ) -> Reservation | dict[str, Any]:

    cached = get_cached_response(idempotency_key, "create_reservation", db)
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
        idempotency_key,
        "create_reservation",
        "/reservations",
        response_data,
        200,
        db
    )
    return reservation



@app.post("/reservations/{reservation_id}/release", response_model=ReservationOut)
def release_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        idempotency_key: str = Header()
                        ) -> Reservation | dict[str, Any]:

    cached = get_cached_response(idempotency_key, "release_reservation", db)
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
        idempotency_key,
        "release_reservation",
        f"/reservations/{reservation_id}/release",
        response_data,
        200,
        db
    )

    return reservation


@app.post("/payments/{reservation_id}/pay", response_model=PaymentOut)
def create_payment(
        reservation_id: int,
        db: Session = Depends(get_db),
        idempotency_key: str = Header()
) -> Payment | dict[str, Any]:

    cached = get_cached_response(idempotency_key, "create_payment", db)
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
        idempotency_key,
        "create_payment",
        f"/payments/{reservation_id}/pay",
        response_data,
        200,
        db
    )

    return payment

@app.post("/payments/{payment_id}/refund", response_model=PaymentOut)
def refund(
        payment_id: int,
        db: Session = Depends(get_db),
        idempotency_key: str = Header()
           ) -> Payment | dict[str, Any]:

    cached = get_cached_response(idempotency_key, "refund", db)
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
        idempotency_key,
        "refund",
        f"/payments/{payment_id}/refund",
        response_data,
        200,
        db
    )

    return payment


@app.post("/shipping/{payment_id}/ship", response_model=ShipmentOut)
def create_shipping(
        payment_id: int,
        db: Session = Depends(get_db),
        idempotency_key: str = Header()
) -> Shipment | dict[str, Any]:

    cached = get_cached_response(idempotency_key, "create_shipping", db)
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
        idempotency_key,
        "create_shipping",
        f"/shipping/{payment_id}/ship",
        response_data,
        200,
        db
    )

    return shipment

@app.post("/shipping/{shipment_id}/cancel", response_model=ShipmentOut)
def cancel_shipment(
        shipment_id: int,
        db: Session = Depends(get_db),
        idempotency_key: str = Header()
) -> Shipment | dict[str, Any]:

    cached = get_cached_response(idempotency_key, "cancel_shipment", db)
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
        idempotency_key,
        "cancel_shipment",
        f"/shipping/{shipment_id}/cancel",
        response_data,
        200,
        db
    )

    return shipment