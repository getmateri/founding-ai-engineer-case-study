# Architecture

## Problem Decomposition

The core problem: generate structured documents from multiple source files with human oversight.

**Key subproblems:**

1. **Document Schema Definition** - How to structure any document as extractable fields
   - Solution: Three-layer architecture (see [SCHEMA.md](./SCHEMA.md))
   - Layer 1: Template schema (what fields exist)
   - Layer 2: Extracted fields (values with metadata)
   - Layer 3: Rendered document (final prose output)

2. **Source Ingestion** - How to get documents into LLM-readable format
   - Excel → parsed to text with cell references preserved
   - PDF/DOCX/DOC → extracted text content
   - ZIP → auto-extracted and contents parsed
   - Markdown → passed through directly
   - Extensible: add parsers for new formats as needed

3. **Human-in-the-Loop Timing** - When does the human intervene?
   - After extraction, before finalization
   - User reviews all low-confidence fields (confidence < 1.0)
   - User can edit any field at any time
   - Finalization blocked until all fields confirmed

4. **Source Traceability** - How to link back to original data
   - Every extracted value includes source file and location
   - Conflicts show which sources disagree and what values they have
   - User decisions logged with timestamps and reasoning

---

## System Design

This is an **agentic workflow**, not a pure agent. Intentionally constrained for reliability. See [PROMPTS.md](./PROMPTS.md) for more detail on this.

### Capabilities

The system can:
- Parse multiple document formats (Excel, PDF, DOCX, DOC, Markdown, ZIP)
- Extract structured data using LLM with source citations
- Detect conflicts between sources
- Render extracted data into a formatted document
- Track user decisions and modifications

### Control Flow

1. **Start**: User selects document type and clicks "Generate"
2. **Load Sources**: System reads all files from source directory, parses into text
3. **Extract Sections**: For each section in the schema, make an LLM call to extract fields. Each call includes full source context but only asks for that section's fields.
4. **Review**: User sees all extracted fields with metadata (source, confidence, conflicts). Fields with confidence < 1.0 are highlighted for review. User can click any field to edit.
5. **Edit Loop**: User edits fields until satisfied. Each edit sets confidence to 1.0 and logs the decision.
6. **Finalize**: Only available when all fields have confidence = 1.0. Generates final outputs.

**States:**
- `INIT` - Session created, ready to start
- `EXTRACTING` - LLM calls in progress
- `REVIEWING` - User reviewing and editing fields
- `COMPLETE` - Outputs generated

### Context Management

- **Per-section extraction**: Each LLM call gets full source context but only extracts fields for one section. Prevents context overflow and improves accuracy.
- **In-memory session state**: Document data, user decisions, and LLM call metrics stored per session.
- **File outputs**: Extracted data, conflicts, decisions, and final document saved to output directory.

---

## Automation Framework

### What to Automate vs. Ask User

**Automate:**
- Document parsing and format conversion
- Initial field extraction with best-guess values
- Conflict detection between sources
- Document rendering from confirmed fields

**Don't automate (require user):**
- Final value confirmation for low-confidence fields
- Conflict resolution when sources disagree
- Any field where AI confidence < 1.0

**Philosophy:** Don't ask the user questions mid-flow. Extract everything, show all the data with metadata, let them review and edit):
 - The AI does the tedious work (reading documents, finding values)
- The human makes the judgment calls (resolving conflicts, confirming accuracy)

### Confidence Thresholds

**Binary only: 0.0 or 1.0**

- `1.0` = Value explicitly stated in source, no ambiguity, exact match
- `0.0` = Anything else (inferred, calculated, assumed, uncertain)

Why not gradients? What's the difference between 0.7 and 0.8 confidence? Nothing actionable. Binary forces the AI to be conservative and makes the review UX clear: confirmed or needs review.

### Speed vs. Accuracy Trade-off

Chose accuracy:
- Delays between extraction calls (rate limiting)
- Separate LLM call per section (better focus)
- Full source context in each call (no chunking/retrieval)

For legal/financial documents, users will wait for accuracy. This isn't a chatbot.

---

## Conflict Resolution

### Detection

During extraction, LLM identifies when multiple sources provide different values for the same field:

```json
{
  "value": "extracted_value",
  "conflicts": [
    {"source": "policy.md", "value": "15%"},
    {"source": "deal_model.xlsx", "value": "20%"}
  ]
}
```

### User Surfacing

- Conflicting fields highlighted in UI
- All conflicting values shown with their sources
- User clicks to edit and picks the correct value (or enters a new one)

### Source Hierarchy

Currently hardcoded per document type. For example, term sheets use: **Deal Model > Firm Policy > Defaults**

Future work: let users specify priority, or use AI to infer document relationships.

---

## Error Recovery

### User Corrections

When user edits a field:
1. New value saved
2. Confidence set to 1.0 (user-confirmed)
3. Source updated to "user_input / manual edit"
4. Conflicts cleared (user made the decision)
5. Decision logged with timestamp, old value, new value, optional reason

### State Preservation

- **Preserved**: All extracted data, user edits, decision history
- **Recomputed**: Document preview (re-rendered after each edit)
- **Not preserved across server restart**: Session state (in-memory only for MVP)

---

## Limitations & Future Work

### Cut for Time

- **No persistent sessions** - state lost on server restart
- **No streaming** - extraction is blocking, no progress updates per-field
- **Hardcoded source hierarchy** - can't configure which files take precedence
- **Single document type** - architecture supports multiple, but only one implemented
- **No evals** - prompt changes are "vibe-checked", not measured

### With More Time

- **Persist sessions** to database, resume interrupted extractions
- **Streaming extraction** with real-time field updates in UI
- **User-configurable source priority** with drag-and-drop ranking
- **Evaluation suite** for extraction accuracy on test documents
- **Template builder** - UI for creating new document types
- **Audit log** for compliance (who changed what, when, why)

### Supporting Other Document Types

See [SCHEMA.md](./SCHEMA.md) for detailed steps. Summary:

1. Define Pydantic schema with sections and fields
2. Write extraction prompts for each section
3. Create render template
4. Register document type

The extraction → review → finalize flow stays the same. That's the point of the architecture.
