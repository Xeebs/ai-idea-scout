# Scenario 1 — Early-stage SaaS, small team, no ops engineer

## Input

> We're a 3-person team building an AI-powered customer support triage tool. We call the Anthropic API directly from a Node backend (no framework, just the SDK) for every ticket that comes in — roughly 1,800 tickets/day right now, growing. None of us has ever worked in ML ops; we're all generalist full-stack engineers. We don't have a formal data-residency requirement, but customer ticket content does include personal info (names, emails, account numbers) and we'd rather not pipe that through a third party if we can avoid it. Our actual problem: we had a day last week where our Anthropic bill tripled and we have no idea which tickets or which part of our flow (initial classification call vs. follow-up summarization call) caused it. We just want to know what's happening.

## Expected behavior

- Recognizes all five required inputs are present: stack (Anthropic SDK, Node), volume (~1,800/day), team size/maintenance capacity (3 generalist engineers, none dedicated to ops), data-residency-adjacent constraint (PII, reluctance to pipe through third party), and the specific pain point (cost spike, can't attribute to which call).
- Walks the tiers in order and lands on **Tier 2 (minimal self-hosted library)**: volume is above the Tier 1 "just read the dashboard" threshold (~1,000/day) and there's a real pain point dashboards apparently aren't answering (per-call attribution); no dedicated ops engineer argues against Tier 3; the stated reluctance to send PII-bearing content to a third party is a genuine, if informal, data-handling constraint supporting Tier 2 over Tier 3; nothing here demands Tier 4.
- Cites the actual numbers/facts in the "Why" (1,800/day, 3 generalist engineers, PII reluctance, unattributed cost spike) — not a generic justification.
- Gives one-line tradeoffs for Tiers 1, 3, and 4 (omitting Tier 2 since it's the recommendation).
- Produces an instrumentation plan: wrap the initial classification call and the follow-up summarization call separately (so they're distinguishable later — directly answering the stated pain point), log prompt/response/latency/model/cost/error plus a trace id grouping both calls per ticket, recommends SQLite (volume is well under 10k/day), and states a week-one done-state framed around being able to attribute cost by call type.
- States a concrete revisit trigger (e.g., "if volume crosses ~10,000/day" or "if you hire a dedicated ops/eval engineer").

## Pass/fail criteria

- PASS if the recommendation is Tier 2, is justified with the specific numbers given (not boilerplate), includes a usable instrumentation plan naming the two distinct call types from the prompt, and includes a revisit trigger.
- FAIL if it recommends Tier 1 (ignores the stated real pain point the dashboard isn't solving), Tier 3 (ignores the stated no-ops-engineer and PII-reluctance facts), or gives a generic "it depends" without tying to the inputs.
- FAIL if the instrumentation plan is generic boilerplate that doesn't address the actual stated problem (distinguishing classification-call cost from summarization-call cost).
