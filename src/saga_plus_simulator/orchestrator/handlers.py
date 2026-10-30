from typing import Any

from httpx2 import HTTPStatusError, RequestError, AsyncClient




def status_error_handler(e: HTTPStatusError) -> None:
    try:
        print(e.response.json()["detail"])
    except (ValueError, KeyError):
        print(e.response.text)
    return

def request_error_handler(e: RequestError) -> None:
    print(f"Request failed: {type(e).__name__} - {e}")
    return

async def call_step(client: AsyncClient, method, url, **kwargs) -> dict[str, Any]:
    response = await client.post(url, **kwargs)
    response.raise_for_status()
    return response.json()