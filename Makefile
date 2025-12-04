.PHONY: run setup clean test

# Default target
run:
	python src/main.py

# Set up the environment
setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

# Clean output artifacts
clean:
	rm -rf out/*
	mkdir -p out

# Run with verbose logging
debug:
	DEBUG=1 python src/main.py

# Validate outputs exist
check:
	@echo "Checking output artifacts..."
	@test -f out/extracted_data.json || (echo "Missing: extracted_data.json" && exit 1)
	@test -f out/conflicts.json || (echo "Missing: conflicts.json" && exit 1)
	@test -f out/user_decisions.json || (echo "Missing: user_decisions.json" && exit 1)
	@test -f out/term_sheet.md || (echo "Missing: term_sheet.md" && exit 1)
	@test -f out/execution_log.json || (echo "Missing: execution_log.json" && exit 1)
	@echo "All outputs present!"
