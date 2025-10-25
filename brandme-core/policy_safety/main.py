"""Policy & safety FastAPI service."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from common.logger import ensure_request_id, get_logger, redact_user_id
from policy_safety import consent_rules, region_rules

app = FastAPI(title="Brand.Me Policy & Safety")
logger = get_logger("policy-safety")


class PolicyCheckRequest(BaseModel):
    scanner_user_id: uuid.UUID
    garment_id: uuid.UUID
    region_code: str = Field(..., min_length=2)
    action: str = Field(..., min_length=1)


class PolicyCheckResponse(BaseModel):
    decision: str
    resolved_scope: str
    policy_version: str


@app.post("/policy/check", response_model=PolicyCheckResponse)
async def policy_check(request: Request, payload: PolicyCheckRequest) -> Any:
    scope = consent_rules.get_scope(str(payload.scanner_user_id), str(payload.garment_id))
    legality = region_rules.is_allowed(payload.region_code, scope)

    if legality is True:
        decision = "allow"
    elif legality is False:
        decision = "deny"
    else:
        decision = "escalate"

    response_body = PolicyCheckResponse(
        decision=decision,
        resolved_scope=scope,
        policy_version="policy_v1_us-east1",
    )

    response = JSONResponse(response_body.dict())
    request_id = ensure_request_id(request, response)

    logger.bind(
        request_id=request_id,
        scanner_user=redact_user_id(str(payload.scanner_user_id)),
        garment_id=str(payload.garment_id)[:8] + "…",
        region_code=payload.region_code,
        decision=decision,
    ).info("Policy decision computed")

    # TODO: escalate -> queue human/compliance review.
    # TODO: Never directly return private Midnight-only data here.

    return response


@app.get("/healthz")
async def healthcheck(request: Request) -> Response:
    response = JSONResponse({"status": "ok"})
    ensure_request_id(request, response)
    return response
