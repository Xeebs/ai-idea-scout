---
name: minimal-self-hosted-llm-observability-library
description: Build-vs-buy decision aid for LLM observability — scores a team's stack, request volume, and team size against four tiers (skip it, minimal self-hosted library, buy a vendor platform, full custom build) and, if a lightweight library fits, produces a first-week instrumentation plan. Use when a team is about to adopt observability tooling and hasn't committed engineering time yet.
---

# Minimal Self-Hosted LLM Observability — Build-vs-Buy Decision Aid

## When to use this
A solo developer or small team (roughly under 10 engineers) running an LLM-backed product is about to decide how to get visibility into prompts, responses, latency, cost, and failures — and is weighing three real options: do nothing extra and read provider dashboards, adopt a minimal self-hosted logging library, or buy a vendor platform (Langfuse, Helicone, LangSmith, Arize, etc.). Use this skill *before* any engineering time is spent, not after a tool is already half-integrated. Do not use this for teams that already have a dedicated ML-ops/eval engineer and are choosing between enterprise platforms — that is a different, higher-stakes evaluation this skill is not scoped for.

## Inputs
**Data source**: Manual — the user pastes a description of their current LLM stack (which SDK/providers they call), request volume (requests/day), team size (specifically how many engineers could maintain observability tooling, not total headcount), any data-residency or compliance constraint, and what's currently missing or painful (e.g., "we can't tell why costs spiked last week").

If any of these five are missing, ask for them before producing a recommendation — do not guess request volume or compliance posture.

## Procedure
1. **Collect the five inputs**: stack/providers, request volume/day, engineers available to maintain tooling, data-residency/compliance constraint (yes/no/unsure), and the specific pain point driving the request.
2. **Classify into one of four tiers** using these explicit thresholds — never skip straight to a verdict without checking each in order:
   - **Tier 1 — Skip dedicated tooling.** Request volume is low enough (roughly under 1,000 requests/day) and the team is pre-product-market-fit, such that reading the LLM provider's own usage dashboard answers the stated pain point. Recommend revisiting once volume or team size grows.
   - **Tier 2 — Minimal self-hosted library.** Team has no dedicated ops/eval engineer, wants prompt/response/latency/cost tracing without SaaS lock-in or recurring cost, and either has a data-residency constraint or simply doesn't want a third party holding prompt/response data. This is the default recommendation for the population this skill targets: small teams who today either skip observability or hand-roll a throwaway script.
   - **Tier 3 — Buy a vendor platform.** Team has (or is about to hire) a dedicated eval/ops role, needs features a minimal library won't have (dataset evals, human annotation queues, A/B testing, SSO/enterprise compliance), and is willing to accept recurring cost and a third party processing prompt/response data.
   - **Tier 4 — Build fully custom.** Requirements are genuinely unmet by both a minimal library and vendor platforms (e.g., a highly specific internal data pipeline integration), and the team has sustained engineering capacity to maintain a bespoke tool indefinitely — flag this as the highest-risk, highest-cost option and ask the user to confirm Tier 2/3 were genuinely insufficient before committing to it.
3. **Write the recommendation**, citing the specific input values that drove the tier (e.g., "800 req/day and no dedicated ops engineer → Tier 2").
4. **Name what's given up** by not choosing each of the other three tiers in one line each — this is a decision aid, not a verdict with no visible tradeoffs.
5. **If Tier 2 is recommended**, produce a first-week instrumentation plan: which calls to wrap first (primary user-facing completion calls before background/batch jobs), the exact fields to log (prompt, response, latency, model, cost, error, a trace/session id to group multi-turn calls), the storage choice (SQLite under ~10k requests/day, Postgres above that), and a one-sentence note on what "done" looks like for week one (e.g., "you can answer: what was our slowest and most expensive call yesterday, and why").
6. **Set a revisit trigger** — a concrete number (request volume or team size) at which the recommendation should be re-run, so the decision isn't treated as permanent.

## Output format
```
## Recommendation: Tier <N> — <name>

**Why**: <one or two sentences citing the specific input values>

**What you give up by not choosing the others**:
- Tier 1 (skip tooling): <one line>
- Tier 2 (minimal library): <one line>
- Tier 3 (buy vendor platform): <one line>
- Tier 4 (build custom): <one line>
(omit the line matching the recommended tier itself)

**Instrumentation plan** (only if Tier 2):
- Wrap first: <specific call path>
- Log fields: <list>
- Storage: <SQLite or Postgres, with the volume reasoning>
- Week-one done-state: <one sentence>

**Revisit this recommendation if**: <concrete trigger, e.g. "request volume crosses 5,000/day" or "you hire a dedicated eval engineer">
```

## Guardrails
- Never produce a recommendation without asking for and citing all five inputs — a generic "it depends" answer with no numbers is a failed run of this skill.
- Never present a vendor's own build-vs-buy blog content as a neutral source if referenced — most public guides on this topic are vendor-authored and lean toward "buy"; flag this bias explicitly if the user mentions having read one.
- Never recommend Tier 4 (full custom build) as a first answer — it is only reachable after confirming Tiers 2 and 3 were checked and found insufficient, because reinventing a minimal library or a vendor platform from scratch is the exact waste of engineering time this skill exists to prevent.
- Never recommend Tier 3 (buy) when the user has stated a hard data-residency/compliance constraint that the named vendor doesn't satisfy — flag the conflict instead of papering over it.
- Never skip the "revisit trigger" — a build-vs-buy call made once and never revisited is how teams end up locked into the wrong tier as they scale.
