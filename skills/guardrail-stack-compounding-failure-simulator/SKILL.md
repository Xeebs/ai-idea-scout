---
name: guardrail-stack-compounding-failure-simulator
description: Computes the real end-to-end missed-hazard rate and false-block rate of a stacked (multi-layer) guardrail pipeline from each layer's measured accuracy/FP/FN numbers, instead of a naive single-accuracy guess, and ranks which layer dominates the result. Use before shipping or re-tuning a multi-layer guardrail stack (content filter → classifier → tool-call guard → output validator, etc.) when a team wants the actual compounded number rather than an eyeballed estimate.
---

# Stack Math: Guardrail Compounding-Failure Calculator

## When to use this
Trigger this when a team has — or is about to ship — two or more chained guardrail checks in front of or around an LLM (e.g. input content filter, topic classifier, tool-call guard, output validator) and wants to know the *actual* system-level reliability of that stack, not a rule-of-thumb guess. The tell is: "we have N guardrail layers, each individually tested at X% accuracy — what does the whole stack actually catch/block?" or "someone said stacking guardrails hurts more than it helps, is that true for our numbers?"

This is a one-shot calculation on the numbers as given. It does not run a live Monte Carlo service, does not monitor anything, and does not model what happens when a detector service itself crashes or times out (that is a different concern — an outage/fail-open-vs-fail-closed code audit, not an accuracy-compounding calculation). It only computes what the declared, measured per-layer detection accuracy compounds to across the full pipeline.

## Inputs
**Data source**: Manual — the team types or pastes each guardrail layer's measured accuracy/false-positive/false-negative rate, the declared pipeline order, and each layer's fail-open-vs-fail-closed policy. A future connected version could pull live per-layer pass/fail rates automatically from an observability backend (Langfuse, Arize, Datadog) that captures guardrail spans, but no mature connector purpose-built for "per-layer guardrail accuracy over time" exists today, so this stays a manual paste-in.

Required, per layer, in pipeline order:
1. **Name** (e.g. "content filter", "topic classifier").
2. Either (a) a **true-positive rate (TPR)** for catching genuinely hazardous input and a **false-positive rate (FPR)** for wrongly flagging benign input, OR (b) a single blended **accuracy** number if that's all the team has measured (see Step 2 for how this degrades the output).
3. **Fail-open or fail-closed** — what the layer does if it itself can't render a decision (timeout, abstain, crash). This is recorded and surfaced as a qualitative tail-risk note, not folded into the math (see Guardrails).

