.PHONY: run start-backend start-frontend setup clean check install

# =============================================================================
# MAIN COMMANDS
# =============================================================================

# Full setup + run instructions
run:
	@echo "============================================"
	@echo "Term Sheet Generator"
	@echo "============================================"
	@echo ""
	@echo "Run these in two separate terminals:"
	@echo ""
	@echo "  Terminal 1 (backend):  make start-backend"
	@echo "  Terminal 2 (frontend): make start-frontend"
	@echo ""
	@echo "Then open http://localhost:3000"
	@echo "============================================"

# Start the backend API server
start-backend:
	@echo "Starting backend on http://localhost:8000..."
	uv run uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Start the frontend dev server
start-frontend:
	@echo "Starting frontend on http://localhost:3000..."
	cd web && npm run dev

# =============================================================================
# SETUP
# =============================================================================

# Full setup - install all dependencies
setup:
	@echo "Installing Python dependencies..."
	uv sync
	@echo "Installing frontend dependencies..."
	cd web && npm install
	@echo "Creating output directory..."
	mkdir -p out
	@echo ""
	@echo "Setup complete! Run 'make run' for instructions."

# Install Python dependencies only
install:
	uv sync

# =============================================================================
# UTILITIES
# =============================================================================

# Clean all output artifacts
clean:
	rm -rf out/*
	mkdir -p out
	@echo "Output directory cleared"

# Clear session cache only (keeps output files)
clear-cache:
	rm -f out/.session_cache.json
	@echo "Session cache cleared"

# Validate all required outputs exist
check:
	@echo "Checking output artifacts..."
	@test -f out/extracted_data.json || (echo "❌ Missing: extracted_data.json" && exit 1)
	@test -f out/conflicts.json || (echo "❌ Missing: conflicts.json" && exit 1)
	@test -f out/user_decisions.json || (echo "❌ Missing: user_decisions.json" && exit 1)
	@test -f out/term_sheet.md || (echo "❌ Missing: term_sheet.md" && exit 1)
	@test -f out/execution_log.json || (echo "❌ Missing: execution_log.json" && exit 1)
	@echo "✅ All outputs present!"

# =============================================================================
# LEGACY / DEV
# =============================================================================

# Alias for backwards compatibility
run-server: start-backend
dev-frontend: start-frontend
