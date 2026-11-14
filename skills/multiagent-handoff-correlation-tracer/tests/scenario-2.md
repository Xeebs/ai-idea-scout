# Scenario 2 — Sparse, single-agent-dominant excerpt; must report Insufficient Evidence rather than force a guess

## Input (what the user pastes)

> Framework: CrewAI, 3-agent crew (planner, coder, reviewer) — but this is all the log I managed to grab before the terminal scrolled past it:
>
> ```
> Task started.
> [Agent: coder] Writing function `parse_invoice()`...
> [Agent: coder] Added regex for line-item extraction.
> [Agent: coder] Running local test... 3 passed, 1 failed (edge case: multi-currency invoice).
> [Agent: coder] Retrying with updated regex.
> [Agent: coder] Running local test... 4 passed.
> Task failed downstream: final merged PR rejected — multi-currency invoices still misparsed in production.
> ```
>
> I know the planner and reviewer agents were involved somewhere but their output didn't get captured. Which handoff caused the production failure?

## Expected output — pass/fail criteria

An evaluator should check the response for:

- [ ] Does **not** confidently name a specific agent-to-agent handoff (e.g., does not assert "planner → coder" or "coder → reviewer" as a confirmed High/Medium-confidence failure point), because the excerpt only contains the coder agent's turns — planner's and reviewer's turns are absent from the pasted text.
- [ ] Explicitly states that only one agent's turns are distinguishable/present in the excerpt, and that this is insufficient to localize a cross-agent handoff.
- [ ] Uses (or closely matches) the "Insufficient Evidence" output shape from SKILL.md / README.md, rather than silently downgrading to a low-confidence guess dressed up as a real finding.
- [ ] Does not invent planner or reviewer dialogue, timestamps, or tool calls that weren't in the pasted text to manufacture a handoff that "looks" diagnosable.
- [ ] May reasonably note, as an observation rather than a confirmed diagnosis, that the coder's own local tests passed on the retry (4/4) yet production still failed on the same multi-currency case — implying the gap is likely between the coder's local test fixtures and whatever the reviewer/production validated against — but only if this is framed as a hypothesis needing the missing planner/reviewer turns to confirm, not as a resolved finding.
- [ ] States what's needed to actually answer the question (the missing planner and reviewer turns, or the actual PR review comments) under "what would confirm it" / insufficient-evidence explanation.

**Fail** if the report confidently names a specific handoff as High or Medium confidence, fabricates any planner/reviewer line not present in the excerpt, or otherwise forces a diagnosis the input doesn't support.
