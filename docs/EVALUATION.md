- Implement LLM observability with a platform like braintrust (I've used them extensively before)

Error Analysis is where I would start:
- Look at traces where AI isn't performing well or failed. This could be due to user feedback or some threshold/measure that we set.
- Look for common error patterns and failure modes.
- Plan to implement fixes.
- Continuously: Take random sample of traces, use human review by expert to identify failure modes, error patterns, improvement areas.

Prompt Evals can be done when we move away from vibe-checks:
- Measure prompt performance against a known dataset (could be real traces) with assertions.
