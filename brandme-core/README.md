# brandme-core

brandme-core hosts the core orchestration services for Brand.Me, Inc. It determines garment intent, evaluates policy and safety rules, and coordinates downstream systems that reveal provenance facets while maintaining auditability.

## Services

### ai-brain-hub
- FastAPI microservice that normalizes scan intents.
- Endpoint: `POST /intent/resolve`
- Resolves a `garment_id` from the submitted `garment_tag` via `lookup_garment_id()` placeholder logic.
- Responds with `{ action: "request_passport_view", garment_id, scanner_user_id }` and always sets an `X-Request-Id` header (reusing an incoming header or generating a UUID).

Run locally:
```bash
uvicorn ai_brain_hub.main:app --host 0.0.0.0 --port 8000
```

### policy-safety
- FastAPI service that verifies consent-driven visibility and regional restrictions before any reveal.
- Endpoint: `POST /policy/check`
- Uses placeholder modules `consent_rules` and `region_rules` to determine `resolved_scope` and whether the reveal is legal.
- Returns `{ decision, resolved_scope, policy_version }` with `X-Request-Id` header propagation.

Run locally:
```bash
uvicorn policy_safety.main:app --host 0.0.0.0 --port 8001
```

### orchestrator
- Python module that executes when a scan is allowed.
- Inserts a `scan_event` row, queries downstream services for allowed facets, anchors cross-chain proofs, and notifies compliance audit stubs.
- `process_allowed_scan(decision_packet)` coordinates the data flow; execute the module directly for a demo run.

Run demo:
```bash
python orchestrator/orchestrator.py
```

## Environment Variables

Create a `.env` or export the following variables:

- `DATABASE_URL` – Postgres connection string with UUID + JSONB support.
- `REGION_DEFAULT` – Default region code (e.g., `us-east1`).
- `KNOWLEDGE_SERVICE_URL` – Base URL for the knowledge service.
- `TX_BUILDER_URL` – Base URL for the chain transaction builder.
- `COMPLIANCE_AUDIT_URL` – Base URL for the compliance audit service.

Load them locally with `source .env`.

## Development

Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Lint placeholder:
```bash
flake8 || echo "TODO: configure linting"
```

Run tests (when added) with `pytest`.

## Notes
- TODO: Integrate Cardano DID minting during account onboarding.
- TODO: Expand policy handling for additional regions beyond `us-east1`.
- TODO: Implement escalation workflows that route `escalate` decisions to human reviewers.
