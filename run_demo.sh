#!/usr/bin/env bash
# run_demo.sh — One-command demo for PeakFlow Analytics.
# Starts backend + frontend, runs a sample prediction, prints URLs.
set -euo pipefail

echo "╔══════════════════════════════════════════════╗"
echo "║   PeakFlow Analytics — Demo                   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

CLEANUP_ON_EXIT=false
cleanup() {
    if [ "$CLEANUP_ON_EXIT" = true ]; then
        echo ""
        echo ":: Shutting down..."
        kill "$BACKEND_PID" 2>/dev/null || true
        kill "$FRONTEND_PID" 2>/dev/null || true
        echo "   Done."
    fi
}
trap cleanup EXIT

# ── 1. Activate venv ──────────────────────────────────────────────────
if [ ! -d venv ]; then
    echo "❌ Run 'bash setup.sh' first."
    exit 1
fi
source venv/bin/activate

# ── 2. Start backend ──────────────────────────────────────────────────
echo ":: Starting backend..."
python run.py &
BACKEND_PID=$!
CLEANUP_ON_EXIT=true
sleep 3

if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Backend running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi
echo ""

# ── 3. Start frontend (if Bun is available) ───────────────────────────
if command -v bun &> /dev/null; then
    echo ":: Starting frontend..."
    cd frontend && bun run dev &
    FRONTEND_PID=$!
    cd ..
    sleep 3
    echo "   ✓ Frontend running on http://localhost:5173"
else
    echo "   ⚠ Bun not found — frontend skipped. Install: https://bun.sh"
fi
echo ""

# ── 4. Sample prediction ──────────────────────────────────────────────
echo ":: Sample prediction (Chisapani, normal conditions)..."
curl -sf -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"station_id":"chisapani","temperature":22,"rainfall":18,"humidity":72,"river_flow":392}' \
    | python3 -m json.tool
echo ""

echo ":: Sample prediction (Chisapani, flood conditions)..."
curl -sf -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"station_id":"chisapani","temperature":30,"rainfall":55,"humidity":85,"river_flow":5200}' \
    | python3 -m json.tool
echo ""

echo "╔══════════════════════════════════════════════╗"
echo "║   Demo is running.                             ║"
echo "║                                                ║"
echo "║   Frontend  → http://localhost:5173             ║"
echo "║   Backend   → http://localhost:8000             ║"
echo "║   API docs  → http://localhost:8000/docs        ║"
echo "║                                                ║"
echo "║   Press Ctrl+C to stop.                        ║"
echo "╚══════════════════════════════════════════════╝"

wait
