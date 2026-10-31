-- ReconGuard Schema Definition for Exasol Personal
-- Track 01: Money, Risk & Regulation | Team codeleon

CREATE SCHEMA IF NOT EXISTS RECON_GUARD;
OPEN SCHEMA RECON_GUARD;

-- 1. Core Banking System (CBS) Ledger
CREATE TABLE IF NOT EXISTS cbs_transactions (
    txn_id VARCHAR(64) PRIMARY KEY,
    account_id VARCHAR(64),
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    txn_type VARCHAR(10) NOT NULL, -- DEBIT / CREDIT
    booking_time TIMESTAMP NOT NULL,
    reference_id VARCHAR(128),
    channel VARCHAR(32),           -- UPI, NEFT, RTGS, POS, ECOM, SWIFT
    description VARCHAR(256),
    status VARCHAR(20) DEFAULT 'PENDING'
);

-- 2. Payment Gateway & Settlement Feed
CREATE TABLE IF NOT EXISTS gateway_settlements (
    settlement_id VARCHAR(64) PRIMARY KEY,
    gateway_name VARCHAR(32) NOT NULL, -- RAZORPAY, STRIPE, NPCI_UPI, VISA, SWIFT
    batch_id VARCHAR(64),
    gross_amount DECIMAL(18, 2) NOT NULL,
    fee_deducted DECIMAL(18, 2) DEFAULT 0.00,
    net_amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    settlement_time TIMESTAMP NOT NULL,
    external_ref VARCHAR(128),
    narrative VARCHAR(256)
);

-- 3. Production Reconciled Ledger
CREATE TABLE IF NOT EXISTS reconciled_ledger (
    recon_id VARCHAR(64) PRIMARY KEY,
    cbs_txn_id VARCHAR(64),
    settlement_id VARCHAR(64),
    match_type VARCHAR(32) NOT NULL, -- EXACT_1_TO_1, BATCH_1_TO_N, TOLERANCE_FEE, AI_FUZZY_GOVERNED
    matched_amount DECIMAL(18, 2) NOT NULL,
    variance_amount DECIMAL(18, 2) DEFAULT 0.00,
    confidence_score DECIMAL(5, 2) NOT NULL,
    reconciled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_by VARCHAR(64) NOT NULL
);

-- 4. Suspense Breaks Queue
CREATE TABLE IF NOT EXISTS suspense_queue (
    break_id VARCHAR(64) PRIMARY KEY,
    source_table VARCHAR(32) NOT NULL,
    source_id VARCHAR(64) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    booking_time TIMESTAMP NOT NULL,
    break_reason VARCHAR(64) NOT NULL,
    pseudonym_token VARCHAR(64),
    status VARCHAR(20) DEFAULT 'OPEN' -- OPEN, STAGED_IN_SHADOW, RESOLVED, DISPUTED
);

-- 5. Isolated Shadow Branch for Governed AI Write Path
CREATE TABLE IF NOT EXISTS recon_shadow_branch (
    branch_id VARCHAR(64) NOT NULL,
    proposal_id VARCHAR(64) PRIMARY KEY,
    break_id VARCHAR(64) NOT NULL,
    proposed_cbs_id VARCHAR(64),
    proposed_settlement_id VARCHAR(64),
    proposed_adjustment_type VARCHAR(32) NOT NULL,
    proposed_amount DECIMAL(18, 2) NOT NULL,
    ai_confidence DECIMAL(5, 2) NOT NULL,
    ai_rationale VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approval_status VARCHAR(20) DEFAULT 'PENDING_REVIEW'
);

-- 6. Governed Audit Trail & Byte-for-Byte Undo Log
CREATE TABLE IF NOT EXISTS governance_audit_log (
    audit_id VARCHAR(64) PRIMARY KEY,
    branch_id VARCHAR(64) NOT NULL,
    action VARCHAR(32) NOT NULL, -- MERGE, UNDO
    pre_state_hash VARCHAR(64) NOT NULL,
    post_state_hash VARCHAR(64) NOT NULL,
    rows_affected INTEGER NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operator VARCHAR(64) NOT NULL
);
