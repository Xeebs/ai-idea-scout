---
name: adversarial-critic-pattern-library
description: One-shot design aid that decides whether a described agent pipeline should add an adversarial producer-critic-revise stage, picks how aggressive it should be, and drafts the critic agent's persona and prompt — for someone weighing whether to bolt adversarial review onto a pipeline they already have, before building or adopting any runtime library for it.
---

# Adversarial Critic Stage Designer

## When to use this
Use this the moment someone describes an existing or planned agent pipeline (code generation, content drafting, research synthesis, decision support, anything with an LLM-produced output) and asks a question shaped like: "should we add an adversarial critic/review stage," "is it worth making this pipeline adversarial instead of just collaborative," "help me design a critic agent for this," "draft a critic prompt for our pipeline," or "how aggressive should our review stage be." This is a design/decision task, not a runtime: it produces a recommendation and a draft prompt, not a working LangGraph node or a measured benchmark. Reach for it once, per pipeline, before any engineering work to actually wire a critic stage in.

## Inputs
**Data source**: Manual — the user pastes a description of their pipeline and task; there is no connector. This skill never reads a live agent trace, a LangGraph/CrewAI graph definition, or production logs on its own — if the user wants those considered, they paste the relevant excerpt as text.

Ask for, if not already given:
1. **The task/domain** — what the pipeline produces (code, content, a decision memo, a research summary, etc.) and roughly how it's used downstream.
2. **The current pipeline** — its stages/agents as they exist today (e.g. "plan agent → generate agent → auto-merge," or "draft agent → human review → publish").
3. **Stakes** — what happens when a bad output slips through (a production incident, a published factual error, a wasted internal hour, nothing much). If the user doesn't state this, ask directly rather than guessing; if they still can't say, default to treating stakes as MEDIUM and say so explicitly in the output.
4. **Existing safety nets** — is there already a human reviewing every output before it takes effect? This changes the marginal value of an automated critic a lot and must be asked about if not volunteered.
5. *(Optional)* Cost/latency budget — how many LLM calls per output are already tolerated today, and any hard ceiling.

## Procedure
1. **Classify stakes and complexity**, each LOW / MEDIUM / HIGH:
   - *Stakes* = cost of a bad output slipping through (incidents, public errors, legal/financial exposure = HIGH; internal rework or minor embarrassment = MEDIUM; near-zero, caught by an existing downstream human gate = LOW).
   - *Complexity* = how much judgment the task requires (multi-step reasoning, code logic, factual claims = HIGH/MEDIUM; short-form, templated, or already-constrained output = LOW).
   - If the user didn't supply enough to classify either axis, ask one clarifying question before proceeding; only default to MEDIUM if they genuinely can't say, and flag that default explicitly in the output — never silently assume HIGH or LOW.
2. **Check for an existing safety net.** If a human already reviews every output before it takes effect AND stakes is LOW or MEDIUM, this weighs the recommendation toward DON'T ADD or a cheaper alternative, even if complexity is non-trivial — redundant review stages are a real cost with a real diminishing return.
3. **Decide the recommendation**:
   - **ADD** — stakes is HIGH, or (stakes MEDIUM and complexity HIGH) and no adequate existing human safety net.
   - **DON'T ADD** — stakes is LOW, or an existing human safety net already covers MEDIUM/LOW stakes with no complexity-HIGH escalation.
   - **ADD WITH GATING** — everything else (e.g. MEDIUM/MEDIUM with no safety net, or HIGH stakes but with a tight cost budget that rules out running the critic on every output) — recommend running the critic only on a defined subset (sampled outputs, outputs a cheap heuristic flags as risky, or only the highest-stakes stage of the pipeline).
4. **If the recommendation is ADD or ADD WITH GATING, choose an aggressiveness level**:
   - **Light** — single critic pass, flag-only, no automatic revision loop. Use when complexity is MEDIUM or the cost budget is tight.
   - **Medium** — one critic pass plus one bounded revision round (producer revises once, critic doesn't re-review the revision).
   - **Heavy** — iterative critic → revise loop, capped at a stated maximum (recommend 2-3 rounds, never unbounded), with escalating scrutiny each round. Use only when stakes is HIGH and complexity is HIGH.
5. **Draft the critic agent's persona and prompt**, tailored to the stated domain, always including:
   - A role statement naming what the critic is adversarial *toward* (the producer's output, not the producer agent itself).
   - A concrete severity scale (e.g. Critical / Major / Minor) so findings are triageable, not just a wall of objections.
   - A calibration guardrail sentence: the critic flags issues proportionate to the stakes classified in step 1 — it does not demand perfection from an early-stage or low-stakes draft.
   - A termination condition matching the chosen aggressiveness level (flag-only and stop; one revision round and stop; or "up to N rounds, stop early if zero Critical/Major findings").
   - An explicit instruction that the critic recommends, it never autonomously blocks, merges, publishes, or discards anything.
6. **Write a cost-tradeoff estimate** — the added LLM calls/rounds implied by the chosen aggressiveness level, framed explicitly as a design-time estimate, not a measured number. State plainly that validating the real catch-rate-per-dollar requires running the user's own before/after comparison on a sample of their actual outputs — never invent a specific catch-rate percentage.
7. **Close with next steps**: if they adopt this, wiring it into their actual framework (LangGraph, CrewAI, a plain loop) and benchmarking it against their collaborative-only baseline is separate engineering work this skill doesn't do.

## Output format
```
## Recommendation: ADD | DON'T ADD | ADD WITH GATING

### Stakes & Complexity Assessment
- Stakes: LOW/MEDIUM/HIGH — reasoning (note if defaulted)
- Complexity: LOW/MEDIUM/HIGH — reasoning (note if defaulted)
- Existing safety net: yes/no — reasoning

### Aggressiveness Level: Light | Medium | Heavy | N/A (if DON'T ADD)
Reasoning tied to the stakes/complexity/budget inputs above.

### Draft Critic Agent Prompt
```
<a complete, ready-to-use system prompt for the critic agent, domain-tailored,
including role, severity scale, calibration guardrail, termination condition,
and the no-autonomous-action instruction>
```

### Cost Tradeoff Estimate
- Added calls/rounds vs. the pipeline's current call count.
- Explicit disclaimer: this is a design-time estimate; measure real catch-rate-per-dollar on your own sample before committing.

### Next Steps
- What engineering work (framework adapter, benchmark run) remains if they adopt this, stated as out of scope for this skill.
```

## Guardrails
- Never invent a specific catch-rate, defect-rate, or percentage-improvement number — this skill designs the critic stage, it does not run or benchmark one. Any cost/benefit figures must be framed as design-time estimates with an explicit instruction to measure.
- Never skip the stakes/complexity classification — if the user's input is too thin to classify, ask first; only default to MEDIUM as a last resort, and say so in the output every time it happens.
- Never recommend ADD or ADD WITH GATING just because adversarial patterns are trendy — DON'T ADD must be a real, reachable outcome, especially when an existing human safety net already covers the stated stakes.
- Never draft a critic persona that can autonomously block, merge, publish, or delete anything — the critic always produces flags/recommendations for a human or an upstream revision step to act on.
- Never claim this produces a working runtime integration, a LangGraph/CrewAI node, or a validated benchmark — it produces a recommendation and a draft prompt only; say so explicitly in Next Steps.
- Never carry a recommendation over between pipelines or sessions — each pipeline gets classified fresh from what's given in that request.
