# Adversarial Critic Stage Designer

A paste-in prompt for any AI chat tool. Describe a pipeline you already have (or are planning) where an LLM produces some output — code, content, a decision memo, a research summary — and this returns a one-shot recommendation on whether to bolt an adversarial producer-critic-revise stage onto it, how aggressive that stage should be, and a ready-to-use draft prompt for the critic agent itself. It does not build, wire up, or benchmark anything — it's the "should I even do this, and if so how" design step you take before any engineering work.

## When to use this

Use it when you're weighing whether to add a critic/review stage to a pipeline you're building or already running, deciding between a purely collaborative design and an adversarial one, or you just need a critic agent's persona and prompt drafted for a specific task. This is a one-time design decision per pipeline, not something you run continuously.

## What to give it

**Data source: Manual.** You paste everything — this does not read a live agent trace, a LangGraph/CrewAI graph, or production logs on its own. If you want those considered, paste the relevant excerpt as text.

1. **The task/domain** — what the pipeline produces and roughly how the output gets used (e.g. "generates small bug-fix PRs that auto-open against our repo," "drafts Instagram captions a social media manager reviews before posting").
2. **The current pipeline** — its stages/agents as they exist today.
3. **Stakes** — what happens when a bad output slips through: a production incident, a published error, wasted internal time, or next to nothing. If you're not sure, say so and it will ask or default conservatively.
4. **Existing safety nets** — does a human already review every output before it takes effect? This matters a lot for the recommendation.
5. *(Optional)* **Cost/latency budget** — how many LLM calls per output you already tolerate, and any hard ceiling.

## The prompt

Paste this whole block into your AI chat tool, then fill in your own details where indicated:

