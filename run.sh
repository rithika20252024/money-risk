#!/usr/bin/env bash
# ReconGuard Quickstart & Runner Script
# Track 01: Money, Risk & Regulation | ExaThon 2026 | Team codeleon

set -e

echo "=========================================================="
echo "🛡️  ReconGuard: Autonomous Financial Reconciliation Engine"
echo "    ExaThon India 2026 | Track 01: Money, Risk & Regulation"
echo "    Team: codeleon"
echo "=========================================================="

# Check if venv exists, otherwise create it
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating Python virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
else
    echo "[1/3] Virtual environment detected (.venv)."
fi

# Run automated tests
echo "[2/3] Running automated verification test suite..."
PYTHONPATH=. .venv/bin/pytest tests/test_reconciliation.py -v

# Launch ReconGuard React + TypeScript Dashboard
echo "[3/3] Launching ReconGuard React Dashboard at http://localhost:8000..."
echo "Open http://localhost:8000 in your browser to explore the dashboard."
.venv/bin/python3 server.py
