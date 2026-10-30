import random
import uuid
from typing import Any

import httpx2

from saga_plus_simulator.orchestrator.handlers import (
    COMPENSATIONS,
    call_step,
    request_error_handler,
    retry,
    status_error_handler,
)


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
        #That list we are using in compensation in the exception handling
        completed_steps: list[tuple[str, int]] = []
        try:


            orders_data = await retry(
                lambda: call_step(
                    client,
                    "/orders",
                    json={"product_id": product_id, "quantity": quantity},
                    headers={"Idempotency-key": idempotency_key}
                )
            )
            #After every step we have to append them into list declared above.
            # We are using this list in exception handling

            completed_steps.append(("order", orders_data["id"]))



            reservations_data = await retry(
                lambda: call_step(
                    client,
                    "/reservations",
                    json={"order_id": orders_data["id"], "quantity": orders_data["quantity"]},
                    headers={"Idempotency-key": idempotency_key}
                )
            )
            #yet another append

            completed_steps.append(("reservation", reservations_data["id"]))


            payment_data = await retry(
                lambda: call_step(
                    client,
                    f"/payments/{reservations_data["id"]}/pay",
                    headers={"Idempotency-key": idempotency_key}
                )
            )
            # yet another append

            completed_steps.append(("payment", payment_data["id"]))



            shipment_data = await retry(
                lambda: call_step(
                    client,
                    f"/shipping/{payment_data["id"]}/ship",
                    headers={"Idempotency-key": idempotency_key}
                )
            )

            # yet another append

            completed_steps.append(("shipment", shipment_data["id"]))

        except httpx2.HTTPStatusError as e:

            status_error_handler(e)

            for step_name, step_id in reversed(completed_steps):
                method, url_template = COMPENSATIONS[step_name]
                url = url_template.format(id=step_id)
                func = getattr(client, method)
                await func(url, headers={"Idempotency-key": idempotency_key})

            return None

        except httpx2.RequestError as e:
            request_error_handler(e)
            return None
        #rozwiązanie problemu zwrócenia Any w mypy, cast wymusza typowanie
        return shipment_data

if __name__ == "__main__":
    import asyncio

    asyncio.run(run_saga())
