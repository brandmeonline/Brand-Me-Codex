"""ai-brain-hub FastAPI service for intent normalization."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from common.logger import ensure_request_id, get_logger, redact_user_id

app = FastAPI(title="Brand.Me AI Brain Hub")
logger = get_logger("ai-brain-hub")


class IntentResolveRequest(BaseModel):
    scan_id: uuid.UUID = Field(..., description="Unique scan identifier")
    scanner_user_id: uuid.UUID = Field(..., description="UUID of the scanning user")
    garment_tag: str = Field(..., min_length=1, description="Garment tag scanned by the user")
    region_code: str = Field(..., min_length=2, description="Region code from request context")


class IntentResolveResponse(BaseModel):
    action: str = Field("request_passport_view", const=True)
    garment_id: uuid.UUID
    scanner_user_id: uuid.UUID


def lookup_garment_id(garment_tag: str) -> uuid.UUID:
    """Placeholder garment lookup that returns a deterministic UUID."""
    namespace = uuid.UUID("00000000-0000-0000-0000-000000000001")
    return uuid.uuid5(namespace, garment_tag)


@app.post("/intent/resolve", response_model=IntentResolveResponse)
async def resolve_intent(request: Request, payload: IntentResolveRequest) -> Any:
    response_body = IntentResolveResponse(
        garment_id=lookup_garment_id(payload.garment_tag),
        scanner_user_id=payload.scanner_user_id,
    )
    response = JSONResponse(response_body.dict())
    request_id = ensure_request_id(request, response)

    logger.bind(
        request_id=request_id,
        scan_id=str(payload.scan_id),
        scanner_user=redact_user_id(str(payload.scanner_user_id)),
        region_code=payload.region_code,
    ).info("Resolved garment intent")
    return response


@app.get("/healthz")
async def healthcheck(request: Request) -> Response:
    response = JSONResponse({"status": "ok"})
    ensure_request_id(request, response)
    return response
