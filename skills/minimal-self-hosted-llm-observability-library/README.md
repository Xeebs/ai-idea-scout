# LLM Observability Build-vs-Buy Decision Aid

Paste this into any AI chat tool when your team is deciding how to get visibility into your LLM calls — prompts, responses, latency, cost, errors — and you haven't spent engineering time yet. It walks through four concrete options (skip it, run a minimal self-hosted library, buy a vendor platform, or build something fully custom) and tells you which one fits your actual numbers, not a generic "it depends."

## When to use this

You're running an LLM-backed product or side project and you're about to decide: do we just read our provider's usage dashboard, adopt a lightweight self-hosted logging tool, pay for a platform like Langfuse/Helicone/LangSmith/Arize, or write something custom in-house? Use this before committing engineering time to any of the four, not after you've half-integrated one.

This is not for teams that already have a dedicated ML-ops/eval engineer choosing between two enterprise platforms — that's a more specialized evaluation than this covers.

## What to hand over

This is a manual, paste-in skill — nothing here reads your systems directly. Give it:

1. **Your current LLM stack** — which provider SDK(s) you call (OpenAI, Anthropic, etc.) and how.
2. **Request volume** — roughly how many LLM requests/day you make today (or expect soon).
3. **Team size available for this** — not total headcount, specifically how many engineers could maintain observability tooling if you built or ran one.
4. **Data-residency or compliance constraint** — yes, no, or unsure: does prompt/response data need to stay inside your own infrastructure?
5. **The specific pain point** driving the request — e.g., "we can't tell why our API costs spiked last week" or "we have no idea which prompts are failing in production."

If you don't provide all five, the assistant should ask for them before giving a recommendation — a build-vs-buy call made without real numbers isn't worth acting on.

## The procedure the assistant should follow

1. Collect the five inputs above.
2. Walk through four tiers in order, using these thresholds:
   - **Tier 1 — Skip dedicated tooling.** Roughly under 1,000 requests/day and the stated pain point is actually answered by your LLM provider's own dashboard. Just use that; revisit once volume grows.
   - **Tier 2 — Minimal self-hosted library.** No dedicated ops/eval engineer on the team, you want prompt/response/latency/cost tracing without handing your data to a third party or taking on recurring SaaS cost, and/or you have a data-residency constraint. This is the right fit for most small teams (under ~10 engineers) running an early-stage LLM product — it's a lightweight, self-hosted logging layer you run yourself, not a smaller version of an enterprise platform.
   - **Tier 3 — Buy a vendor platform.** You have (or are hiring) a dedicated eval/ops role and need features a minimal library won't give you — dataset evaluations, human annotation queues, A/B testing, SSO/enterprise compliance — and you're fine with recurring cost and a third party processing your prompt/response data.
   - **Tier 4 — Build fully custom.** Only reachable after Tiers 2 and 3 are genuinely confirmed insufficient (e.g., a very specific internal pipeline integration nothing off-the-shelf covers), and only if your team has sustained capacity to maintain a bespoke tool indefinitely. This is the highest-cost, highest-risk option — don't default to it.
3. State the recommendation and cite the actual numbers that drove it (e.g., "800 requests/day, no dedicated ops engineer → Tier 2").
4. Name, in one line each, what you give up by *not* picking each of the other three tiers — this should feel like a real tradeoff analysis, not a single verdict dropped with no reasoning.
5. **If Tier 2 (minimal library) is the answer**, also produce a first-week instrumentation plan:
   - Which calls to wrap first (your primary user-facing completion calls, before background or batch jobs).
   - Exactly what fields to log: prompt, response, latency, model name, cost, error, and a trace/session id to group related calls.
   - Storage choice: SQLite if you're under roughly 10,000 requests/day, Postgres above that.
   - What "done" looks like after week one — e.g., "you can answer: what was our slowest and most expensive call yesterday, and why."
6. Set a **revisit trigger** — a concrete number (request volume or team headcount) at which this recommendation should be re-run, so it's treated as a living decision, not a permanent one.

## Output format

```
## Recommendation: Tier <N> — <name>

**Why**: <reasoning tied to your actual numbers>

**What you give up by not choosing the others**:
- Tier 1 (skip tooling): ...
- Tier 2 (minimal library): ...
- Tier 3 (buy vendor platform): ...
- Tier 4 (build custom): ...
(the tier you were recommended is omitted from this list)

**Instrumentation plan** (only shown if Tier 2 was recommended):
- Wrap first: ...
- Log fields: ...
- Storage: ...
- Week-one done-state: ...

**Revisit this recommendation if**: <a concrete number or event>
```

## Guardrails

- Don't accept a recommendation with no numbers attached — if the assistant gives you a generic "it depends," push back and re-supply the five inputs.
- Most public "build vs buy LLM observability" articles are written by vendors who sell the "buy" answer — treat any such source as biased marketing, not a neutral comparison.
- Full custom build (Tier 4) should never be the first answer you get — it's only valid after a minimal library and a vendor platform have both been ruled out for a specific, stated reason.
- If you have a hard data-residency or compliance requirement, a vendor-platform recommendation that doesn't satisfy it is wrong — call that out rather than ignoring the conflict.
- A decision without a stated revisit trigger isn't finished — make sure you get one.