```
You are designing an adversarial producer-critic-revise stage for my agent pipeline. Follow this
procedure exactly. Do not skip steps, and do not invent numbers you weren't given.

STEP 1 — Classify two axes, each LOW / MEDIUM / HIGH:
- Stakes: the cost of a bad output slipping through (incidents, public errors, legal/financial
  exposure = HIGH; internal rework or minor embarrassment = MEDIUM; near-zero, already caught by a
  downstream human gate = LOW).
- Complexity: how much judgment the task requires (multi-step reasoning, code logic, factual
  claims = HIGH/MEDIUM; short-form, templated, or already-constrained output = LOW).
If I haven't given you enough to classify either axis, ask me one clarifying question before
continuing. Only default to MEDIUM as a last resort, and say explicitly that you defaulted.

STEP 2 — Check whether a human already reviews every output before it takes effect. If yes, and
stakes is LOW or MEDIUM, that weighs toward NOT adding a critic stage or toward a cheaper
alternative, even if complexity isn't trivial. A redundant review stage is a real cost with
diminishing returns — don't recommend adding one just because the pattern is popular.

STEP 3 — Decide the recommendation:
- ADD — stakes is HIGH, or (stakes MEDIUM and complexity HIGH) with no adequate existing human
  safety net.
- DON'T ADD — stakes is LOW, or an existing human safety net already covers MEDIUM/LOW stakes
  without a complexity-HIGH escalation.
- ADD WITH GATING — everything else (e.g. MEDIUM/MEDIUM with no safety net, or HIGH stakes but a
  tight cost budget). Recommend running the critic only on a defined subset: a sample of outputs,
  outputs a cheap heuristic flags as risky, or only the pipeline's highest-stakes stage.

STEP 4 — If the recommendation is ADD or ADD WITH GATING, pick an aggressiveness level:
- Light: single critic pass, flag-only, no automatic revision loop. Use for MEDIUM complexity or a
  tight budget.
- Medium: one critic pass plus one bounded revision round (the producer revises once; the critic
  does not re-review that revision).
- Heavy: iterative critic-to-revise loop capped at a stated maximum (recommend 2-3 rounds, never
  unbounded), with escalating scrutiny each round. Only for HIGH stakes and HIGH complexity.

STEP 5 — Draft the critic agent's persona and system prompt, tailored to my stated domain,
including all of:
- A role statement naming what the critic is adversarial toward: the producer's OUTPUT, never the
  producer agent itself.
- A concrete severity scale (e.g. Critical / Major / Minor) so findings are triageable.
- A calibration guardrail sentence: the critic flags issues proportionate to the stakes classified
  in Step 1 — it does not demand perfection from an early-stage or low-stakes draft.
- A termination condition matching the aggressiveness level chosen in Step 4.
- An explicit instruction that the critic recommends only — it never autonomously blocks, merges,
  publishes, or deletes anything.

STEP 6 — Write a cost tradeoff estimate: the added LLM calls/rounds implied by the chosen
aggressiveness level versus my pipeline's current call count. State explicitly that this is a
design-time estimate, not a measured number, and that I need to run my own before/after comparison
on a sample of my actual outputs to know the real catch-rate-per-dollar. Never invent a specific
catch-rate percentage.

STEP 7 — Close with next steps: note that wiring this into my actual framework (LangGraph, CrewAI,
a plain loop) and benchmarking it against a collaborative-only baseline is separate engineering
work this exercise doesn't cover.

STEP 8 — Output in exactly this format:

## Recommendation: ADD | DON'T ADD | ADD WITH GATING

### Stakes & Complexity Assessment
- Stakes: LOW/MEDIUM/HIGH — reasoning (note if defaulted)
- Complexity: LOW/MEDIUM/HIGH — reasoning (note if defaulted)
- Existing safety net: yes/no — reasoning

### Aggressiveness Level: Light | Medium | Heavy | N/A (if DON'T ADD)
Reasoning tied to the inputs above.

### Draft Critic Agent Prompt
<a complete, ready-to-use system prompt for the critic agent, following Step 5 exactly>

### Cost Tradeoff Estimate
- Added calls/rounds vs. my pipeline's current call count.
- Explicit note that this is a design-time estimate, not a measured one.

### Next Steps
- What engineering work remains if I adopt this, stated as out of scope here.

RULES YOU MUST FOLLOW:
- Never invent a catch-rate, defect-rate, or percentage-improvement number.
- Never skip the stakes/complexity classification — ask first if unclear; default to MEDIUM only
  as a last resort and say so.
- Never recommend ADD or ADD WITH GATING just because adversarial patterns are popular — DON'T ADD
  must be a real possible outcome.
- Never draft a critic that can autonomously block, merge, publish, or delete anything.
- Never claim this produced a working integration or a validated benchmark — only a recommendation
  and a draft prompt.

My task/domain:
<describe what the pipeline produces and how the output is used>

My current pipeline:
<describe the stages/agents as they exist today>

Stakes if a bad output slips through:
<describe, or say "not sure">

Existing safety net:
<is there already a human reviewing every output before it takes effect? yes/no/describe>

Cost/latency budget (optional):
<how many LLM calls per output you already tolerate, and any hard ceiling, or say "no constraint stated">
```

## What you get back

A recommendation (ADD / DON'T ADD / ADD WITH GATING) with the stakes-and-complexity reasoning behind it, an aggressiveness level if a critic stage is warranted, a complete draft system prompt for the critic agent tailored to your domain, a cost tradeoff estimate framed honestly as a design-time guess rather than a measured number, and a short list of the engineering work that's still ahead of you if you decide to adopt it.

## What this is not

This is not a benchmark, a LangGraph/CrewAI node, or a working runtime library. It does not measure your actual catch rate or cost — it tells you whether the pattern is worth trying for your specific pipeline and gives you a draft critic prompt to start from. If the recommendation is ADD or ADD WITH GATING and you like the draft, the next step is wiring it into your actual framework and running your own before/after comparison on real outputs — that's separate engineering work, not something a pasted prompt should claim to have already done for you.
