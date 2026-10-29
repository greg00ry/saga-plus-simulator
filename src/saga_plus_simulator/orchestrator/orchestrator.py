import random
import uuid
from typing import Any, cast

import httpx2

from saga_plus_simulator.orchestrator.handlers import request_error_handler, status_error_handler


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
        quantity: int) -> dict[str, Any] | None:
    async with httpx2.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            orders = await client.post(
                "/orders",
                json={"product_id": product_id, "quantity": quantity,},
                headers={"Idempotency-key": idempotency_key}
            )
            orders.raise_for_status()
            orders_data = orders.json()
        except httpx2.HTTPStatusError as e:
            status_error_handler(e)
            return None
        except httpx2.RequestError as e:
            request_error_handler(e)
            return None

        try:
            reservations = await client.post(
                "/reservations",
                json={"order_id":orders_data["id"], "quantity": orders_data["quantity"]},
                headers={"Idempotency-key": idempotency_key}
            )
            reservations.raise_for_status()
            reservations_data = reservations.json()
        except httpx2.HTTPStatusError as e:
            status_error_handler(e)
            return None
        except httpx2.RequestError as e:
            request_error_handler(e)
            return None

        try:
            payment = await client.post(
                f"/payments/{reservations_data["id"]}/pay",
                headers={"Idempotency-key": idempotency_key}
            )
            payment.raise_for_status()
            payment_data = payment.json()
        except httpx2.HTTPStatusError as e:
            status_error_handler(e)
            return None
        except httpx2.RequestError as e:
            request_error_handler(e)
            return None

        try:
            shipment = await client.post(
                f"/shipping/{payment_data["id"]}/ship",
                headers={"Idempotency-key": idempotency_key}
            )
            shipment.raise_for_status()
            shipment_data = shipment.json()
        except httpx2.HTTPStatusError as e:
            status_error_handler(e)
            return None
        except httpx2.RequestError as e:
            request_error_handler(e)
            return None
#rozwiązanie problemu zwrócenia Any w mypy, cast wymusza typowanie
        return cast(dict[str, Any], shipment_data)

if __name__ == "__main__":
    import asyncio

    asyncio.run(run_saga())
