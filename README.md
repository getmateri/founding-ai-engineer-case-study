# Materi — Document Generator

AI-powered document generation with human-in-the-loop review.

## Quick Start

```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# 2. Install dependencies
make setup

# 3. Start the servers (run in two terminals)
make start-backend   # Terminal 1: starts API on localhost:8000
make start-frontend  # Terminal 2: starts UI on localhost:3000

# 4. Open http://localhost:3000
```

## Full Walkthrough

1. **Open the app** at http://localhost:3000
2. **Review data sources** - you'll see the files in `/data/` (deal model, firm policy, term sheet references)
3. **Click "Generate Term Sheet"** - extraction takes ~60 seconds
4. **Review extracted fields** - left panel shows all fields with confidence and sources
5. **Edit low-confidence fields** - click any field to edit, this sets confidence to 100%
6. **Finalize** - only available when all fields are confirmed

## Output Files

After finalization, check the `out/` directory:

- `term_sheet.md` - the final document
- `extracted_data.json` - all fields with sources and confidence
- `conflicts.json` - any conflicts between sources
- `user_decisions.json` - log of your edits
- `execution_log.json` - LLM call metrics

Run `make check` to verify all outputs exist.

## Commands

```bash
make setup          # Install all dependencies (Python + Node)
make start-backend  # Start API server (localhost:8000)
make start-frontend # Start web UI (localhost:3000)
make clean          # Clear output directory
make check          # Verify output files exist
```

## Project Structure

```
├── docs/
│   ├── ARCHITECTURE.md   # System design
│   ├── SCHEMA.md         # Document schema design
│   └── PROMPTS.md        # Prompts and rationale
├── data/
│   ├── Model.xlsx        # Deal financial model
│   ├── firm_policy.md    # Investment policy
│   └── Termsheets.zip    # Reference term sheets
├── src/
│   ├── api.py            # FastAPI server
│   ├── agent.py          # Extraction orchestration
│   ├── schema.py         # Pydantic models
│   ├── extraction.py     # LLM extraction logic
│   ├── rendering.py      # Markdown generation
│   └── outputs.py        # Output file generation
├── web/                  # Next.js frontend
└── out/                  # Generated outputs
```

## Tech Stack

- **Backend**: Python, FastAPI,
- **Frontend**: Next.js, React, Tailwind CSS

