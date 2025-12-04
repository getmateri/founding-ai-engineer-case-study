# Prompts & Design Rationale

## Design Philosophy

This system is intentionally **not a pure agent** - it's an agentic workflow. This is by design.

### Why an Agentic Workflow, Not a Full Agent?

**The primary goal is trust.** Users need to trust the output. That requires giving them control and predictability.

A pure agentic system would be:
- Harder to test
- Harder to debug  
- Less deterministic
- More surface area for unwanted AI behavior

By constraining the AI to a structured workflow, we get:
- Predictable execution (same inputs → same flow)
- Clear points for human intervention
- Easier monitoring and debugging
- A working e2e solution vs. a theoretical agentic one (for the purposes of this case study)

This doesn't mean agents are wrong - they're likely the end goal. But for now I would start with a structured workflow to build a real, reliable product that users can use and provide feedback. Maybe an agent is the answer to this feedback...

### Why No Chat?

Chat creates ambiguity. The user has to describe what they want, and the AI has to interpret it. That's two potential failure points.

With direct field editing:
- User sees exactly what data exists
- User clicks to edit, types new value, done
- No prompt engineering for edit detection
- No "why did the AI not understand me?"

We have the document schema. We have the context. Generate the best guess, let the human confirm and adjust. Simpler for everyone.

### Extensibility

This workflow pattern can support multiple document types. Add a new schema, add section prompts, use the same extraction → review → finalize flow. The term sheet is just the first implementation and it can be scaled (with some tweaks) to many document types. User facing of this could be templates (public or private) for common document types.

---

## System Prompt

Sent with every extraction LLM call:

```
You are an expert at extracting structured data from financial documents for venture capital term sheets.

Your job is to extract specific fields from the provided source documents. For each field:
1. Find the value in the documents (deal model takes precedence for deal-specific terms, firm policy for standard terms)
2. Note exactly where you found it (file + cell reference or section)
3. Rate your confidence using BINARY scoring:
   - 1.0 = You are 100% certain (value explicitly stated, exact match, no ambiguity)
   - 0.0 = Anything less than 100% certain (inferred, assumed, derived, or any doubt)
4. If multiple sources conflict, note all values

IMPORTANT: Only use confidence 1.0 when the value is EXPLICITLY and UNAMBIGUOUSLY stated. If you had to infer, calculate, or make any assumption, use 0.0 so a human can review.

Be precise with numbers and percentages. Use the exact format requested.
```

This is simple and where I would start, once the system is live and we can no longer function off "vibe-checks" with prompt changes, we would have to implement evals to measure improvements.

### Why Binary Confidence?

Gradient confidence (0.7, 0.85, etc.) creates ambiguity. What's the threshold for review? 0.8? 0.9? Why lol? (Same reason I always get LLM as a judge to do pass or fail and not score out of 5)

Binary scoring is unambiguous:
- **1.0** = AI is certain, auto-approve (unless high-stakes field)
- **0.0** = Human must verify

This forces the AI to be conservative. When in doubt, flag for review. That's exactly what we want to build trust in the system.

---

## Section Extraction

Documents are composed of **sections**, and sections contain **fields**.

Each document type defines its sections and the fields within them. The extraction process calls the LLM once per section with a prompt specifying which fields to extract.

### Output Schema

Every extracted field follows this structure:

```json
{
  "field_name": {
    "value": "extracted value or null",
    "source": {"file": "filename", "location": "cell or section reference"},
    "confidence": 0.0 or 1.0,
    "conflicts": [{"source": "other file", "value": "conflicting value"}],
    "reasoning": "why this value was chosen"
  }
}
```

### Why Separate Section Calls?

One call for all fields would:
- Exceed context limits with large source documents
- Reduce extraction accuracy
- Make debugging harder (which section failed?)

Separate calls allow focused extraction with full source context per section.

---

## Source Context Structure

Each extraction call includes source documents in this format:

```
=== DEAL MODEL (Model.xlsx) ===
[parsed Excel content as text]

=== FIRM POLICY (firm_policy.md) ===
[markdown content]

=== REFERENCE TERM SHEETS (format examples) ===
[up to 3 reference term sheets, truncated to 5000 chars each]

IMPORTANT:
- Extract values from the DEAL MODEL for deal-specific terms
- Use FIRM POLICY for standard terms and defaults  
- The reference term sheets are for FORMAT guidance only - do NOT extract values from them
- If a value is not found, set value to null and confidence to 0
```

Source Hierarchy is currently hardcoded: **deal model > firm policy > defaults**

This is a simplification and future work could:
- Let users specify file priority
- Use AI to analyze relationships between documents
- Build a knowledge management layer for source understanding

---

## Summary

This is a **controlled AI workflow** designed for:
- **Trust** - users see and control everything
- **Predictability** - deterministic flow, clear intervention points
- **Simplicity** - no chat ambiguity, direct editing
- **Reliability** - easier to test, debug, and monitor
