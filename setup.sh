#!/usr/bin/env bash
# setup.sh — One-command setup for PeakFlow Analytics.
# Usage: bash setup.sh
set -euo pipefail

echo "╔══════════════════════════════════════════════╗"
echo "║   PeakFlow Analytics — Setup                  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. Python environment ─────────────────────────────────────────────
echo ":: Setting up Python virtual environment..."
if [ ! -d venv ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✓ Python deps installed"
echo ""

# ── 2. Environment file ───────────────────────────────────────────────
echo ":: Creating .env from .env.example (edit later for AI features)..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✓ .env created (API keys are optional)"
else
    echo "   - .env already exists, skipping"
fi
echo ""

# ── 3. Frontend ───────────────────────────────────────────────────────
echo ":: Installing frontend dependencies..."
if command -v bun &> /dev/null; then
    cd frontend && bun install && cd ..
    echo "   ✓ Frontend deps installed (Bun)"
else
    echo "   ⚠ Bun not found. Install it: https://bun.sh"
    echo "     Then run: cd frontend && bun install"
fi
echo ""

# ── 4. Verify model ───────────────────────────────────────────────────
echo ":: Verifying model artifacts..."
if [ -f app/models/cross_station_model.pth ]; then
    python3 -c "
import sys
sys.path.insert(0, '.')
from app.services.cross_station_service import predict_flood_risk
r = predict_flood_risk('chisapani', 22, 18, 72, 392)
print(f'   ✓ Model loaded — Chisapani example: {r[\"risk_level\"]} risk ({r[\"probability\"]:.1%})')
print(f'   ✓ Stations supported: {len(r[\"station_flow_stats\"])} stats precomputed')
" || {
    echo "   ⚠ Cross-station model missing — run: make retrain"
    exit 1
}
fi
echo ""

# ── 5. Quick test ─────────────────────────────────────────────────────
echo ":: Testing backend..."
python3 -c "
from app.services.nasa_service import fetch_live_weather
# Just check import works, don't call NASA from setup
print('   ✓ NASA POWER service importable')
from app.services.compliance_engine import evaluate_ifc_compliance
result = evaluate_ifc_compliance(392, 280)
print(f'   ✓ Compliance engine OK — compliance: {result[\"ps4_status\"]}')
"
echo ""

echo "╔══════════════════════════════════════════════╗"
echo "║   Setup complete!                              ║"
echo "║                                                ║"
echo "║   Start the demo:                              ║"
echo "║     make run-demo                              ║"
echo "║                                                ║"
echo "║   Or start separately:                         ║"
echo "║     make run-backend    (terminal 1)            ║"
echo "║     make run-frontend   (terminal 2)            ║"
echo "╚══════════════════════════════════════════════╝"
