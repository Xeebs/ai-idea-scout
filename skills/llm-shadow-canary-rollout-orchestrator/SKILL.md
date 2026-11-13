---
name: llm-shadow-canary-rollout-orchestrator
description: Drafts a shadow-test-then-canary rollout plan (sample rate, duration, judge-comparison gate, canary ramp, rollback triggers) for a specific prompt or model version change before it ships to production. Use when a team is about to change a live LLM feature's prompt or model and wants a concrete, numbered plan instead of shipping blind or hand-wiring the playbook from scratch each time.
---

# Promote Gate: Shadow-to-Canary Rollout Plan Advisor

## When to use this
Someone is about to ship a change to a prompt or model version behind a production LLM feature (a new system prompt, a model swap, a few-shot example change, a temperature/parameter tweak) and wants a concrete rollout plan — not generic advice, a plan with actual numbers for their actual traffic and change — before it touches real users. This is the one-time planning pass; it does not run anything. (A running version of this that actually duplicates traffic and enforces the gate automatically is a separate, heavier piece of infrastructure — out of scope for this skill.)

Do not use this for infrastructure/config changes unrelated to prompt or model content (e.g., a pure latency/caching change with no output-affecting change) — there is nothing for a judge to compare in shadow mode, so the core mechanism this skill designs doesn't apply.

## Inputs

**Data source**: Manual — the user describes the change and types or pastes the numbers below; this skill does not connect to any gateway, proxy, or eval backend. (The idea this skill comes from also describes a *Connected* runtime orchestrator that plugs into an LLM gateway like LiteLLM and an eval backend like Langfuse to execute a plan automatically — that is the separate, heavier "project" half. This skill is the planning pass that produces the plan a human or that orchestrator would then execute; it works from what the user tells it, nothing more.)

Required:
1. **The change** — old version vs. new version, concretely: full prompt text (or a diff) if it's a prompt change, or the old and new model names if it's a model swap. "We tweaked the prompt" is not enough — paste the actual text.
2. **Current traffic volume** for the feature being changed — requests per day (or per hour), even if approximate.
3. **What the feature does and who it's for** — e.g. "customer-facing billing chatbot," "internal code-review summarizer," "content moderation classifier." This drives risk tier.

Strongly recommended (ask for these if missing rather than silently assuming):
4. **Existing offline eval results**, if any — a pass rate, score, or "we haven't run one."
5. **Cost per request** (even rough) — needed to size the shadow-mode cost impact honestly.
6. **Risk tolerance / blast radius notes** — is this change behind a kill switch already? Does it touch money, safety, or legal exposure? Is there human review downstream?

If 1–3 are missing, ask for them before drafting anything — a plan built on a guessed traffic number or a vague change description is worse than no plan, because it looks authoritative while being made up.

## Procedure

1. **Classify risk tier** from the change + feature description, using this table (pick the highest-matching tier):
   - **TIER 3 (high)**: change touches money, safety, legal/compliance output, or is a full model swap on a customer-facing path.
   - **TIER 2 (medium)**: prompt rewrite (not just wording tweak) on a customer-facing feature, or any change on an internal feature with downstream business impact (reports, decisions made from the output).
   - **TIER 1 (low)**: minor prompt wording tweak, few-shot example change, or parameter tweak on an internal/low-stakes feature.
   State which tier and why in one sentence, citing the specific input that drove it.

2. **Check the offline-eval prerequisite.** If the user reported no offline eval, or a weak one (small held-out set, no explicit pass/fail bar), say so explicitly and recommend the minimum bar before shadow testing starts: a held-out set of at least 20-30 representative inputs, scored against the *current live* version's output on the same inputs, with an explicit pass threshold. Do not draft a shadow stage that assumes offline eval passed if the user hasn't actually run one — flag it as a blocking prerequisite, not a nice-to-have, for Tier 2/3.

