# Scenario 1 — Single failing trace, no diff

## Setup
A coding agent (LangGraph-style ReAct loop) was tasked with "fix the failing `test_parse_csv_with_quotes` test in `utils/csv_parser.py`." The run failed (test still red after the agent gave up at step 18). This is the kind of export a user would paste after exporting from LangGraph callbacks or a Langfuse trace.

## Input trace (paste this to the skill)

```json
{
  "task": "Fix failing test test_parse_csv_with_quotes in utils/csv_parser.py",
  "outcome": "failed",
  "steps": [
    {"i": 1, "actor": "llm", "action": "plan", "summary": "Decide to read the failing test first."},
    {"i": 2, "actor": "tool:read_file", "action": "read", "summary": "Read tests/test_csv_parser.py", "status": "ok"},
    {"i": 3, "actor": "tool:read_file", "action": "read", "summary": "Read utils/csv_parser.py", "status": "ok"},
    {"i": 4, "actor": "tool:run_tests", "action": "test", "summary": "Ran test_parse_csv_with_quotes", "status": "error", "output": "AssertionError: expected 3 fields, got 2"},
    {"i": 5, "actor": "llm", "action": "plan", "summary": "Hypothesis: quote handling in split logic is wrong."},
    {"i": 6, "actor": "tool:search_docs", "action": "search", "summary": "Searched 'python csv quoted field split'", "status": "ok"},
    {"i": 7, "actor": "tool:search_docs", "action": "search", "summary": "Searched 'csv module quotechar escapechar'", "status": "ok"},
    {"i": 8, "actor": "tool:search_docs", "action": "search", "summary": "Searched 'regex split respecting quotes python'", "status": "ok"},
    {"i": 9, "actor": "tool:search_docs", "action": "search", "summary": "Searched 'csv parser quoted comma edge case'", "status": "ok"},
    {"i": 10, "actor": "tool:edit_file", "action": "edit", "summary": "Modified split regex in csv_parser.py", "status": "ok"},
    {"i": 11, "actor": "tool:run_tests", "action": "test", "summary": "Ran test_parse_csv_with_quotes", "status": "error", "output": "AssertionError: expected 3 fields, got 4"},
    {"i": 12, "actor": "tool:edit_file", "action": "edit", "summary": "Tweaked regex again", "status": "ok"},
    {"i": 13, "actor": "tool:run_tests", "action": "test", "summary": "Ran test_parse_csv_with_quotes", "status": "error", "output": "AssertionError: expected 3 fields, got 4"},
    {"i": 14, "actor": "tool:edit_file", "action": "edit", "summary": "Tweaked regex a third time", "status": "ok"},
    {"i": 15, "actor": "tool:run_tests", "action": "test", "summary": "Ran test_parse_csv_with_quotes", "status": "error", "output": "AssertionError: expected 3 fields, got 4"},
    {"i": 16, "actor": "tool:edit_file", "action": "edit", "summary": "Reverted to original regex, tried escaping differently", "status": "ok"},
    {"i": 17, "actor": "tool:run_tests", "action": "test", "summary": "Ran test_parse_csv_with_quotes", "status": "error", "output": "AssertionError: expected 3 fields, got 2"},
    {"i": 18, "actor": "llm", "action": "give_up", "summary": "Agent reports unable to fix the test after repeated attempts.", "status": "error"}
  ]
}
```

## Pass criteria
- [ ] Output includes a trace summary noting ~18 steps and a "failed" outcome.
- [ ] Output segments into roughly three phases: (1) investigation/reading (steps ~1–4), (2) research via search_docs (steps ~5–9), (3) a retry loop of edit→test→edit→test (steps ~10–18).
- [ ] The retry-loop phase (steps 11–17) is flagged as an anomaly — repeated edits with no new information, same assertion error pattern recurring.
- [ ] Every phase label cites specific step indices (not a vague unsupported description).
- [ ] Bottom line correctly identifies the edit/test retry loop (roughly steps 10–18) as where the run got stuck, without inventing a root cause the trace doesn't show (e.g., it should not confidently state the *exact* code-level bug, since the trace doesn't include diffs of what text was actually changed — it can say "the agent kept tweaking the split regex without resolving the field count mismatch" which is grounded, not "it forgot to handle escaped quotes" which the trace doesn't actually prove).
- [ ] No fabricated fields (timestamps, costs) — trace has none, so output should not invent any.

## Fail conditions
- Treats the whole trace as one undifferentiated block.
- Produces phase labels with no cited step ranges.
- Invents a specific code-level root cause not evidenced by the trace content shown.
