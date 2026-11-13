---
name: nonprofit-ai-deployment-playbook
description: Turns a nonprofit's usage profile into a written AI-stack recommendation with a realistic cost range, reliability caveats, and a fallback plan — use when a nonprofit ops person or technical volunteer is choosing which AI provider/hosting stack to deploy before committing budget.
---

# Nonprofit AI Deployment Playbook

## When to use this
A nonprofit ops person, ED, or technical volunteer is about to pick an AI stack (for an FAQ chatbot, document Q&A over program materials, translation, or a similar client-facing or internal workload) and wants a decision, not a generic "best AI tools for nonprofits" listicle. Reach for this skill before budget or a vendor contract is committed — not after an org has already hit an undisclosed rate limit or a "not intended for production use" wall mid-deployment.

## Inputs
**Data source**: Manual + Connected — the org's usage profile (workload type, expected monthly volume, budget ceiling, data sensitivity, technical capacity, region) is typed in by the user (Manual); current vendor terms (AWS nonprofit credits/Bedrock, Oracle Cloud Always Free, Scaleway free tier, Hugging Face free/PRO, OpenAI/ChatGPT nonprofit pricing, Anthropic/Claude for Nonprofits, and self-hosted-via-Ollama hardware costs) are checked live via web search (Connected — a mature, already-available capability in any web-search-enabled chat tool), never pulled from training-data memory of old pricing.

Required manual fields — ask for any that are missing before proceeding, never assume them:
1. **Workload type(s)** — e.g. FAQ chatbot, document Q&A/RAG over program materials, translation, something else.
2. **Expected monthly volume** — approximate users/month and queries or documents per month.
3. **Budget ceiling** — a real number (even "basically $0" is a valid, important answer).
4. **Data sensitivity** — does this touch client/beneficiary PII, health data, immigration status, or other sensitive information?
5. **Technical capacity** — no dedicated IT / one part-time volunteer / dedicated technical staff.
6. **Region/country** — affects which nonprofit discount programs and data-residency rules apply.

## Procedure
1. **Intake check.** Confirm all six required fields above are present. If any are missing, ask for them explicitly before doing anything else — do not guess a budget or sensitivity level on the org's behalf.
2. **Live-check current vendor terms** for each of these candidate stacks via web search, not memory, and record the source URL and the date checked for every number used downstream:
   - AWS nonprofit credits / Bedrock pay-as-you-go
   - Oracle Cloud Always Free
   - Scaleway free tier
   - Hugging Face free tier + PRO ($/mo)
   - OpenAI/ChatGPT nonprofit or Team pricing
   - Anthropic Claude for Nonprofits pricing
   - Self-hosted via Ollama on budget hardware (one-time hardware cost + electricity, no per-query fee)
   For each, explicitly capture: current free-tier limits, any "not intended for reliable/commercial/production use" disclaimer language, nonprofit discount terms and eligibility restrictions, and known rate-limit behavior.
3. **Map the workload to a resource profile.** FAQ chatbots are low-token, high-concurrency, latency-sensitive. Document Q&A/RAG adds embedding + vector storage cost and scales with corpus size, not just query count. Translation is typically batchable and latency-tolerant. This changes which free-tier caps actually bind.
4. **Score each candidate stack** against the org's profile:
   - Does projected cost at stated volume fit the budget ceiling, using the live-checked numbers (not best-case marketing numbers)?
   - Does the provider's own disclaimer language rule it out for this data-sensitivity level (e.g. a tier explicitly marked "not for reliable/commercial use" is disqualifying for anything touching beneficiary PII or a client-facing mission-critical flow)?
   - Does the org's technical capacity support the stack (self-hosted options require real technical capacity; a no-IT org should not be steered toward self-hosting without a strong caveat)?
   - Is a nonprofit discount program actually available in the org's region, and does the org likely qualify (check stated eligibility exclusions, e.g. government/academic exclusions some programs apply)?
5. **Pick a primary recommendation and a fallback.** The fallback must name the specific triggering condition (e.g. "if you exceed 2,000 queries/month on the free tier" or "if the free tier's 'not for commercial use' clause gets enforced") and what to switch to when it fires — this is the step that prevents the exact forced-mid-deployment-switch crisis the org is trying to avoid.
6. **Write the recommendation** in the Output format below. If live search could not confirm current terms for a candidate (e.g. a vendor page didn't load or terms look stale), say so explicitly rather than silently falling back on older pricing knowledge.

## Output format
A single written recommendation, structured as:

```
## Recommended Stack: <name>

**Why this fits your profile:** 2-4 sentences tying the choice to the org's stated
workload, volume, budget, sensitivity, and technical capacity.

**Realistic monthly cost range:** $X-$Y (sourced from live-checked vendor terms,
not best-case marketing figures) — cite source + date checked.

**Reliability caveats to expect:** bullet list of specific things that will go
wrong or need attention (rate limits, "not for production use" disclaimers,
latency under load, data residency/retention terms), each tied to a source.

**Fallback plan:** the specific trigger condition and the specific stack/action
to switch to when it fires.

## Alternatives considered and rejected
One line each for 1-2 runner-up stacks and why they were ranked below the
recommendation for this org specifically.

## Sources checked (with date)
Every vendor page or term consulted, with the date checked — no number in this
report should be untraceable to this list.

## Flags for human follow-up
Anything this skill cannot verify itself (e.g. "if beneficiary health data is
involved, get a privacy/legal review of <vendor>'s data retention terms before
committing — this skill did not verify ToS legal enforceability").
```

## Guardrails
- Never state a cost, rate limit, or free-tier term without a live-checked source and date — vendor free-tier terms change unpredictably, and reusing stale knowledge-cutoff pricing recreates the exact "low-cost AI illusion" this skill exists to prevent.
- Never recommend a stack whose own provider disclaims reliable/commercial/production use for a workload the org flagged as client-facing or touching sensitive beneficiary data, without surfacing that disclaimer prominently as a rejection reason or a loud caveat.
- Never skip the fallback plan — a recommendation with no named trigger condition and no named next step is not a usable deployment plan, it's a guess.
- Never guess a missing required manual input (budget, sensitivity, technical capacity) — ask for it.
- Never claim to have verified ToS legal enforceability, data-residency compliance, or HIPAA/GDPR-equivalent status — flag these for a human legal/privacy review instead of asserting compliance.
- Never present this as a one-time, permanent answer — note that free-tier terms drift and the org should re-run this check before any major scale-up or at least every 2-3 months.
