export interface ReconMetrics {
  total_cbs_count: number;
  total_settlement_count: number;
  exact_matched: number;
  fee_tolerance_matched: number;
  time_drift_matched: number;
  suspense_breaks_count: number;
  total_reconciled_volume: number;
  total_suspense_volume: number;
  sql_execution_time_ms: number;
}

export interface SuspenseBreak {
  break_id: string;
  source_table: string;
  source_id: string;
  account_token: string;
  amount: number;
  channel: string;
  reference_id: string;
  booking_time: string;
  break_reason: string;
  description: string;
  status: string;
}

export interface ReconciledRecord {
  recon_id: string;
  cbs_txn_id: string;
  settlement_id: string;
  match_type: string;
  matched_amount: number;
  variance_amount: number;
  confidence_score: number;
  reconciled_at: string;
  verified_by: string;
}

export interface Proposal {
  proposal_id: string;
  branch_id: string;
  break_id: string;
  proposed_cbs_id: string;
  proposed_settlement_id: string;
  proposed_adjustment_type: string;
  proposed_amount: number;
  ai_confidence: number;
  ai_rationale: string;
  cbs_ref: string;
  gw_ref: string;
  cbs_narrative: string;
  gw_narrative: string;
  created_at: string;
  approval_status: string;
}

export interface AuditEntry {
  audit_id: string;
  branch_id: string;
  action: string;
  pre_state_hash: string;
  post_state_hash: string;
  rows_affected: number;
  executed_at: string;
  operator: string;
}
