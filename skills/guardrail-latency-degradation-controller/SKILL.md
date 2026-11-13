---
name: guardrail-latency-degradation-controller
description: Designs a tiered degradation policy for a team's LLM guardrail checks under a latency/SLO budget — which checks drop first, what cheap fallback substitutes for each, and what gets flagged as unprotected. Use when a team has a set of guardrail checks, a measured latency cost per check, and a p99 latency budget they're currently violating or close to violating.
---

# Soft Landing: Guardrail Degradation Policy Designer

## When to use this
Use this when a team already runs LLM guardrail checks (classifiers, rule engines, LLM-judge calls) in front of a latency-sensitive production path (customer support, voice, real-time chat) and either:
- their p99 request latency is breaching budget because of the guardrail layer, or
- they currently handle any latency spike by disabling guardrails entirely rather than degrading gracefully, or
- they're about to ship a new guardrail layer and want a pressure-tested fallback plan before they need one.

This is a one-time (or periodic, when checks change) design pass — it produces a policy document, not a running system. If the user wants the policy actually enforced against live traffic, that's a build project (a proxy/middleware), not this skill.

## Inputs
**Data source**: Manual — the user pastes, for each guardrail check they run: its name, type (deterministic rule, ML classifier, or LLM-judge call), measured latency (p50 and/or p95/p99 in ms), what it catches (e.g. PII leakage, jailbreak/prompt injection, toxicity, brand/tone, format validation), and whether it's currently blocking (synchronous, must complete before the response is returned) or already async/sampled. The user also states their overall latency budget for the guardrail layer (a target p99 in ms) and whether checks run serially or in parallel today. (Note: the source idea file did not include an explicit **Data Sources** field — this classification was inferred from the idea's own Skill Angle, which describes a team "handing over" their checks and SLO, and is clearly a pasted-list workflow, not a live connector today.)

If the user doesn't have exact latency numbers, ask for at least rough estimates (even "LLM judge call ~400ms, regex filter <5ms" is enough) — do not invent numbers.

## Procedure
1. **Parse the check inventory.** Build a table: check name, type, latency (use p95 if given, else p50), what it catches, current blocking status. If any check is missing a latency number, flag it and ask rather than guessing.
2. **Compute current load.** Sum latencies (serial) or take the max (parallel, if the user says checks run concurrently) and compare to the stated budget. Report the headroom or overage explicitly, e.g. "6 checks totaling 540ms serial against a 300ms budget — 240ms over."
3. **Classify severity per check**, using the user's own labels where given; where not given, infer from what the check catches using this default ranking (state the inference explicitly, never silently):
   - **Critical**: PII/data leakage, jailbreak/prompt injection, illegal content.
   - **High**: toxicity/hate, self-harm content, hallucinated factual claims in high-stakes domains (medical/legal/financial).
   - **Medium**: brand tone, off-topic drift, format/schema validation.
   - **Low**: style nitpicks, verbosity checks, non-critical formatting.
4. **For each check, identify a cheaper fallback candidate** if one exists among the other checks or is a well-known deterministic substitute (e.g., LLM-judge toxicity check → keyword/regex blocklist + a small classifier; LLM-judge PII check → a deterministic PII-regex/NER library). If no credible cheap fallback exists for a Critical or High check, flag it explicitly as a **coverage gap** — never invent a fallback to make the table look complete.
5. **Draft the tiered degradation policy**, ordered so the cheapest, highest-severity checks are last to drop and the most expensive, lowest-severity checks are first to drop:
   - **Tier 0 (always-on)**: Critical-severity checks plus anything near-zero latency cost (<~10ms) regardless of severity.
   - **Tier 1 (drop under moderate pressure, e.g. >80% of budget consumed)**: Medium/Low severity checks with available cheap fallback or safe async-deferral.
   - **Tier 2 (drop under severe pressure, e.g. >95% of budget consumed, or an active SLO breach)**: everything else not in Tier 0, including High-severity checks only if a credible fallback was found in step 4 — otherwise keep them in Tier 0 and say so even though it means the budget can't be met without infra change.
   - Every dropped check gets an assigned fallback action: substitute-with-cheaper-check, defer-to-async/sampled-review, or (last resort, flagged) drop-with-no-replacement.
6. **Write the trigger thresholds** as a percentage of budget consumed (not raw ms, since budgets vary by deployment) so the policy is portable.
7. **Flag anything the policy cannot safely resolve** — e.g. a Critical check that's also the most expensive with no fallback. State plainly that this is an infrastructure/cost problem the policy can't paper over, not a tiering problem.

## Output format
A single Markdown document with these sections, in this order:
1. **Input summary table** — every check as parsed, with any inferred (not user-stated) fields marked `(inferred)`.
2. **Load assessment** — total/max latency vs. budget, overage or headroom in ms and %.
3. **Degradation policy table** — columns: Tier | Checks in tier | Trigger threshold | Action if triggered | Fallback substitute (or "none — coverage gap").
4. **Coverage gaps** — a called-out list of any Critical/High check with no fallback, each with one sentence on why it can't be safely dropped.
5. **YAML policy snippet** — a machine-readable rendering of the tiers/thresholds/fallbacks suitable for a team to hand to whoever builds the enforcement layer, e.g.:
   ```yaml
   budget_ms_p99: 300
   tiers:
     - name: tier_0_always_on
       trigger_pct_of_budget: 0
       checks: [pii_regex_filter, jailbreak_classifier]
     - name: tier_1_moderate_pressure
       trigger_pct_of_budget: 80
       checks: [brand_tone_llm_judge]
       action: defer_to_async
   coverage_gaps:
     - check: toxicity_llm_judge
       reason: "no deterministic fallback found; dropping removes all toxicity coverage"
   ```
6. **Open questions / assumptions made** — every severity inference and every fallback substitution the skill made without explicit user confirmation, listed so the team can correct them before adopting the policy.

## Guardrails
- Never drop a Critical-severity check to Tier 1 or Tier 2 unless the user explicitly reclassifies its severity or a genuine deterministic fallback was identified and named — "just drop it" under pressure is the exact failure mode this skill exists to prevent.
- Never invent a latency number, a fallback mechanism, or a severity label — state every inference explicitly in the Open Questions section so nothing silently becomes a hidden assumption.
- Never present this as a live/enforced policy — it is a design artifact for a human (or a separate build project) to implement and test against real traffic before trusting it in production.
- If the check inventory plus budget shows the SLO is mathematically unreachable even after full degradation (every check in Tier 0 still exceeds budget), say so plainly instead of forcing a tiering that pretends it works.
- Do not search the web or invent industry-standard latency benchmarks to fill gaps in what the user provided — ask for the missing number instead.
