"""Copyright (c) Brand.Me, Inc. All rights reserved."""
"""Seed demo data for Brand.Me Minimal Live Slice."""

import os
import sys
from uuid import uuid4

import psycopg2
from psycopg2 import extras


def get_connection_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable must be set")
    return database_url


def main() -> None:
    conn = psycopg2.connect(get_connection_url())
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            demo_user_id = str(uuid4())
            demo_garment_id = str(uuid4())
            demo_facet_id = str(uuid4())
            demo_policy_id = str(uuid4())

            cur.execute(
                """
                INSERT INTO users (user_id, handle, display_name, region_code, persona_warm_cold, persona_sport_couture, trust_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (handle) DO NOTHING
                """,
                (
                    demo_user_id,
                    "demo_creator",
                    "Demo Creator",
                    "us-east1",
                    0.75,
                    0.60,
                    85.00,
                ),
            )

            cur.execute(
                """
                INSERT INTO garments (garment_id, creator_id, current_owner_id, display_name, category, cardano_asset_ref, authenticity_hash, public_esg_score, public_story_snippet)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (garment_id) DO NOTHING
                """,
                (
                    demo_garment_id,
                    demo_user_id,
                    demo_user_id,
                    "Aurora Thread Jacket",
                    "outerwear",
                    "cardano_asset_demo_ref",
                    "hash_demo_authenticity",
                    "AA",
                    "Hand-crafted with recycled fibers for a radiant debut.",
                ),
            )

            cur.execute(
                """
                INSERT INTO garment_passport_facets (facet_id, garment_id, facet_type, facet_payload, is_public_default, cardano_ref)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (facet_id) DO NOTHING
                """,
                (
                    demo_facet_id,
                    demo_garment_id,
                    "ESG",
                    extras.Json(
                        {
                            "esg_score": "AA",
                            "summary": "Certified low-impact dye process",
                        }
                    ),
                    True,
                    "cardano_facet_hash_demo",
                ),
            )

            cur.execute(
                """
                INSERT INTO consent_policies (policy_id, garment_id, visibility_scope, facet_type, allowed)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (policy_id) DO NOTHING
                """,
                (
                    demo_policy_id,
                    demo_garment_id,
                    "public",
                    "ESG",
                    True,
                ),
            )
    finally:
        conn.close()
    print("Seed complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Seed failed: {exc}", file=sys.stderr)
        sys.exit(1)
