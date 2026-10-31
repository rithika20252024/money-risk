"""
ReconGuard High-Performance Backend API Server
Serves the React + TypeScript Frontend and bridges Exasol Personal & Gemini Flash
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

from reconstruct_dataset import create_synthetic_financial_dataset
from exasol_engine import ExasolReconEngine, ReconMetrics
from agent_orchestrator import GeminiFlashReconAgent
from governance_ledger import GovernanceLedger

# Global application state
engine = ExasolReconEngine()
ledger = GovernanceLedger(engine)
agent = GeminiFlashReconAgent()
active_branch = None
staged_proposals = []
latest_metrics = ReconMetrics()

# Initialize with default 5000 records on boot
initial_cbs, initial_gw = create_synthetic_financial_dataset(n_records=5000)
engine.ingest_data(initial_cbs, initial_gw)
latest_metrics = engine.run_deterministic_reconciliation()

class ReconAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def _send_json(self, data: Any, status_code=200):
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

    def do_GET(self):
        global engine, ledger, agent, active_branch, staged_proposals, latest_metrics
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self._send_json({
                "is_exasol_live": engine.is_connected,
                "engine_mode": "Live Exasol Personal" if engine.is_connected else "High-Fidelity In-Memory Columnar Engine",
                "active_branch": active_branch,
                "ledger_hash": ledger._hash_ledger_state(),
                "metrics": {
                    "total_cbs_count": latest_metrics.total_cbs_count,
                    "total_settlement_count": latest_metrics.total_settlement_count,
                    "exact_matched": latest_metrics.exact_matched,
                    "fee_tolerance_matched": latest_metrics.fee_tolerance_matched,
                    "time_drift_matched": latest_metrics.time_drift_matched,
                    "suspense_breaks_count": latest_metrics.suspense_breaks_count,
                    "total_reconciled_volume": latest_metrics.total_reconciled_volume,
                    "total_suspense_volume": latest_metrics.total_suspense_volume,
                    "sql_execution_time_ms": latest_metrics.sql_execution_time_ms
                }
            })

        elif path == "/api/breaks":
            self._send_json(engine.get_suspense_breaks())

        elif path == "/api/reconciled":
            self._send_json(engine.get_reconciled_records()[:100]) # return top 100 for fast UI rendering

        elif path == "/api/branch/diff":
            if not active_branch:
                self._send_json({"status": "NO_ACTIVE_BRANCH", "diff_rows": [], "changes_count": 0, "total_value": 0})
            else:
                diff = ledger.compute_branch_diff(active_branch)
                diff["current_ledger_hash"] = ledger._hash_ledger_state()
                self._send_json(diff)

        elif path == "/api/proposals":
            self._send_json(staged_proposals)

        elif path == "/api/audit":
            self._send_json(ledger.engine.audit_log)

        else:
            # Serve frontend/dist static files
            import os
            import mimetypes
            dist_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
            rel_path = path.lstrip("/")
            file_path = os.path.join(dist_dir, rel_path) if rel_path else os.path.join(dist_dir, "index.html")

            if os.path.exists(file_path) and os.path.isfile(file_path):
                mime, _ = mimetypes.guess_type(file_path)
                with open(file_path, "rb") as f:
                    content = f.read()
                self._set_headers(200, content_type=mime or "application/octet-stream")
                self.wfile.write(content)
            elif os.path.exists(os.path.join(dist_dir, "index.html")):
                with open(os.path.join(dist_dir, "index.html"), "rb") as f:
                    content = f.read()
                self._set_headers(200, content_type="text/html")
                self.wfile.write(content)
            else:
                self._send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        global engine, ledger, agent, active_branch, staged_proposals, latest_metrics
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json()

        if path == "/api/ingest":
            count = int(body.get("count", 5000))
            cbs, gw = create_synthetic_financial_dataset(n_records=count)
            engine.ingest_data(cbs, gw)
            active_branch = None
            staged_proposals = []
            latest_metrics = engine.run_deterministic_reconciliation()
            self._send_json({
                "message": f"Successfully ingested {count:,} transactions into Exasol Personal",
                "cbs_count": len(cbs),
                "gw_count": len(gw),
                "metrics": {
                    "total_cbs_count": latest_metrics.total_cbs_count,
                    "exact_matched": latest_metrics.exact_matched,
                    "fee_tolerance_matched": latest_metrics.fee_tolerance_matched,
                    "suspense_breaks_count": latest_metrics.suspense_breaks_count,
                    "sql_execution_time_ms": latest_metrics.sql_execution_time_ms
                }
            })

        elif path == "/api/reconcile":
            latest_metrics = engine.run_deterministic_reconciliation()
            self._send_json({
                "success": True,
                "execution_ms": latest_metrics.sql_execution_time_ms,
                "matched_count": latest_metrics.exact_matched + latest_metrics.fee_tolerance_matched + latest_metrics.time_drift_matched,
                "breaks_count": latest_metrics.suspense_breaks_count
            })

        elif path == "/api/agent/propose":
            active_branch = ledger.create_shadow_branch()
            breaks = engine.get_suspense_breaks()
            unmatched_gw = engine.get_unmatched_gateway_records()
            staged_proposals = agent.analyze_breaks_and_propose(breaks, unmatched_gw, active_branch)
            ledger.stage_proposals(active_branch, staged_proposals)
            self._send_json({
                "success": True,
                "branch_id": active_branch,
                "proposals_count": len(staged_proposals),
                "proposals": staged_proposals
            })

        elif path == "/api/branch/merge":
            if not active_branch:
                self._send_json({"success": False, "message": "No active branch to merge"}, 400)
                return
            result = ledger.commit_branch(active_branch, operator=body.get("operator", "COMPLIANCE_OFFICER_01"))
            self._send_json(result)

        elif path == "/api/branch/undo":
            if not active_branch:
                self._send_json({"success": False, "message": "No active branch to undo"}, 400)
                return
            result = ledger.byte_for_byte_undo(active_branch, operator=body.get("operator", "COMPLIANCE_OFFICER_01"))
            self._send_json(result)

        else:
            self._send_json({"error": "Endpoint not found"}, 404)

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ReconAPIHandler)
    print(f"[ReconGuard API] Server listening on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
