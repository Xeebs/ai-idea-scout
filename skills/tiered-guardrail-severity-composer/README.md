# Tier Gate: Severity-Tiered Guardrail Policy Draft

A self-contained prompt template for drafting a severity-tiered fail-open/fail-closed policy across a team's LLM guardrail checks (NeMo Guardrails, Guardrails AI, LLM Guard, or custom classifiers) — and a precedence order for resolving conflicts when more than one check fires on the same response. Paste the block below into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with your own guardrail details, and it will produce a draft policy document.

## When to use this

Use this when:
- You have more than one guardrail/classifier check running on model output (safety, toxicity, PII, jailbreak detection, brand tone, formatting, factuality, etc.) and currently just "block on any failure," with no documented reasoning for which checks should actually block vs. log-and-continue.
- You're about to add new guardrail checks and want a policy decided up front instead of hand-rolling ad hoc if/else logic for which failure wins when two checks disagree.
- You've had either over-blocking complaints (a minor tone/formatting flag killing a fine response) or a near-miss under-block (something that should have been caught wasn't), and want a structured severity tier instead of uniform "block everything" logic.

This produces a **draft policy document for a human to review and adopt** — it does not run, call, or configure any guardrail tool itself, and it does not validate the policy against real traffic. It is a design/review step that should happen *before* building or configuring the runtime enforcement logic, not a replacement for testing that logic against a benchmark of real and adversarial inputs once built.

## What to hand over

This is entirely manual — you paste in your own setup; nothing is fetched automatically, because no single tool today can read a unified config across NeMo Guardrails, Guardrails AI, and LLM Guard even if you use more than one.

Required:
1. **Your list of guardrail categories/checks** — e.g., "PII detection (Presidio), jailbreak/prompt-injection (NeMo Guardrails colang flow), toxicity (Guardrails AI toxic-language validator), brand tone (custom LLM-judge prompt), output format validation (JSON schema check)." Include what implements each, even if it's "custom regex" or "not decided yet."
2. **Current behavior for each** — does it always block the response today, does it only log, or is there no defined behavior yet?

Strongly recommended (if you skip these, say so — the output will note reduced confidence):
3. **1–3 scenarios where multiple checks could fire on the same response** — e.g., "a response that's slightly off-brand in tone but also contains a borderline prompt-injection pattern." Real examples are best; hypotheticals are fine too.
4. **Risk context** — user-facing or internal tool? Regulated industry? Have you had over-blocking complaints, or a near-miss where something harmful almost got through?

## The prompt

Paste this, filling in your own details where marked:

```
You are drafting a severity-tiered fail-open/fail-closed guardrail policy for my LLM application. Here is my setup:

GUARDRAIL CATEGORIES AND CURRENT BEHAVIOR:
[list each category, the tool/classifier behind it, and whether it currently blocks, logs only, or has no defined behavior]

MIXED-FLAG SCENARIOS (optional):
[describe 1-3 situations where more than one check could fire on the same response]

RISK CONTEXT:
[user-facing or internal; regulated industry or not; any past over-blocking complaints or under-block near-misses]

Do the following:

1. Classify each category I listed into one severity tier:
   - SAFETY-CRITICAL: hazardous/illegal content, severe PII/secret leakage, security exploits, self-harm — a miss causes irreversible real-world harm.
   - COMPLIANCE: regulatory/legal exposure (financial advice disclaimers, health claims, copyright) — a miss causes legal/contractual risk, not direct harm.
   - BRAND/QUALITY: tone, formatting, minor factual nits — a miss causes annoyance or brand friction, not harm or legal exposure.
   - AMBIGUOUS: I can't confidently place this from what was described.

2. Apply this default fail-mode per tier, and never skip stating the tier before the fail mode:
   - SAFETY-CRITICAL and COMPLIANCE -> fail-closed (block) by default, always.
   - BRAND/QUALITY -> fail-open (log, let it through) by default, UNLESS I described a repeat incident tied to that specific category, in which case flag it as a candidate for fail-closed and explain why.
   - AMBIGUOUS -> do not guess a tier. Put it in an Open Questions list with the specific question needed to resolve it.

3. Draft a precedence order: when multiple checks fire on the same response, higher-severity fail-closed verdicts always override lower-severity fail-open verdicts regardless of which fired first. Rank my tiers explicitly and give one line of reasoning for the ranking.

4. Walk any mixed-flag scenarios I gave through the draft policy, showing which verdict wins and why. If I gave none, construct one illustrative example per pair of adjacent-severity categories I listed, clearly labeled "illustrative, not a reported incident."

5. List every blind spot separately: categories with no classifier yet, BRAND/QUALITY categories flagged for fail-closed reconsideration due to stated incidents, and every AMBIGUOUS category with its resolving question.

6. Output the result in exactly this structure:

# Severity-Tiered Guardrail Policy - Draft

**Confidence**: [full / limited, and why if limited]

## 1. Policy Table
| Category | Classifier/tool | Severity tier | Fail mode | Rationale |
|---|---|---|---|---|

## 2. Composition / Precedence Order
[ranked list + one-line reasoning]

## 3. Worked Example(s)
[walked-through scenarios, labeled user-supplied or illustrative]

## 4. Flagged Ambiguities / Open Questions
[bulleted list, one resolving question per item]

## 5. What this draft does not do
[state plainly that this policy is unvalidated against real/adversarial traffic and needs benchmark testing before going live]

Rules you must follow:
- Never default anything touching safety, compliance, PII, or security to fail-open. Fail-closed or Open Questions only.
- Never invent incident history, false-block rates, or missed-hazard rates I didn't give you.
- Never silently guess a tier for a category I described too thinly - put it in Open Questions instead.
- Label every worked example by its source (mine vs. illustrative).
- Never claim this draft is production-ready.
```

## What you get back

A markdown report with five sections: a policy table mapping each of your categories to a severity tier and fail mode with a one-line rationale, an explicit precedence order for resolving conflicts between simultaneously-firing checks, one or more worked examples showing the policy in action, a list of ambiguous categories with the specific question needed to resolve each, and an explicit statement that the draft is unvalidated and needs real/benchmark traffic testing before enforcement.

## Guardrails — what this will never do

- Default anything touching safety, compliance, PII, or security to fail-open.
- Report a false-block rate, missed-hazard rate, or any other number about your specific setup that you didn't supply — it only drafts the policy, it doesn't measure it.
- Guess a severity tier for a category you described too thinly — it will ask instead.
- Present a made-up scenario as something you reported.
- Claim the drafted policy is ready to enforce in production without testing.

## Limits

This is a one-time design/review pass. It does not connect to NeMo Guardrails, Guardrails AI, LLM Guard, or any other tool, does not read your actual configuration files, and does not run any classifier. If you want the policy enforced live and proven against a benchmark of mixed-severity adversarial and benign traffic, that is separate runtime infrastructure this skill does not build.
