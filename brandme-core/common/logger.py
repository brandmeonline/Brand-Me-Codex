"""Common logging utilities for Brand.Me core services."""

from __future__ import annotations

import uuid
from typing import Optional

from loguru import logger


def get_logger(service_name: str):
    """Return a logger configured for the given service."""
    configured = logger.bind(service=service_name)
    configured = configured.opt(depth=1)
    return configured


def redact_user_id(user_id: Optional[str]) -> Optional[str]:
    """Return a redacted representation of a user identifier."""
    if not user_id:
        return None
    return f"{user_id[:8]}…"


def ensure_request_id(request, response) -> str:
    """Ensure X-Request-Id is present on the request/response."""
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        request_id = str(uuid.uuid4())
    response.headers["X-Request-Id"] = request_id
    return request_id


__all__ = ["get_logger", "redact_user_id", "ensure_request_id"]
