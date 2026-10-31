"""
ReconGuard Governed Ledger & Undo Engine
Track 01: Money, Risk & Regulation | ExaThon 2026 | Team codeleon

Implements Drydock-style branch isolation, row-level diff inspection,
governed atomic commits, and byte-for-byte undo.
"""

import json
import uuid
import hashlib
import datetime
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd

class GovernanceLedger:
    def __init__(self, exasol_engine):
        self.engine = exasol_engine
        self.shadow_branches: Dict[str, List[Dict[str, Any]]] = {}
        self.merge_history: List[Dict[str, Any]] = []

    def create_shadow_branch(self, branch_name: Optional[str] = None) -> str:
        """Initializes a new isolated shadow branch for AI proposed fixes."""
        if not branch_name:
            branch_id = f"recon_branch_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            branch_id = branch_name
        self.shadow_branches[branch_id] = []
        return branch_id

    def stage_proposals(self, branch_id: str, proposals: List[Dict[str, Any]]) -> int:
        """Stages AI proposals into the branch without touching production."""
        if branch_id not in self.shadow_branches:
            self.shadow_branches[branch_id] = []
        self.shadow_branches[branch_id].extend(proposals)
        return len(proposals)

    def compute_branch_diff(self, branch_id: str) -> Dict[str, Any]:
        """
        Calculates row-level diff between current production state and proposed branch.
        """
        proposals = self.shadow_branches.get(branch_id, [])
        if not proposals:
            return {"status": "EMPTY_BRANCH", "changes_count": 0, "diff_rows": []}

        diff_rows = []
        for prop in proposals:
            diff_rows.append({
                "proposal_id": prop["proposal_id"],
                "target_cbs_id": prop["proposed_cbs_id"],
                "target_settlement_id": prop["proposed_settlement_id"],
                "action": prop["proposed_adjustment_type"],
                "amount": prop["proposed_amount"],
                "confidence": prop["ai_confidence"],
                "justification": prop["ai_rationale"],
                "cbs_ref": prop.get("cbs_ref", ""),
                "gw_ref": prop.get("gw_ref", "")
            })

        return {
            "status": "READY_FOR_REVIEW",
            "branch_id": branch_id,
            "changes_count": len(diff_rows),
            "total_value": sum(r["amount"] for r in diff_rows),
            "diff_rows": diff_rows
        }

    def _hash_ledger_state(self) -> str:
        """Computes deterministic cryptographic hash of the current reconciled ledger."""
        if self.engine.df_reconciled.empty:
            return hashlib.sha256(b"EMPTY_LEDGER").hexdigest()
        serialized = self.engine.df_reconciled.sort_values(by="recon_id").to_json(orient="records")
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def commit_branch(self, branch_id: str, operator: str = "COMPLIANCE_OFFICER_01") -> Dict[str, Any]:
        """
        Executes governed atomic merge:
        1. Captures pre-state hash
        2. Merges approved proposals into production reconciled ledger
        3. Captures post-state hash
        4. Writes immutable audit entry
        """
        proposals = self.shadow_branches.get(branch_id, [])
        if not proposals:
            return {"success": False, "message": "Branch is empty or does not exist."}

        pre_hash = self._hash_ledger_state()
        snapshot_reconciled = self.engine.df_reconciled.copy()
        snapshot_suspense = self.engine.df_suspense.copy()

        new_reconciled_rows = []
        resolved_break_ids = set()

        for prop in proposals:
            if prop["proposed_adjustment_type"] == "SETTLE_FUZZY_MATCH":
                new_reconciled_rows.append({
                    "recon_id": f"REC_AI_{prop['proposal_id']}",
                    "cbs_txn_id": prop["proposed_cbs_id"],
                    "settlement_id": prop["proposed_settlement_id"],
                    "match_type": "AI_FUZZY_GOVERNED",
                    "matched_amount": prop["proposed_amount"],
                    "variance_amount": 0.00,
                    "confidence_score": prop["ai_confidence"],
                    "reconciled_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "verified_by": "GEMINI_GOVERNED_AGENT"
                })
                resolved_break_ids.add(prop["break_id"])

        if new_reconciled_rows:
            self.engine.df_reconciled = pd.concat([
                self.engine.df_reconciled,
                pd.DataFrame(new_reconciled_rows)
            ], ignore_index=True)

        # Update Suspense queue status
        if not self.engine.df_suspense.empty and resolved_break_ids:
            self.engine.df_suspense.loc[
                self.engine.df_suspense['break_id'].isin(resolved_break_ids), 'status'
            ] = 'RESOLVED_BY_AI'

        post_hash = self._hash_ledger_state()

        audit_entry = {
            "audit_id": f"AUDIT_{uuid.uuid4().hex[:8].upper()}",
            "branch_id": branch_id,
            "action": "GOVERNED_MERGE",
            "pre_state_hash": pre_hash,
            "post_state_hash": post_hash,
            "rows_affected": len(new_reconciled_rows),
            "executed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": operator,
            "_snapshot_reconciled": snapshot_reconciled,
            "_snapshot_suspense": snapshot_suspense,
            "_resolved_break_ids": list(resolved_break_ids)
        }
        self.merge_history.append(audit_entry)
        self.engine.audit_log.append({k: v for k, v in audit_entry.items() if not k.startswith("_")})

        return {
            "success": True,
            "audit_id": audit_entry["audit_id"],
            "pre_state_hash": pre_hash,
            "post_state_hash": post_hash,
            "rows_merged": len(new_reconciled_rows),
            "message": f"Successfully merged {len(new_reconciled_rows)} rows to production ledger."
        }

    def byte_for_byte_undo(self, branch_id: str, operator: str = "COMPLIANCE_OFFICER_01") -> Dict[str, Any]:
        """
        Executes exact byte-for-byte rollback:
        Restores previous ledger state snapshot and verifies pre-state hash equality.
        """
        matching_entries = [e for e in self.merge_history if e["branch_id"] == branch_id and e["action"] == "GOVERNED_MERGE"]
        if not matching_entries:
            return {"success": False, "message": "No active merge found for this branch to undo."}

        target_entry = matching_entries[-1]
        pre_rollback_hash = self._hash_ledger_state()

        # Restore snapshots
        self.engine.df_reconciled = target_entry["_snapshot_reconciled"].copy()
        self.engine.df_suspense = target_entry["_snapshot_suspense"].copy()

        restored_hash = self._hash_ledger_state()
        exact_match = (restored_hash == target_entry["pre_state_hash"])

        undo_audit = {
            "audit_id": f"AUDIT_UNDO_{uuid.uuid4().hex[:8].upper()}",
            "branch_id": branch_id,
            "action": "BYTE_FOR_BYTE_UNDO",
            "pre_state_hash": pre_rollback_hash,
            "post_state_hash": restored_hash,
            "rows_affected": target_entry["rows_affected"],
            "executed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": operator
        }
        self.merge_history.append(undo_audit)
        self.engine.audit_log.append(undo_audit)

        return {
            "success": True,
            "exact_byte_match": exact_match,
            "restored_hash": restored_hash,
            "expected_hash": target_entry["pre_state_hash"],
            "rows_reverted": target_entry["rows_affected"],
            "message": "Byte-for-byte undo successful. Production ledger restored to exact previous state."
        }
