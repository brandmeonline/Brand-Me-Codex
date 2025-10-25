-- Copyright (c) Brand.Me, Inc. All rights reserved.
-- Migration: Initial schema for Brand.Me Minimal Live Slice

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    handle TEXT UNIQUE NOT NULL,
    display_name TEXT,
    did_cardano TEXT NULL,
    region_code TEXT,
    persona_warm_cold NUMERIC(3,2),
    persona_sport_couture NUMERIC(3,2),
    trust_score NUMERIC(6,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS garments (
    garment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID REFERENCES users(user_id),
    current_owner_id UUID REFERENCES users(user_id),
    display_name TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    cardano_asset_ref TEXT,
    authenticity_hash TEXT,
    public_esg_score TEXT,
    public_story_snippet TEXT
);

CREATE TABLE IF NOT EXISTS garment_passport_facets (
    facet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    garment_id UUID REFERENCES garments(garment_id),
    facet_type TEXT,
    facet_payload JSONB,
    is_public_default BOOLEAN NOT NULL DEFAULT FALSE,
    midnight_ref TEXT,
    cardano_ref TEXT,
    last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS consent_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    garment_id UUID REFERENCES garments(garment_id),
    visibility_scope TEXT,
    facet_type TEXT,
    allowed BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scan_event (
    scan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scanner_user_id UUID REFERENCES users(user_id),
    garment_id UUID REFERENCES garments(garment_id),
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_scope TEXT,
    policy_version TEXT,
    region_code TEXT,
    shown_facets JSONB
);

CREATE TABLE IF NOT EXISTS chain_anchor (
    anchor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID REFERENCES scan_event(scan_id),
    cardano_tx_hash TEXT,
    cardano_payload_ref TEXT,
    midnight_tx_hash TEXT,
    midnight_payload_ref TEXT,
    crosschain_root_hash TEXT,
    anchored_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    related_scan_id UUID REFERENCES scan_event(scan_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    actor_type TEXT,
    decision_summary TEXT,
    decision_detail JSONB,
    risk_flagged BOOLEAN DEFAULT FALSE,
    escalated_to_human BOOLEAN DEFAULT FALSE,
    human_approver_id UUID NULL REFERENCES users(user_id),
    prev_hash TEXT NULL,
    entry_hash TEXT NOT NULL
);