3. **Size the shadow stage.** Shadow mode generates the candidate's output on real traffic without serving it, so sample size is bounded by wanting enough comparisons to trust the judge's verdict, not by anything user-facing.
   - Target a minimum of 200 shadow comparisons for Tier 1, 400 for Tier 2, 800 for Tier 3 (more comparisons needed where a missed regression costs more).
   - Compute the sample rate from traffic volume: `sample_rate = target_comparisons / (daily_volume * target_duration_days)`, solving for a duration between 1 and 7 days (prefer shorter at low traffic ceilings — cap sample rate at 100% and lengthen duration instead of exceeding it).
   - Show the arithmetic, not just the answer, so the user can sanity-check it against their own cost tolerance.
   - Flag the cost impact in plain terms: shadow mode roughly doubles inference spend on the sampled slice for the shadow window — state the rough extra dollar cost if a cost-per-request was given, or say "ask for cost-per-request to quantify this" if it wasn't.

4. **Define the judge-comparison gate.** Specific to the feature, not generic:
   - Name 2-4 comparison axes relevant to this feature (e.g. for a support chatbot: correctness, tone/policy adherence, resolution rate; for a summarizer: factual coverage, length adherence, omission of key points).
   - State the promotion threshold concretely (e.g. "candidate must win or tie on correctness in ≥90% of comparisons, and must not regress on policy adherence in any comparison" for Tier 3; looser for Tier 1).
   - Explicitly note the judge-reliability caveat: an LLM-as-judge comparison inherits known format-sensitivity and position-bias issues, so for Tier 3 recommend a human spot-check of a random 10% of judge verdicts before trusting the gate; for Tier 1/2 note it as an accepted residual risk.

5. **Define the canary stage.** Only after the shadow gate would pass:
   - Ramp schedule sized to risk tier: Tier 1 → 10% → 50% → 100%, 24h per stage minimum; Tier 2 → 5% → 25% → 100%, 48h per stage minimum; Tier 3 → 1% → 5% → 25% → 100%, 72h per stage minimum.
   - Name concrete rollback triggers: a judge-comparison score drop beyond a stated threshold on live canary traffic, an error-rate or latency regression beyond a stated percentage versus the pre-change baseline, and (for Tier 2/3) any user-reported or support-ticket signal tied to the change.
   - State explicitly that rollback must be to the exact previous prompt+model version, not "whatever was live before," which is why every event needs a version-pair tag — call this out even though tagging implementation is the project's job, not this plan's.

6. **List residual risks** specific to this change — at minimum, always include the judge-reliability caveat and the shadow-cost caveat; add others only if they're specific to what the user described (don't pad with generic risks).

## Output format

A single markdown document, in this exact section order:

```
# Rollout Plan: <short change description>

## Change Summary
<old vs new, one or two lines>

## Risk Tier: <TIER 1/2/3> — <one-sentence reason>

## Prerequisite: Offline Eval
<status: done/weak/missing, and what's needed if not sufficient>

## Shadow Stage
- Sample rate: <X%> for <Y days> (target: <N> comparisons)
- Arithmetic: <show the calculation>
- Cost impact: <estimate or "needs cost-per-request to quantify">
- Judge-comparison axes: <list>
- Promotion threshold: <concrete bar>
- Judge-reliability note: <spot-check recommendation if Tier 3>

## Canary Stage
- Ramp: <stage-by-stage % and minimum duration per stage>
- Rollback triggers: <concrete list>
- Rollback target: exact previous prompt+model version (requires version-pair tagging on every event)

## Residual Risks
- <bulleted list, specific to this change>
```

If any required input was missing and the user chose to proceed anyway with an assumption, mark that field inline as `[ASSUMED: <value>, confirm before executing]` rather than presenting it as given fact.

## Guardrails
- Never fabricate or silently assume a traffic number, cost figure, or eval score that wasn't provided — ask, or mark it `[ASSUMED]` per above.
- Never recommend skipping the offline-eval prerequisite for a Tier 2 or 3 change, even if the user is in a hurry — say so plainly and let them decide to override, don't make the decision for them by omitting the step.
- Never present the judge-comparison gate as infallible — the judge-reliability caveat is mandatory output, not optional color, on every plan.
- Never draft a plan for a change with no output-affecting content (pure infra/latency change) — tell the user this skill doesn't apply and why.
- This skill produces a plan, not a running pipeline — never imply the plan is already being executed or that traffic is already being shadowed; if the user wants that, point out that's the separate orchestrator component, which this plan is designed to feed into but doesn't replace.
