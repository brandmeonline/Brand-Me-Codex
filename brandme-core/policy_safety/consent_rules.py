"""Placeholder consent rules for scope resolution."""

from __future__ import annotations

from loguru import logger


def get_scope(scanner_user_id: str, garment_id: str) -> str:
    """Return the visibility scope for the scanner with respect to the garment."""
    logger.bind(
        scanner_user=scanner_user_id[:8] + "…",
        garment_id=garment_id[:8] + "…",
    ).debug("Determining scope")
    return "public"
