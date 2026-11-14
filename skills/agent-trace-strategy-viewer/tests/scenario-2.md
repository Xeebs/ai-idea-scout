# Scenario 2 — Two traces, diff mode (failing vs. known-good)

## Setup
A research agent was asked, twice, "find the current CEO of a mid-size company and cite a primary source." Run A failed (gave a stale/wrong answer with no usable citation). Run B, run later with a tweaked prompt, succeeded. The user wants to know exactly where the two runs' strategies diverged, not just that they produced different answers.

## Input trace A — failing run (paste this)

```json
{
  "task": "Find the current CEO of Acme Robotics and cite a primary source.",
  "outcome": "failed",
  "steps": [
    {"i": 1, "actor": "llm", "action": "plan", "summary": "Plan: search for 'Acme Robotics CEO'."},
    {"i": 2, "actor": "tool:web_search", "action": "search", "summary": "Searched 'Acme Robotics CEO'", "status": "ok"},
    {"i": 3, "actor": "tool:web_search", "action": "search", "summary": "Top result is a 2021 news article naming 'Jane Ortiz' as CEO", "status": "ok"},
    {"i": 4, "actor": "llm", "action": "decide", "summary": "Accepts the 2021 article as current answer without checking date relevance."},
    {"i": 5, "actor": "tool:web_search", "action": "search", "summary": "Searched 'Jane Ortiz Acme Robotics' to find a bio page for citation", "status": "ok"},
    {"i": 6, "actor": "tool:web_search", "action": "search", "summary": "Found a 2021 press release mentioning Jane Ortiz", "status": "ok"},
    {"i": 7, "actor": "llm", "action": "answer", "summary": "Answers 'Jane Ortiz' citing the 2021 press release.", "status": "error", "output": "Wrong — company's investor relations page shows a CEO change in 2024."}
  ]
}
```

## Input trace B — successful run (paste this)

```json
{
  "task": "Find the current CEO of Acme Robotics and cite a primary source.",
  "outcome": "passed",
  "steps": [
    {"i": 1, "actor": "llm", "action": "plan", "summary": "Plan: search for 'Acme Robotics CEO'."},
    {"i": 2, "actor": "tool:web_search", "action": "search", "summary": "Searched 'Acme Robotics CEO'", "status": "ok"},
    {"i": 3, "actor": "tool:web_search", "action": "search", "summary": "Top result is a 2021 news article naming 'Jane Ortiz' as CEO", "status": "ok"},
    {"i": 4, "actor": "llm", "action": "decide", "summary": "Flags the article as dated and plans to check the company's own investor relations page for a current, primary source.", "status": "ok"},
    {"i": 5, "actor": "tool:web_search", "action": "search", "summary": "Searched 'Acme Robotics investor relations leadership'", "status": "ok"},
    {"i": 6, "actor": "tool:read_page", "action": "read", "summary": "Opened Acme Robotics' official investor relations 'Leadership' page", "status": "ok"},
    {"i": 7, "actor": "llm", "action": "answer", "summary": "Answers 'Marcus Lin' citing the company's own investor relations page, dated 2024.", "status": "ok"}
  ]
}
```

## Pass criteria
- [ ] Both traces are segmented (likely 2 phases each: initial search, then either "accept stale result" vs. "verify via primary source").
- [ ] Diff mode correctly identifies step 4 in both traces as the divergence point — run A accepted the 2021 article at face value, run B flagged it as dated and sought a primary source instead. The output should name step 4 specifically in both traces, not a later or earlier step.
- [ ] The divergence description states the actual differing action (accepting a dated secondary source vs. deliberately seeking a primary/current source), not a generic "run A failed, run B passed."
- [ ] Bottom line correctly attributes run A's failure to not checking recency/authority of the source, grounded in steps 3–7 of trace A.
- [ ] Output does not claim the trace contains timestamps if none are given — the trace JSON above has no explicit timestamp field, only outcome dates mentioned in text; the skill should not invent a time span section beyond what's stated in the step summaries.

## Fail conditions
- Reports a divergence point that isn't step 4 (e.g., picks the final answer step as the only difference).
- States the two runs diverged without citing specific step indices from both traces.
- Fabricates a "primary source URL" or specific citation text not present in either trace.
