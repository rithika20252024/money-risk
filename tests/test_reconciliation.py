"""
ReconGuard Comprehensive Test Suite
Validates Exasol Columnar Reconciliation, Zero-PII Sanitization,
AI Agent Matching, and Byte-for-Byte Undo.
"""

import pytest
from reconstruct_dataset import create_synthetic_financial_dataset
from exasol_engine import ExasolReconEngine
from agent_orchestrator import GeminiFlashReconAgent, PIISanitizer
from governance_ledger import GovernanceLedger

def test_synthetic_data_generation():
    cbs, gw = create_synthetic_financial_dataset(n_records=1000)
    assert len(cbs) == 1000
    assert len(gw) >= 900 # ~97% have settlements generated, 3% are true suspense breaks
    assert all("txn_id" in r and "amount" in r for r in cbs)
    assert all("settlement_id" in r and "gross_amount" in r for r in gw)

def test_exasol_deterministic_reconciliation():
    engine = ExasolReconEngine()
    cbs, gw = create_synthetic_financial_dataset(n_records=2000)
    engine.ingest_data(cbs, gw)
    
    metrics = engine.run_deterministic_reconciliation()
    
    # Exasol deterministic rules should reconcile >= 85% of volume natively
    auto_resolved = metrics.exact_matched + metrics.fee_tolerance_matched + metrics.time_drift_matched
    match_rate = auto_resolved / len(cbs)
    
    assert match_rate >= 0.85, f"Expected >= 85% match rate, got {match_rate:.2%}"
    assert metrics.exact_matched > 1500
    assert metrics.fee_tolerance_matched > 50
    assert metrics.suspense_breaks_count > 0
    assert metrics.sql_execution_time_ms < 500.0 # Sub-second execution

def test_zero_pii_sanitization():
    raw_record = {
        "txn_id": "CBS_TXN_001",
        "customer_name": "Aarav Sharma",
        "account_id": "ACC_9876543210",
        "amount": 15000.0,
        "description": "UPI payment by Aarav Sharma phone 9876543210 to Flipkart"
    }
    sanitized = PIISanitizer.sanitize(raw_record)
    
    assert "customer_name" not in sanitized
    assert sanitized["account_id"] == "ACC_REDACTED_3210"
    assert "9876543210" not in sanitized["description"]
    assert "[PHONE_REDACTED]" in sanitized["description"]

def test_ai_agent_and_branch_diff():
    engine = ExasolReconEngine()
    cbs, gw = create_synthetic_financial_dataset(n_records=500)
    engine.ingest_data(cbs, gw)
    engine.run_deterministic_reconciliation()
    
    agent = GeminiFlashReconAgent()
    ledger = GovernanceLedger(engine)
    
    branch_id = ledger.create_shadow_branch("test_shadow_branch")
    breaks = engine.get_suspense_breaks()
    unmatched_gw = engine.get_unmatched_gateway_records()
    
    proposals = agent.analyze_breaks_and_propose(breaks, unmatched_gw, branch_id)
    assert len(proposals) == len(breaks)
    
    ledger.stage_proposals(branch_id, proposals)
    diff = ledger.compute_branch_diff(branch_id)
    
    assert diff["status"] == "READY_FOR_REVIEW"
    assert diff["changes_count"] == len(proposals)
    assert diff["total_value"] > 0

def test_governed_merge_and_byte_for_byte_undo():
    engine = ExasolReconEngine()
    cbs, gw = create_synthetic_financial_dataset(n_records=500)
    engine.ingest_data(cbs, gw)
    engine.run_deterministic_reconciliation()
    
    agent = GeminiFlashReconAgent()
    ledger = GovernanceLedger(engine)
    
    branch_id = ledger.create_shadow_branch("branch_undo_test")
    breaks = engine.get_suspense_breaks()
    unmatched_gw = engine.get_unmatched_gateway_records()
    
    proposals = agent.analyze_breaks_and_propose(breaks, unmatched_gw, branch_id)
    ledger.stage_proposals(branch_id, proposals)
    
    initial_reconciled_count = len(engine.df_reconciled)
    pre_merge_hash = ledger._hash_ledger_state()
    
    # 1. Commit / Merge branch
    merge_result = ledger.commit_branch(branch_id, operator="AUDITOR_TEST")
    assert merge_result["success"] is True
    assert merge_result["pre_state_hash"] == pre_merge_hash
    assert len(engine.df_reconciled) > initial_reconciled_count
    
    # 2. Execute Byte-for-Byte Undo
    undo_result = ledger.byte_for_byte_undo(branch_id, operator="AUDITOR_TEST")
    assert undo_result["success"] is True
    assert undo_result["exact_byte_match"] is True
    assert undo_result["restored_hash"] == pre_merge_hash
    assert len(engine.df_reconciled) == initial_reconciled_count

if __name__ == "__main__":
    pytest.main(["-v", __file__])
