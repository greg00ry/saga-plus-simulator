
from httpx2 import HTTPStatusError, RequestError


def status_error_handler(e: HTTPStatusError) -> None:
    try:
        print(e.response.json()["detail"])
    except (ValueError, KeyError):
        print(e.response.text)
    return

def request_error_handler(e: RequestError) -> None:
    print(f"Request failed: {type(e).__name__} - {e}")
    return