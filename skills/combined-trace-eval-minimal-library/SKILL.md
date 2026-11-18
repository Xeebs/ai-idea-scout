---
name: combined-trace-eval-minimal-library
description: Build-vs-buy-vs-pair decision aid for teams who need both LLM tracing AND pass/fail eval regression checks on one feature. Scores a team's stack, eval needs, and scale into one of four paths — adopt a combined trace+eval library, adopt a tracing-only minimal library, manually pair two separate libraries (tracing + eval), or buy a full vendor platform — and sketches the first eval assertions if the combined-library path fits. Use when a team is choosing LLM observability/eval tooling and hasn't committed engineering time yet.
---

# Combined Trace+Eval Minimal Library — Build-vs-Buy-vs-Pair Decision Aid

## When to use this
A team is adding an LLM-backed feature to an existing product and needs to decide how to get both (a) visibility into prompts/responses/latency/cost and (b) pass/fail regression checks against expected outputs — before any engineering time is committed to a specific tool. Use this at that decision point, not after a tool is half-integrated.

This skill is specifically for teams who need **both halves** (tracing and eval), or are unsure whether they need the eval half yet. If a team has already confirmed they only need tracing with no pass/fail checks, that's a tracing-only decision outside this skill's scope — point them to a tracing-only build-vs-buy aid instead. Do not use this for teams that already have a dedicated eval/ops engineer evaluating enterprise platforms (Arize, Datadog LLM Observability, etc.) — that's a higher-stakes platform bake-off this skill isn't scoped for.

## Inputs
**Data source**: Manual — the user pastes a description of their current LLM stack and language (e.g., "Python, calling OpenAI directly"), whether they need pass/fail eval checks or just tracing (and if unsure, what's driving the question), request volume (requests/day), team size (how many engineers could maintain this tooling, not total headcount), any data-residency/compliance constraint, and whether any tracing or eval library is already partially integrated. This mirrors how the parent idea's underlying library itself connects — in-process SDK wrapping of the team's own LLM calls, a mature and trivial integration point requiring no external platform — but the decision-aid skill itself only ever works from what the user pastes about their stack and needs, never from a live connector.

If any of the six inputs above is missing, ask for it before producing a recommendation — do not guess eval need, volume, or compliance posture.

## Procedure
1. **Collect the six inputs**: stack/language, eval need (yes/no/unsure + driver), request volume/day, engineers available to maintain tooling, data-residency/compliance constraint, and any existing partial tracing/eval integration.
2. **Resolve "unsure" on eval need first**, before branching, using this question: "If a prompt change silently made the feature worse, would you find out from a regression check, or from a user complaint?" If the answer is "user complaint" or unknown, treat eval need as YES — that gap is the exact evidence this idea is built on (teams hand-rolling this after shipping tracing alone).
3. **Branch into one of four paths**, in this order — never skip a check to jump to a later path:
   - **Path A — Tracing only, no eval library needed.** Eval need is genuinely NO (the team has no pass/fail checks today and no plan to add them this quarter) and volume is low enough that provider dashboards or a minimal tracing-only library cover the stated pain point. Recommend a tracing-only minimal self-hosted library (e.g., this repo's own "Lean Log") and stop — do not recommend eval tooling the team hasn't asked for.
   - **Path B — Combined library (this idea's library).** Eval need is YES, the team wants one install instead of wiring two tools together, has no dedicated eval/ops engineer, and either has a data-residency constraint or simply doesn't want prompt/response data leaving their infrastructure. This is the default recommendation for day-one tracing+eval on a single feature with a small team.
   - **Path C — Manually pair two libraries (e.g., OpenLLMetry for tracing + DeepEval for eval).** Eval need is YES and is scoped to this one feature (not a cross-feature/platform need), the team already has one half partially integrated (e.g., OpenLLMetry already wired in) and wants to keep using it, or has engineering capacity to maintain two separate dependencies and specifically wants each half to be independently best-in-class rather than a single combined tool. Name the specific pairing and flag the integration cost (two configs, two local stores unless deliberately pointed at one, two upgrade cadences) as the real tradeoff against Path B.
   - **Path D — Buy a full vendor platform** (Langfuse, LangSmith, Arize, etc.). Team has or is about to hire a dedicated eval/ops role, and either the need spans multiple AI features/teams rather than just this one, or the team needs capabilities neither a minimal library nor a manual pairing will have (dataset-level evals at scale, human annotation queues, A/B testing, SSO/enterprise compliance) — and is willing to accept recurring cost and a third party processing prompt/response data, or already runs the multi-container self-host stack this is scoped for.
   - **Tie-break when both C and D's conditions are technically met** (e.g., a feature already has one half integrated, but the team has also just hired a dedicated eval engineer and named platform-wide needs): prefer Path D whenever the stated need explicitly spans more than this one feature, or explicitly names human annotation queues or A/B testing — those are platform-level capabilities that a single feature's manual pairing doesn't provide, and defaulting to C here would under-serve a need the team has already told you is bigger than one feature.
4. **Write the recommendation**, citing the specific input values that drove the path (e.g., "eval need YES via the regression question, no ops engineer, data-residency constraint → Path B").
5. **Name what's given up** by not choosing each of the other three paths, one line each.
6. **If Path B (combined library) is recommended**, sketch the first one or two assertion checks to wire up: name the specific call to wrap first (the feature's primary user-facing completion call), one deterministic matcher (e.g., exact-match or schema check against a known-good example) and, only if the eval need described in step 1 can't be matcher-checked (open-ended generation, tone, correctness that isn't exact-matchable), one LLM-judge rubric check — state explicitly that the judge check is optional and costs an extra model call per run.
7. **Set a revisit trigger** — a concrete number (request volume, team size, or "when you hire a dedicated eval engineer") at which the recommendation should be re-run.

## Output format
```
## Recommendation: Path <A-D> — <name>

**Why**: <one or two sentences citing the specific input values, including how eval need was resolved>

**What you give up by not choosing the others**:
- Path A (tracing only): <one line>
- Path B (combined library): <one line>
- Path C (manually pair two libraries): <one line>
- Path D (buy a platform): <one line>
(omit the line matching the recommended path itself)

**First assertion checks to wire up** (only if Path B):
- Wrap first: <specific call path>
- Deterministic matcher: <what it checks>
- Judge check (optional): <only if needed, with the extra-cost caveat>

**Revisit this recommendation if**: <concrete trigger>
```

## Guardrails
- Never produce a recommendation without resolving the eval-need question explicitly (step 2) — "unsure" defaulting silently to "no eval" is exactly the trap this skill exists to catch; always show the regression question and its answer in the output.
- Never recommend Path D (buy) as a first answer for a single feature on a small team without a dedicated ops role — it is only reachable after confirming the team's stated needs genuinely exceed Paths B and C.
- Never recommend Path D when the user has stated a hard data-residency/compliance constraint the named vendor doesn't satisfy — flag the conflict instead of papering over it.
- Never recommend Path B (combined library) and then sketch more than one optional judge-based check — "minimal" is the entire premise of this library; piling on judge checks in the first pass defeats the point and should be flagged as scope creep.
- Never skip the "revisit trigger" line.
- Never claim this skill connects to a live tracing/eval backend — it only works from what the user pastes about their stack; if the user wants a specific failing trace turned into an eval case (not a tooling decision), say this is a different task and point them to a trace-to-eval drafting skill instead.
