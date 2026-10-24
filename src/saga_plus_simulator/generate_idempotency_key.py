
from typing import Any

from sqlalchemy.orm import Session

from saga_plus_simulator.models import ProcessedRequests


def create_idempotency_key(object_id: str, method: str) -> str:
    return object_id + method

def save_response(
        id: str,
        method: str,
        path: str,
        response_body: dict[str, Any],
        response_status: int,
        db: Session) -> None:
    request = ProcessedRequests(
        idempotency_key=create_idempotency_key(id, method),
        endpoint=path,
        response_body=response_body,
        response_status=response_status,
    )
    db.add(request)
    db.commit()
    return
def get_cached_response (
        id: str,
        method: str,
        db: Session
) -> dict[str, Any] | None:
    key = create_idempotency_key(id, method)
    existing = db.get(ProcessedRequests, key)
    if existing is None:
        return None
    return existing.response_body

