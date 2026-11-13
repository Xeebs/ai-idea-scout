# Scenario 1 — CI PR-review bot, identical-argument + repeated-error-code loop

## Setup
A team runs a GitHub Actions coding-agent bot that refreshes PR context before commenting. Auth token refresh is broken for one PR, and the agent keeps retrying the exact same call. This mirrors the idea's own cited evidence (`gh-aw-firewall` PR #11280: "29 of 35 inspected agent runs failed repeatedly ... spending ~10 AIC per run without producing value").

## Input (pasted by the user)

```
Run: run-4471
1. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
2. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
3. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
4. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
5. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
6. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
7. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
8. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
9. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
10. refresh_pr_context(pr_number=8832, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
(run timed out after 10 calls, total cost 0.10 AIC, no comment posted)

Run: run-4472
1. refresh_pr_context(pr_number=9010, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
2. refresh_pr_context(pr_number=9010, branch="feature/9010-fix") -> SUCCESS cost=0.01 AIC
3. post_comment(pr_number=9010, body="Reviewed.") -> SUCCESS cost=0.02 AIC
(run completed normally, total cost 0.04 AIC)

Run: run-4473
1. refresh_pr_context(pr_number=7765, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
2. refresh_pr_context(pr_number=7765, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
3. refresh_pr_context(pr_number=7765, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
4. refresh_pr_context(pr_number=7765, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
5. refresh_pr_context(pr_number=7765, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
6. refresh_pr_context(pr_number=7765, branch="main") -> FAIL error=AUTH_401 cost=0.01 AIC
(run timed out after 6 calls, total cost 0.06 AIC, no comment posted)
```

## Expected output (pass/fail criteria)

A response PASSES if it:
1. Identifies run-4471 and run-4473 as waste runs (Strategy A — identical args — and Strategy B — repeated AUTH_401 — both fire on calls 1-2), with run-4472 correctly identified as clean (a 2nd attempt with *different* arguments succeeded — this must NOT be flagged as a waste loop).
2. States the trip point at call #2 for both waste runs (2 identical repeats = threshold reached), marking calls 3 onward in each as wasted: 8 wasted calls in run-4471, 4 wasted calls in run-4473.
3. Computes wasted cost correctly from the given cost field: run-4471 = 0.08 AIC wasted (calls 3-10), run-4473 = 0.04 AIC wasted (calls 3-6), total = 0.12 AIC across the batch — does not invent a different figure and does not report "cost data not provided" (cost was given).
4. Explicitly cites run-4472's successful 2nd attempt (different branch argument) as the reason not to recommend a threshold below 2, per the guardrail.
5. Recommends Strategy A/B threshold=2 with a clear rationale, and does not recommend threshold=1.
6. Does not report any Strategy C match (no reworded/semantically-similar arguments appear in this batch — a response that fabricates one FAILS).
7. Includes the required caveats line stating this is retrospective, not a live monitor.

FAILS if it treats run-4472 as a waste run, miscounts wasted calls/cost, invents a Strategy C match, or recommends threshold=1.
