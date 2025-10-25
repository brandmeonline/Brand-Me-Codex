"""Placeholder region legality checks."""

from __future__ import annotations

from loguru import logger


ALLOWED_REGIONS = {"us-east1"}


def is_allowed(region_code: str, scope: str):
    """Return True if the provided region allows the resolved scope."""
    allowed = region_code in ALLOWED_REGIONS
    logger.bind(region_code=region_code, scope=scope, allowed=allowed).debug(
        "Checking regional permission"
    )
    return allowed
