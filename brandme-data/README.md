# brandme-data

brandme-data is the authoritative database schema for Brand.Me, Inc., powering verifiable fashion identity with immutable provenance and consent-aware visibility. This repository defines the Postgres structure that underpins the Minimal Live Slice (MLS) and ensures consistent data modeling across the platform.

## Schema Overview

The migrations in this repository create the following tables:

- `users`
- `garments`
- `garment_passport_facets`
- `consent_policies`
- `scan_event`
- `chain_anchor`
- `audit_log`

These tables store user personas, garment metadata, passport facets, consent policies, scan events, blockchain anchors, and compliance audit history. They enable downstream services to enforce policy decisions, log provenance, and expose transparency portals without leaking private data.

## Service Integrations

All Brand.Me services share this schema:

- **brandme-gateway** ingests garment scans and writes initial events.
- **brandme-core** resolves intents, evaluates policy, and orchestrates scan flows.
- **brandme-agents** surfaces identity, knowledge, and compliance data.
- **brandme-chain** anchors proofs to Cardano and Midnight.
- **brandme-console** renders governance and transparency experiences.

## Local Development

### Prerequisites

- PostgreSQL with the `uuid-ossp` extension available.
- Python 3.12+
- `psql` CLI

### Running Migrations

1. Ensure your Postgres instance is running and accessible.
2. Export the database URL:

   ```bash
   export DATABASE_URL="postgresql://brandme_user:brandme_pass@localhost:5432/brandme"
   ```

3. Apply migrations with `psql`:

   ```bash
   for file in migrations/*.sql; do
       echo "Applying $file";
       psql "$DATABASE_URL" -f "$file";
   done
   ```

### Seeding Demo Data

1. Install dependencies (creates a local virtual environment if desired).

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r seed/requirements.txt
   ```

2. Run the seed script:

   ```bash
   export DATABASE_URL="postgresql://brandme_user:brandme_pass@localhost:5432/brandme"
   python seed/seed_demo.py
   ```

The script inserts a demo user, garment, passport facet, and consent policy to bootstrap the MLS workflow.
