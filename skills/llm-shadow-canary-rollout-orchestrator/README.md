# Promote Gate: Shadow-to-Canary Rollout Plan Advisor

Paste this whole document into any AI chat tool (Claude, ChatGPT, Copilot, etc.) along with your answers to the "Tell me" section at the bottom, and it will draft a concrete, numbered rollout plan for shipping a prompt or model change safely.

## What this is for

You're about to change a prompt or swap a model behind a production LLM feature, and you want a real plan — specific sample rates, specific thresholds, specific rollback triggers for *your* traffic and *your* change — instead of either shipping blind or re-inventing the shadow-test-then-canary playbook from scratch. This produces the plan. It does not run anything for you; you (or your team's own tooling) execute it.

**Where this data comes from**: everything this needs, you type in directly — the change itself, your traffic volume, your eval results if you have them. There's no live connection to your LLM gateway or observability backend here; if you want the shadow-traffic-duplication and judge-scoring to run automatically instead of manually, that's a separate, heavier engineering project (a plugin sitting in front of your LLM gateway), and this plan is designed to be fed straight into something like that once you build or buy it.

## Instructions for the AI

You are drafting a shadow-test-then-canary rollout plan for a specific LLM prompt or model change. Follow this procedure exactly.

**First, check you have enough information.** You need, at minimum: (1) the actual old vs. new prompt text or old vs. new model names — not a vague description, the real content; (2) current traffic volume for the feature (requests/day or /hour, even approximate); (3) what the feature does and who it's for. If any of these three is missing or vague, ask for it before drafting anything. A plan built on a guessed traffic number or a hand-wavy change description is worse than no plan — it looks authoritative while being made up.

Also ask for, if not already given: existing offline eval results (or confirmation there are none), rough cost per request, and any notes on risk tolerance (does this touch money, safety, legal/compliance, or is there a kill switch already).

**Step 1 — Risk tier.** Classify the change as:
- **Tier 3 (high)**: touches money, safety, legal/compliance output, or is a full model swap on a customer-facing path.
- **Tier 2 (medium)**: a real prompt rewrite (not just wording) on a customer-facing feature, or any change on an internal feature whose output feeds business decisions or reports.
- **Tier 1 (low)**: a minor wording tweak, few-shot example change, or parameter tweak on an internal/low-stakes feature.

State the tier and the one specific fact that drove the classification.

**Step 2 — Offline eval check.** If there's no offline eval, or a weak one (small sample, no explicit pass bar), say so plainly and specify the minimum bar needed first: a held-out set of 20-30 representative inputs, scored against the *current live* version's output on the same inputs, with an explicit pass threshold. For Tier 2/3 changes, treat this as a blocking prerequisite — don't draft the shadow stage as if it already passed.

**Step 3 — Size the shadow stage.** Shadow mode means the candidate version generates output on real traffic but that output is never shown to users — only compared against the live version's output on the same input, by a judge.
- Target comparisons needed: 200 for Tier 1, 400 for Tier 2, 800 for Tier 3.
- Compute: `sample_rate = target_comparisons / (daily_volume × duration_days)`, choosing a duration between 1 and 7 days. If the math pushes sample rate above 100%, lengthen the duration instead of exceeding 100%.
- Show your arithmetic, not just the final number.
- Estimate the cost impact: shadow mode roughly doubles inference spend on the sampled slice for the shadow window. If a cost-per-request was given, compute the rough dollar cost; if not, say explicitly that you need it to quantify this.

**Step 4 — Judge-comparison gate.** Pick 2-4 comparison axes specific to what this feature actually does (for a support chatbot: correctness, tone/policy adherence, resolution rate; for a summarizer: factual coverage, length adherence, omitted key points — adapt to the real feature described). State a concrete promotion threshold (e.g. "candidate must win or tie on correctness in ≥90% of comparisons, zero regressions on policy adherence" for Tier 3; looser for Tier 1). Always add this caveat: LLM-as-judge comparisons are known to be sensitive to output format and have position bias, so for Tier 3 recommend a human spot-check of ~10% of judge verdicts before trusting the gate; for Tier 1/2, note it as an accepted residual risk.

**Step 5 — Canary stage.** Only sketched for after the shadow gate would pass:
- Tier 1 ramp: 10% → 50% → 100%, minimum 24h per stage.
- Tier 2 ramp: 5% → 25% → 100%, minimum 48h per stage.
- Tier 3 ramp: 1% → 5% → 25% → 100%, minimum 72h per stage.
- Concrete rollback triggers: a judge-comparison score drop beyond a stated threshold on live canary traffic, an error-rate or latency regression beyond a stated percentage against the pre-change baseline, and (Tier 2/3) any user-reported or support-ticket signal tied to the change.
- Note that rollback must restore the *exact* previous prompt+model version — which only works if every logged event is tagged with its exact version pair; flag this as a requirement even though implementing the tagging is outside this plan's scope.

**Step 6 — Residual risks.** Always list the judge-reliability caveat and the shadow-cost caveat. Add anything else only if it's specific to the actual change described — don't pad with generic risk language.

**Output exactly this structure:**

```
# Rollout Plan: <short change description>

## Change Summary
<old vs new>

## Risk Tier: <1/2/3> — <one-sentence reason>

## Prerequisite: Offline Eval
<status and what's needed if insufficient>

## Shadow Stage
- Sample rate: <X%> for <Y days> (target: <N> comparisons)
- Arithmetic: <the calculation>
- Cost impact: <estimate or note that cost-per-request is needed>
- Judge-comparison axes: <list>
- Promotion threshold: <concrete bar>
- Judge-reliability note: <spot-check recommendation if Tier 3>

## Canary Stage
- Ramp: <stages, percentages, minimum durations>
- Rollback triggers: <concrete list>
- Rollback target: exact previous prompt+model version (requires version-pair tagging on every event)

## Residual Risks
- <specific bullets>
```

If you proceeded with any assumed value because the user chose not to provide it, mark it inline as `[ASSUMED: <value>, confirm before executing]` rather than presenting it as a known fact.

**Never do:**
- Never invent a traffic number, cost figure, or eval score that wasn't given — ask, or mark it `[ASSUMED]`.
- Never recommend skipping the offline-eval prerequisite for a Tier 2/3 change — flag it even if the user seems eager to skip ahead.
- Never present the judge-comparison gate as infallible — the reliability caveat is mandatory, every time.
- Never draft a plan for a change with no output-affecting content (e.g. a pure latency/infra change with identical outputs) — say this skill doesn't apply and explain why.
- Never imply the plan is already running or that traffic is already being shadowed — this produces a plan for a human (or a separate automated system) to execute, nothing here executes it.

---

## Tell me (fill this in before running the above)

1. **The change**: old prompt/model vs. new prompt/model (paste actual text or exact model names)
2. **Current traffic volume** for this feature (requests/day or /hour)
3. **What the feature does and who it's for**
4. **Existing offline eval results**, if any (or say "none yet")
5. **Rough cost per request**, if known
6. **Anything about risk tolerance** — does this touch money/safety/compliance, is there a kill switch, etc.
