from fastapi.testclient import TestClient
from sqlalchemy import text

from saga_plus_simulator.main import app

client = TestClient(app)

def test_full_saga_happy_path(client, sample_product, sample_order) -> None:
    reservation = client.post("/reservations", json={"order_id": sample_order.id, "quantity": 2})
    reservation_id = reservation.json()["id"]
    assert reservation.status_code == 200

    payment = client.post(f"/payments/{reservation_id}/pay")
    payment_id = payment.json()["id"]
    assert payment.status_code == 200
    assert payment.json()["amount"] == sample_product.price * 2
    assert payment.json()["status"] == "paid"

    shipment = client.post(f"/shipping/{payment_id}/ship" )
    assert shipment.status_code == 200
    assert shipment.json()["status"] == "package picked up"
    return

def test_no_leftover_data_after_saga(engine):
    with engine.connect() as conn:
        count = conn.execute(text("SELECT count(*) FROM products")).scalar()
        assert count == 0