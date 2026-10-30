import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any

import httpx2
from httpx2 import AsyncClient, HTTPStatusError, RequestError

COMPENSATIONS = {
      "order": ("post", "/orders/{id}/release"),
      "reservation": ("post", "/reservations/{id}/release"),
      "payment": ("post", "/payments/{id}/refund"),
      "shipment": ("post", "/shipping/{id}/cancel"),
  }

def status_error_handler(e: HTTPStatusError) -> None:
    try:
        print(e.response.json()["detail"])
    except (ValueError, KeyError):
        print(e.response.text)
    return

def request_error_handler(e: RequestError) -> None:
    print(f"Request failed: {type(e).__name__} - {e}")
    return

async def call_step(client: AsyncClient, url: str, **kwargs: Any) -> dict[str, Any]:
    response = await client.post(url, **kwargs)
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    return data

async def retry(
        func:  Callable[[], Awaitable[dict[str, Any]]],
        max_attempts: int = 3,
        base_delay: float = 1.0
) -> dict[str, Any]:
    for attempt in range(max_attempts):
        try:
            return await func()
        except httpx2.HTTPStatusError:
            if attempt == max_attempts - 1:
                raise
            delay = random.uniform(0, min(30, base_delay * 2 ** attempt))
            await asyncio.sleep(delay)
    raise RuntimeError("unreachable")