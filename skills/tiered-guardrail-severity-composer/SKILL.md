---
name: tiered-guardrail-severity-composer
description: Reviews a team's current set of LLM guardrail/classifier checks (safety, compliance, tone, formatting, etc.) and drafts a severity-tiered fail-open/fail-closed policy plus a precedence order for resolving conflicting verdicts when multiple checks fire on the same response. Use when a team is standing up or auditing a layered guardrail stack (NeMo Guardrails, Guardrails AI, LLM Guard, or custom) and currently just "blocks on any failure" or has no documented per-category fail behavior.
---

# Tier Gate: Severity-Tiered Guardrail Policy Draft

## When to use this
Reach for this when a team says something shaped like "we have five different guardrail checks running and no idea which ones should actually block a response vs. just log it," or "we keep over-blocking on tone/formatting flags while an actual jailbreak check and a minor toxicity nit both fire on the same response and we're not sure which one should win," or "we're adding NeMo Guardrails / Guardrails AI / LLM Guard checks one at a time and never wrote down a policy for what happens when they disagree."

This is a one-time design/review pass that produces a draft policy document, not a running system. It does not call any guardrail model, does not execute classifiers, and does not enforce anything live. If what's actually wanted is the runtime engine that enforces this policy against real traffic and the benchmark that proves the false-block/missed-hazard rates, that is a separate build (the parent idea's "Project" — this skill is the design half, not the runtime half).

## Inputs
**Data source**: Manual — the user pastes/describes their own guardrail categories, which tool or classifier implements each, and the current block-vs-log behavior for each. There is no connector or API this reads from; nothing here is fetched automatically, and no mature cross-vendor connector exists today that could read a live guardrail config across NeMo Guardrails, Guardrails AI, and LLM Guard uniformly — this is a manual design conversation.

Required:
1. A list of the guardrail categories/checks currently running or planned (e.g., "PII detection," "jailbreak/prompt-injection," "toxicity," "brand tone," "factuality/hallucination," "output format validation"), and which tool/classifier implements each, even if only "custom regex" or "not sure yet."
2. The current behavior for each: always blocks the response, logs only, or "no defined behavior — we just added the check."

Strongly recommended (skip only if genuinely unavailable, and say so in the output):
3. 1–3 example scenarios where more than one check could plausibly fire on the same response (e.g., "a reply that's slightly off-brand in tone AND contains a borderline prompt-injection pattern").
4. Risk context: is this user-facing or internal, regulated industry or not, and any past incident shape — specifically whether the team has seen over-blocking complaints (support cost, friction) or a near-miss under-block (something harmful got through).

## Procedure
1. **Classify every stated category into a severity axis**, one at a time, using this heuristic:
   - **SAFETY-CRITICAL** — hazardous/illegal content, severe PII/secret leakage, security exploit, self-harm, CSAM-adjacent — anything where a miss causes irreversible real-world harm.
   - **COMPLIANCE** — regulatory or legal exposure (e.g., financial advice disclaimers, HIPAA-adjacent health claims, copyright) where a miss causes legal/contractual risk rather than direct physical/safety harm.
   - **BRAND/QUALITY** — tone, formatting, minor factual nits, style guide violations — a miss causes user annoyance or brand friction, not harm or legal exposure.
   - **AMBIGUOUS** — the category as described doesn't clearly map to one of the above, or the user's own description is too thin to tell (e.g., "content filter" with no detail on what it actually catches).
2. **Apply the default fail-mode per tier** — never skip this step by eyeballing it, always state the tier before the fail-mode:
   - SAFETY-CRITICAL → **fail-closed** (block the response, or redact/block the specific offending span) by default, always.
   - COMPLIANCE → **fail-closed** by default, always.
   - BRAND/QUALITY → **fail-open** (log the flag, let the response through) by default — UNLESS the user described a repeat incident or accumulated complaint volume tied to that specific category, in which case flag it as a candidate for fail-closed and say why.
   - AMBIGUOUS → do **not** default-assign a tier. List it under Open Questions with the single clarifying question needed to resolve it (usually: "what's the worst realistic thing that slips through if this check misses?").
