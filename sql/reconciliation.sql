-- ReconGuard High-Throughput Reconciliation Queries for Exasol Personal
-- Optimized for In-Memory Vectorized Columnar Execution

-- Query 1: Exact 1-to-1 Deterministic Matching
-- Matches CBS transaction directly to Settlement on reference and exact amount
SELECT 
    c.txn_id AS cbs_txn_id,
    g.settlement_id,
    'EXACT_1_TO_1' AS match_type,
    c.amount AS matched_amount,
    0.00 AS variance_amount,
    100.00 AS confidence_score,
    'EXASOL_DETERMINISTIC_SQL' AS verified_by
FROM cbs_transactions c
JOIN gateway_settlements g
    ON c.reference_id = g.external_ref
   AND c.amount = g.gross_amount
WHERE c.status = 'PENDING';

-- Query 2: Fee-Tolerance Reconciliations (Gateway Fee Discrepancy)
-- Matches transactions where CBS records gross amount but Settlement arrives net of gateway MDR (Merchant Discount Rate)
SELECT 
    c.txn_id AS cbs_txn_id,
    g.settlement_id,
    'TOLERANCE_FEE' AS match_type,
    g.net_amount AS matched_amount,
    g.fee_deducted AS variance_amount,
    98.50 AS confidence_score,
    'EXASOL_DETERMINISTIC_SQL' AS verified_by
FROM cbs_transactions c
JOIN gateway_settlements g
    ON c.reference_id = g.external_ref
   AND c.amount = (g.net_amount + g.fee_deducted)
   AND c.status = 'PENDING'
   AND c.txn_id NOT IN (SELECT cbs_txn_id FROM reconciled_ledger);

-- Query 3: Time-Drift Window Matching (Transactions settled across cutoff window, within 72 hrs)
SELECT 
    c.txn_id AS cbs_txn_id,
    g.settlement_id,
    'TIME_DRIFT_WINDOW' AS match_type,
    c.amount AS matched_amount,
    0.00 AS variance_amount,
    95.00 AS confidence_score,
    'EXASOL_DETERMINISTIC_SQL' AS verified_by
FROM cbs_transactions c
JOIN gateway_settlements g
    ON c.reference_id = g.external_ref
   AND c.amount = g.gross_amount
   AND ABS(DAYS_BETWEEN(c.booking_time, g.settlement_time)) <= 3
WHERE c.status = 'PENDING'
  AND c.txn_id NOT IN (SELECT cbs_txn_id FROM reconciled_ledger);

-- Query 4: Unmatched Suspense Breaks Extraction (Dispatched to Governed AI Layer)
SELECT 
    c.txn_id,
    c.amount,
    c.currency,
    c.booking_time,
    c.reference_id,
    c.channel,
    c.description,
    CASE 
        WHEN c.reference_id IS NULL OR LENGTH(c.reference_id) < 5 THEN 'MALFORMED_OR_MISSING_REF'
        WHEN c.amount > 500000.00 THEN 'HIGH_VALUE_AUDIT_HOLD'
        ELSE 'UNMATCHED_EXTERNAL_BREAK'
    END AS break_reason
FROM cbs_transactions c
WHERE c.status = 'PENDING'
  AND c.txn_id NOT IN (SELECT cbs_txn_id FROM reconciled_ledger WHERE cbs_txn_id IS NOT NULL);
