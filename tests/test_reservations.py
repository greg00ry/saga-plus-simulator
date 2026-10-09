from fastapi.testclient import TestClient

from saga_plus_simulator.main import app

client = TestClient(app)
def test_create_reservation():
    response = client.post(
        "/reservations",
        json={"order_id": 1, "product_id": 1, "quantity": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 1
    assert data["product_id"] == 1
    assert data["quantity"] == 2
    assert data["status"] == "reserved"
    assert "id" in data