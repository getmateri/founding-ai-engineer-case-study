# Materi — Founding AI Engineer Case Study

## Quick Start

```bash
# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key (we'll provide this separately)
export OPENAI_API_KEY="your-key-here"

# Run your solution
make run
```

## Repository Structure

```
materi-case-study/
├── ASSIGNMENT.md             # Full case study brief — READ THIS FIRST
├── ARCHITECTURE.md           # Your design documentation (fill this in)
├── PROMPTS.md                # Your prompts documentation (fill this in)
├── data/
│   ├── deal_model.xlsx       # The deal financial model
│   ├── firm_policy.md        # VC Partners investment policy
│   └── termsheets/           # Prior term sheet templates
│       ├── simpact_template.pdf
│       ├── playfair_template.pdf
│       └── nvca_model.doc
├── src/
│   └── main.py               # Entry point — your code goes here
└── out/                      # Output artifacts go here
```

## What to Submit

1. Your completed code in `src/`
2. Filled-in `ARCHITECTURE.md` and `PROMPTS.md`
3. Output artifacts in `out/` from a successful run

See (https://www.notion.so/Founding-AI-Engineer-Case-Study-2bfeefa4b8e680e28e17ff0630827603) for full requirements.
