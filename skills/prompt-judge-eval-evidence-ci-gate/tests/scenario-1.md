# Scenario 1 — Judge prompt change with one real regression

## Setup
A developer rewrote the system prompt for an LLM-as-judge that scores customer-support ticket triage classifications, to reduce false "urgent" labels. They ran their team's existing eval harness against both `main` and their branch and are about to open a PR. They paste this into the skill:

**Raw eval output (pasted as-is from the team's internal eval runner):**
```
{
  "suite": "triage-judge-v3",
  "results": {
    "main":   {"accuracy": 0.942, "F1": 0.430, "hallucination_rate": 0.031},
    "branch": {"accuracy": 0.938, "F1": 0.453, "hallucination_rate": 0.024}
  }
}
```

**CI run link:** `https://github.com/acmeco/support-agent/actions/runs/9931204477`

**Metrics that matter for this PR:** left blank (all of them).

## Expected output

A Markdown "Eval Evidence" block that:
- Links the CI run exactly as given, with no invented text appended.
- Lists all three metrics as before→after pairs: `accuracy: main 94.2% → branch 93.8%`, `F1: main 43.0 → branch 45.3`, `hallucination_rate: main 3.1% → branch 2.4%` (or equivalent decimal/percent formatting, as long as values are not rounded away).
- Correctly classifies `accuracy` as REGRESSED (0.942 → 0.938, higher-is-better metric got worse), `F1` as IMPROVED, `hallucination_rate` as IMPROVED (lower-is-better metric got better).
- States an overall verdict of `REGRESSED (1 metric: accuracy)` — not IMPROVED, not NEUTRAL, and does not bury or omit the accuracy drop because two other metrics improved.
- Does not editorialize ("this regression is minor and acceptable") — just reports it.

## Pass/fail criteria
- **PASS** if the output block includes all three metrics with correct direction classification, states the CI link verbatim, and the verdict line explicitly says REGRESSED and names `accuracy`.
- **FAIL** if the verdict says IMPROVED or NEUTRAL, if the accuracy regression is dropped or described only as a side note without affecting the verdict, if any metric value is rounded in a way that hides the regression (e.g. displaying both as "94%"), or if the model fabricates additional metrics not present in the input.
