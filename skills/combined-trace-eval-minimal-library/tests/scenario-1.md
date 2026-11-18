# Scenario 1 — Small SaaS team adding an AI summarization feature

## Input (what the user pastes)

> We're a 6-person engineering team at a project-management SaaS. We're adding an AI feature that summarizes a customer's weekly activity into a short digest email, calling the Anthropic API directly from our Python backend. Right now we have zero visibility into it — no logging beyond a generic try/except.
>
> We don't currently have anything like eval tests for it. Someone asked in standup "how do we know this doesn't get worse if we tweak the prompt" and nobody had a good answer — we'd probably only find out from a customer complaint or a support ticket.
>
> Volume: roughly 3,000 digests/day. No one on the team is a dedicated ops or eval person — we're all full-stack generalists. We do have a contractual data-residency requirement with a few enterprise customers that prompt/response content can't leave our own infrastructure. Nothing is integrated yet — no OpenLLMetry, no DeepEval, nothing.

## Expected behavior

1. The skill collects/confirms all six inputs: stack (Python/Anthropic SDK), eval need, volume (3,000/day), team size (6, no dedicated ops/eval role), data-residency constraint (yes), existing integration (none).
2. Eval need is stated as "unsure" in effect (the standup anecdote) — the skill must apply the regression question. The standup anecdote ("we'd find out from a customer complaint") is itself the answer to that exact question, so eval need resolves to YES. The output must show this resolution explicitly, not silently assume "no eval."
3. Branches to **Path B — combined library**: eval need YES, no dedicated ops/eval engineer, data-residency constraint present, nothing currently integrated, single feature on a small team. The output must name these specific values as the reasons, not a generic justification.
4. Produces the three give-up lines for Paths A, C, and D.
5. Produces a "first assertion checks" section: wrap first = the summarization call; a deterministic matcher suggestion (e.g., check digest references only data from that customer's week, length/schema bounds); and — because "did the summary get worse" is not exact-matchable — one optional LLM-judge rubric check, clearly marked optional with the extra-cost note.
6. Sets a revisit trigger (e.g., "revisit if volume crosses some threshold or you hire a dedicated eval/ops engineer").

## Pass/fail criteria

- PASS requires: all six inputs addressed; the regression question and its resolution are shown explicitly; Path B is recommended with the specific driving values named; exactly one optional judge check is suggested (not more); a revisit trigger is stated; the data-residency constraint is referenced in the reasoning.
- FAIL if: the skill silently treats "unsure" eval need as "no eval" without applying the regression question; recommends Path D (buy) first; omits the revisit trigger; suggests more than one judge-based check; or fabricates a connector/integration that wasn't mentioned.