Optional:
4. A **traffic mix** — the assumed or measured ratio of hazardous to benign requests (e.g. "10% adversarial / 90% benign"). If omitted, report rates per-request (which don't depend on mix) and skip the absolute-incident-count projection.

If any layer is missing both the TPR/FPR split and an accuracy number, say so and ask for it — do not invent a plausible-looking number to fill the gap.

## Procedure
1. **Inventory the pipeline.** List every layer in declared order with whatever numbers were given. Flag any layer with no fail-open/closed policy stated as `POLICY UNSTATED` rather than assuming one.

2. **Normalize inputs.**
   - If a layer gives TPR and FPR directly: FNR (miss rate) = 1 − TPR.
   - If a layer gives only a single blended "accuracy" number: treat that number as both TPR and (1 − FPR) are unknown — you cannot split it. Explicitly state that this layer's contribution will only be computable in the simplified "naive AND-composition" estimate (Step 3), not in the separate missed-hazard/false-block breakdown (Step 4), and ask whether the team can supply the split. Do not assume FPR = FNR or any other even split — say the breakdown is unavailable for that layer.

3. **Compute the naive baseline** (what most teams eyeball without this tool): the simple product of every layer's single accuracy number, ∏ accuracy_i. This reproduces rule-of-thumb claims like "five layers at 90% each → ~59%" (0.9^5 ≈ 0.590). Report this number explicitly labeled "naive estimate" — it is the thing this tool exists to improve on, not the final answer.

4. **Compute the real, direction-aware metrics** (only for layers with a full TPR/FPR split; note any layer excluded for lacking one):
   - **Missed-hazard rate** = ∏ FNR_i across all split-available layers. This models the pipeline as a logical OR for detection: a hazardous item escapes only if every layer in the chain fails to catch it independently.
   - **False-block rate** = 1 − ∏ (1 − FPR_i) across all split-available layers. A benign item gets wrongly blocked if any single layer flags it.
   - State the independence assumption explicitly: these formulas assume each layer's errors are statistically independent of the others'. If layers share a model family, training data, or blind spot, real correlated failures will push the true missed-hazard rate higher than this ceiling — flag this as an optimistic-case caveat, not a guarantee.

5. **Apply traffic mix (if given).** For each preset or custom ratio supplied, project expected incident counts per 1,000 requests: hazardous_count × missed-hazard rate, benign_count × false-block rate. If no mix was given, report only the per-request rates from Step 4 and skip this projection.

6. **Sensitivity ranking.** For each split-available layer, recompute the missed-hazard rate and false-block rate with that layer removed entirely from the chain (i.e. set its FNR to 1 and FPR to 0, simulating "this layer isn't there"). Rank layers by how much removing them moves each metric:
   - The layer whose removal increases the missed-hazard rate the most is the **weakest-link catcher** — the stack depends on it most for detection.
   - The layer whose removal decreases the false-block rate the most (i.e. contributes the most to wrongly blocking benign traffic) is the **biggest false-block contributor**.
   - A layer whose removal barely moves either number is **flaggable as redundant** — call this out explicitly, it's one of the two failure modes this tool exists to surface (the other being an under-protected stack).

7. **Fail-open/closed tail-risk note.** List every layer marked fail-open and state plainly: "if this layer's detector itself errors or times out, hazardous traffic passes through unflagged — this risk is not included in the missed-hazard rate above, which only models detection accuracy, not operational outages." Do not attempt to quantify this without an explicit outage-rate input; point out that a dedicated outage/fail-open-vs-fail-closed code audit is the right tool for that question, not this calculator.

8. **Deliver the report** per the Output format below, leading with the delta between the naive estimate (Step 3) and the real computed metrics (Step 4), since that delta is the whole point of the exercise.

## Output format
A single report, in this order:

1. **Pipeline as understood** — table of layer name, order, TPR/FPR or accuracy-only, fail policy.
2. **Naive estimate** — the single ∏ accuracy_i number, labeled "what a back-of-envelope guess would say."
3. **Computed metrics** — missed-hazard rate and false-block rate (per-request, and per-1,000-requests if a traffic mix was given), labeled "what this specific stack, with these measured numbers, actually does."
4. **Delta** — one sentence contrasting naive vs. computed, in plain language (e.g. "the naive estimate undersells your false-block risk by 4x because it blends catch-rate and false-positive-rate into one number").
5. **Sensitivity ranking** — ordered list of layers by impact on missed-hazard rate, then by impact on false-block rate, naming the weakest-link catcher, the biggest false-block contributor, and any flaggable-redundant layer.
6. **Fail-open tail-risk note** — bullet per fail-open layer, or "none of the declared layers are fail-open" if so.
7. **Caveats** — independence assumption, any layer excluded from the real-metrics computation for lacking a TPR/FPR split, and a reminder this is a planning estimate, not a certification.

## Guardrails
- Never fabricate a per-layer TPR, FPR, or accuracy number that wasn't given. If a layer's numbers are missing or only partially given, say exactly what's missing and ask for it before computing anything for that layer — a guessed number presented as real data is worse than no number.
- Never silently assume a fail-open/fail-closed policy for a layer that didn't state one — report it as `POLICY UNSTATED`.
- Never model detector-service operational failure (crashes, timeouts, outages) as part of the missed-hazard or false-block rate — that is explicitly out of scope (see Step 7); conflating accuracy-compounding with outage risk is the single most likely way this tool misleads a team about its own confidence interval.
- Never present the computed numbers as a safety certification, compliance sign-off, or guarantee — they are a planning estimate for prioritizing engineering effort, built on the team's own self-reported measured numbers, which may themselves be stale, offline-eval-only, or not representative of live traffic.
- Never drop the independence-assumption caveat from the final report — correlated failures across layers sharing a model family or blind spot make the real-world missed-hazard rate higher than this ceiling, and a reader skimming only the headline number needs that caveat visible, not buried.
- If fewer than two layers are given, say this tool has nothing to compound and ask whether they meant to describe a single-layer guardrail (a different, simpler question) instead.
