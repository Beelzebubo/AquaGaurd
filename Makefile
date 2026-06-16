.PHONY: setup run-backend run-frontend run-demo eval clean lint

# ── Setup ──────────────────────────────────────────────────────────────
setup: setup-venv setup-frontend

setup-venv:                     ## Create venv & install Python deps
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

setup-frontend:                 ## Install frontend deps (requires Bun)
	cd frontend && bun install

# ── Run ────────────────────────────────────────────────────────────────
run-backend:                    ## Start FastAPI backend on :8000
	. venv/bin/activate && python run.py

run-frontend:                   ## Start React frontend dev server on :5173
	cd frontend && bun run dev

run-demo:                       ## Start both in background + print URLs
	@echo "Starting backend..."
	. venv/bin/activate && nohup python run.py > /tmp/aquaguard-backend.log 2>&1 &
	@sleep 3
	@echo "Starting frontend..."
	cd frontend && nohup bun run dev > /tmp/aquaguard-frontend.log 2>&1 &
	@sleep 3
	@echo ""
	@echo "╔══════════════════════════════════════════╗"
	@echo "║   AquaGuard                                ║"
	@echo "║   Backend  → http://localhost:8000         ║"
	@echo "║   Frontend → http://localhost:5173         ║"
	@echo "║   API docs → http://localhost:8000/docs    ║"
	@echo "╚══════════════════════════════════════════╝"
	@echo ""
	@echo "Test a prediction:"
	@echo '  curl -X POST http://localhost:8000/predict \'
	@echo '    -H "Content-Type: application/json" \'
	@echo '    -d "{\"station_id\":\"chisapani\",\"temperature\":22,\"rainfall\":18,\"humidity\":72,\"river_flow\":392}"'

# ── Evaluation ─────────────────────────────────────────────────────────
eval:                           ## Run cross-station evaluation
	. venv/bin/activate && python scripts/evaluate.py

retrain:                        ## Retrain the cross-station model from scratch
	. venv/bin/activate && python scripts/retrain_cross_station.py

# ── Utility ────────────────────────────────────────────────────────────
clean:                          ## Remove generated / cache files
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf audio/
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete
	rm -rf frontend/dist

format:                         ## Auto-format Python + frontend
	. venv/bin/activate && black scripts/*.py app/ 2>/dev/null || true
	cd frontend && bun run format 2>/dev/null || true

lint:                           ## Check frontend lint
	cd frontend && bun run lint