3. **Draft the composition/precedence order.** When multiple checks fire on the same response, higher-severity fail-closed verdicts always override lower-severity fail-open verdicts, regardless of which check fired first chronologically. Write this as an explicit ranked list (e.g., 1. Safety-critical, 2. Compliance, 3. Brand/Quality) with one line of reasoning for the ranking — this is the rule that resolves "two checks disagree, which one wins."
4. **Validate against supplied scenarios.** If the user gave mixed-flag example scenarios, walk each one through the draft policy and state which verdict wins and why. If no scenarios were supplied, construct one plausible mixed-severity scenario per pair of adjacent-tier categories the user listed, label it clearly as "illustrative — not a reported incident," and walk it through the same way. Never present a constructed scenario as if it were something the user reported.
5. **Surface blind spots explicitly**, as their own list, not buried in the table:
   - Any category the user mentioned with "no classifier yet" or "not sure" behind it.
   - Any BRAND/QUALITY category flagged for fail-closed reconsideration due to stated repeat incidents.
   - Every AMBIGUOUS category, each with its specific resolving question.
6. **Assemble the final report** per the Output format below. If fewer than 2 categories were supplied, or none could be classified with any confidence, say so plainly in a confidence line at the top rather than padding the tables.

## Output format
A single markdown report with exactly these sections, in this order:

```
# Severity-Tiered Guardrail Policy — Draft

**Confidence**: [full / limited — note why if limited, e.g. "only 2 categories described, no example scenarios given"]

## 1. Policy Table
| Category | Classifier/tool | Severity tier | Fail mode | Rationale |
|---|---|---|---|---|
| ... | ... | SAFETY-CRITICAL/COMPLIANCE/BRAND-QUALITY/AMBIGUOUS | fail-closed/fail-open/UNRESOLVED | ... |

## 2. Composition / Precedence Order
1. [highest-severity tier] — overrides all below
2. [next tier]
3. [next tier]
Reasoning: [one line on why this ranking, not just a restatement of the list]

## 3. Worked Example(s)
[For each scenario — user-supplied or illustrative, clearly labeled which — show which check(s) fire, which verdict wins under the draft policy, and why]

## 4. Flagged Ambiguities / Open Questions
- [category]: [the specific question needed to resolve its tier]
- [category with no classifier yet]: [what needs to exist before this can be tiered]
- [BRAND/QUALITY category flagged for reconsideration]: [why, tied to stated incident]

## 5. What this draft does not do
This policy has not been validated against production traffic or a mixed-severity benchmark — it is a starting draft based on the categories and behavior described, not a measured false-block/missed-hazard rate. Before enforcing it live, run it against real or benchmark traffic covering both adversarial-high-severity and benign-low-severity cases in the same response.
```

## Guardrails
- Never default a category to fail-open if the user's own description touches safety, legal/compliance, PII, or security — always fail-closed, or AMBIGUOUS with a resolving question, never a silent downgrade.
- Never invent incident history, benchmark numbers, false-block rates, or missed-hazard rates not supplied by the user — this skill drafts a policy, it does not validate one. Section 5 of the output must always say so plainly.
- Never silently assign a severity tier to a category the user described too thinly to classify — put it in Open Questions with the specific question that would resolve it, instead of guessing.
- Never present a constructed/illustrative mixed-flag scenario as if the user reported it; label every scenario by its source (user-supplied vs. illustrative).
- Never recommend fail-open for a category without naming the specific thing that could slip through if that check misses, so the team chooses with eyes open rather than accepting a default blindly.
- Never present the drafted policy as production-ready — it is explicitly a pre-implementation design/review step, not the runtime enforcement engine or its benchmark validation.
