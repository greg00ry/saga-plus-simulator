import random
import uuid
from typing import Any, cast

import httpx2


async def run_saga() -> None:

    await orchestrator(
        generate_idempotency_key(),
        random.randint(1, 100),
        random.randint(1, 100)
    )
    return

def generate_idempotency_key() -> str:
    return str(uuid.uuid4())

async def orchestrator(
        idempotency_key: str,
        product_id: int,
        quantity: int) -> dict[str, Any]:
    async with httpx2.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/orders",
            json={"product_id": product_id, "quantity": quantity,},
            headers={"Idempotency-key": idempotency_key}
        )
        data = response.json()

        payment = await client.post(
            f"/payments/{data["reservation_id"]}/pay",
            headers={"Idempotency-key": idempotency_key}
        )
        payment_data = payment.json()



        shipment = await client.post(
            f"/shipping/{payment_data["payment_id"]}/ship",
            headers={"Idempotency-key": idempotency_key}
        )
        shipment_data = shipment.json()
#rozwiązanie problemu zwrócenia Any w mypy, cast wymusza typowanie
        return cast(dict[str, Any], shipment_data)