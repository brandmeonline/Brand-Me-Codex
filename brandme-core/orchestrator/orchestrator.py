"""Orchestrator worker for allowed scan events."""

from __future__ import annotations

import datetime as dt
import json
import os
import uuid
from typing import Dict, List

import psycopg2
from psycopg2 import extras

from common.logger import get_logger, redact_user_id

logger = get_logger("orchestrator")


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    return conn


def call_knowledge_service(garment_id: str, scope: str) -> List[Dict[str, object]]:
    """Placeholder knowledge service call returning allowed facets."""
    logger.bind(garment_id=garment_id[:8] + "…", scope=scope).debug(
        "Fetching allowed facets"
    )
    return [
        {
            "facet_type": "ESG",
            "facet_payload_preview": {
                "summary": "Sustainability certified",
                "scope": scope,
            },
        }
    ]


def call_tx_builder(scan_id: str, garment_id: str, scope: str, policy_version: str) -> Dict[str, str]:
    """Placeholder TX builder call that returns mock hashes."""
    logger.bind(
        scan_id=scan_id,
        garment_id=garment_id[:8] + "…",
        scope=scope,
        policy_version=policy_version,
    ).debug("Building cross-chain transaction")
    return {
        "cardano_tx_hash": f"cardano-{uuid.uuid4().hex[:16]}",
        "midnight_tx_hash": f"midnight-{uuid.uuid4().hex[:16]}",
        "crosschain_root_hash": f"root-{uuid.uuid4().hex[:16]}",
    }


def call_compliance_audit_log(
    scan_id: str,
    decision_summary: str,
    decision_detail: Dict[str, object],
    risk_flagged: bool,
    escalated_to_human: bool,
) -> None:
    """Placeholder compliance audit logging."""
    logger.bind(
        scan_id=scan_id,
        decision_summary=decision_summary,
        risk_flagged=risk_flagged,
        escalated_to_human=escalated_to_human,
    ).debug("Logging compliance decision")


def call_compliance_anchor_chain(scan_id: str, tx_hashes: Dict[str, str]) -> None:
    """Placeholder compliance anchor linkage."""
    logger.bind(
        scan_id=scan_id,
        cardano_tx_hash=tx_hashes.get("cardano_tx_hash"),
    ).debug("Linking chain anchors")


def process_allowed_scan(decision_packet: Dict[str, str]) -> Dict[str, object]:
    """Persist an allowed scan event and notify downstream systems."""
    # TODO: future: escalate path to human review if decision == 'escalate'.
    scan_id = decision_packet["scan_id"]
    scanner_user_id = decision_packet["scanner_user_id"]
    garment_id = decision_packet["garment_id"]
    resolved_scope = decision_packet["resolved_scope"]
    policy_version = decision_packet["policy_version"]
    region_code = decision_packet["region_code"]
    occurred_at = decision_packet.get("occurred_at") or dt.datetime.utcnow().isoformat()

    shown_facets = call_knowledge_service(garment_id, resolved_scope)
    tx_hashes = call_tx_builder(scan_id, garment_id, resolved_scope, policy_version)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO scan_event (
                    scan_id,
                    scanner_user_id,
                    garment_id,
                    occurred_at,
                    resolved_scope,
                    policy_version,
                    region_code,
                    shown_facets
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (scan_id) DO NOTHING
                """,
                (
                    scan_id,
                    scanner_user_id,
                    garment_id,
                    occurred_at,
                    resolved_scope,
                    policy_version,
                    region_code,
                    extras.Json(shown_facets),
                ),
            )
    finally:
        conn.close()

    call_compliance_audit_log(
        scan_id=scan_id,
        decision_summary=f"policy allowed scope {resolved_scope}",
        decision_detail={
            "policy_version": policy_version,
            "region_code": region_code,
        },
        risk_flagged=False,
        escalated_to_human=False,
    )
    call_compliance_anchor_chain(scan_id, tx_hashes)

    logger.bind(
        scan_id=scan_id,
        scanner_user=redact_user_id(scanner_user_id),
        shown_facets_count=len(shown_facets),
    ).info("Processed allowed scan")

    return {
        "status": "ok",
        "scan_id": scan_id,
        "shown_facets_count": len(shown_facets),
        "cardano_tx_hash": tx_hashes["cardano_tx_hash"],
        "midnight_tx_hash": tx_hashes["midnight_tx_hash"],
        "crosschain_root_hash": tx_hashes["crosschain_root_hash"],
    }


if __name__ == "__main__":
    demo_packet = {
        "scan_id": str(uuid.uuid4()),
        "scanner_user_id": str(uuid.uuid4()),
        "garment_id": str(uuid.uuid4()),
        "resolved_scope": "public",
        "policy_version": "policy_v1_us-east1",
        "region_code": os.getenv("REGION_DEFAULT", "us-east1"),
        "occurred_at": dt.datetime.utcnow().isoformat(),
    }
    result = process_allowed_scan(demo_packet)
    print(json.dumps(result, indent=2))
