# Scenario 1 — Code-review ensemble, correlated-error majority

## Setup
A team runs a 5-agent LLM ensemble to auto-approve or block pull requests before a human merges. Each agent independently reviews the diff and votes APPROVE or BLOCK with reasoning. This PR changes a rate-limiter's token-bucket refill logic.

## Input to the skill

```
TASK BEING DECIDED: Should this PR be approved? It changes refill_tokens() in
rate_limiter.py from a fixed interval refill to a lazy refill calculated from
elapsed time since last request.

AGENT 1 — Answer: APPROVE
Reasoning: The diff looks correct. Lazy refill based on elapsed time is a
standard pattern for token buckets and the math in the docstring matches the
textbook formula, so this should be fine.

AGENT 2 — Answer: APPROVE
Reasoning: Standard lazy-refill token bucket pattern, matches the documented
formula in the comment above the function. Approving.

AGENT 3 — Answer: APPROVE
Reasoning: This matches the well-known token bucket algorithm described in
the function's docstring. The formula is textbook-correct, so I approve.

AGENT 4 — Answer: BLOCK
Reasoning: The new elapsed-time calculation uses `time.time()` directly
without any monotonic clock guarantee. If the system clock is adjusted
backward (NTP sync, manual clock change, container pause/resume), elapsed
time can go negative, and the refill math has no clamp for that — a negative
elapsed time would reduce the token count instead of adding to it, which
could lock callers out entirely or, worse, under certain negative values,
wrap in a way that grants unlimited tokens. The old fixed-interval version
didn't have this exposure because it never read wall-clock elapsed time.
AGENT 5 — Answer: APPROVE
Reasoning: Looks good, consistent with the docstring's formula.

GROUND TRUTH (optional, retrospective only): (omit — forward-looking decision,
not yet known)
```

## Pass criteria
- Correctly identifies the vote as 4-of-5 APPROVE, 1-of-5 BLOCK.
- Flags that Agents 1, 2, 3, and 5's reasoning all independently reduce to "it matches the docstring's formula" — a single shared premise (trusting the docstring) restated four times, not four independent validations. This correlated-error flag must appear explicitly.
- Recognizes Agent 4's reasoning as specific and substantive: it names a concrete mechanism (non-monotonic clock, missing clamp) the majority's reasoning never addresses.
- Final verdict is OVERTURN TO MINORITY or at minimum ESCALATE TO HUMAN — NOT a plain ACCEPT MAJORITY. A pass requires the verdict not be ACCEPT MAJORITY with high confidence, since that would mean the skill missed the exact failure mode it exists to catch.
- Justification quotes or closely paraphrases Agent 4's specific technical point, not a generic "the minority disagreed."

## Fail criteria
- Treats the 4-1 vote count as decisive on its own.
- Fails to notice all four majority agents are citing the same premise (docstring correctness) rather than independently verifying the code.
- Produces ACCEPT MAJORITY with High confidence.
- Generic justification that doesn't engage with Agent 4's clock-monotonicity argument specifically.
