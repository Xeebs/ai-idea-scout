# Scenario 1 — Mixed read-only/side-effecting specialist roster (the realistic "no" or "narrower-scope" case)

## Input (what the user pastes)

"We're on Vapi with a GPT-4-class triage model that classifies the caller's first full utterance into one of five intents, then hands off serially. Specialists:

1. Billing agent — looks up account balance via our internal API (read-only query), and can also issue refunds up to $50 without further approval.
2. Technical support agent — walks through a scripted troubleshooting flow, no external writes, purely conversational and informational.
3. Sales agent — answers pricing/plan questions (read-only), and can send a follow-up SMS with a quote link if the caller asks.
4. Scheduling agent — books or reschedules appointments by writing directly to our calendar system.
5. Human transfer — escalates the call to a live agent queue, removing the caller from the AI flow entirely.

We're measuring about 1.5 seconds of dead air between the caller finishing their sentence and the specialist starting to respond. We want to know if a parallel-dispatch redesign is worth building, and if so, what it should look like."

## Why this is realistic
Five specialists, a genuine mix of read-only and three different flavors of side-effecting action (a monetary action, a communication action, and a data-write action, plus an irreversible human handoff) — exactly the messy real-world roster the idea file's "Risks & Open Questions" flags as the hard case, not a toy all-read-only example.

## Pass criteria
- [ ] Output includes all 7 named sections (Architecture Reviewed, Specialist Classification, Pre-Filter Recommendation, Arbitration Policy, CallSphere Failure-Mode Check, Recommendation, Suggested Validation Benchmark).
- [ ] Specialist Classification table correctly separates: Technical support = read-only/idempotent; Billing = side-effecting (lookup is reversible/safe to fire, but the $50 refund action itself must be flagged as not safe to fire speculatively); Sales = reversible for the pricing answer but the SMS send flagged as not safe to fire speculatively; Scheduling = side-effecting/irreversible (calendar write); Human transfer = irreversible, "do not fire until commit."
- [ ] Pre-Filter Recommendation is triggered (5 specialists > 3) and recommends a narrowing step before parallel fire — does not recommend blind fire-all-5.
- [ ] CallSphere Failure-Mode Check section explicitly names the 18%-vs-60% result and increased wasted calls, and states a reasoned judgment (not a vague "it depends") on whether this specific 5-specialist mix is likely to hit that same failure without a pre-filter.
- [ ] Recommendation is Narrower-Scope (or a clearly-reasoned Go/No-Go) — given 3 of 5 specialists have real side effects, the output should not recommend parallelizing the full roster without qualification; it should call out which specialists (at minimum Technical support, and the read-only portion of Billing/Sales) are the safe parallel subset.
- [ ] No invented latency percentage (e.g., does not assert "this will cut your 1.5s to 0.6s") since no benchmark data was supplied by the user — only qualitative tradeoff language.
- [ ] Cancellation instructions for Scheduling and Human transfer explicitly say "do not fire until commit," never "cancel cleanly."

## Fail conditions
- Recommending blind parallel-fire of all 5 specialists with no pre-filter.
- Claiming any side-effecting specialist (refund, SMS, calendar write, human transfer) can be "cleanly cancelled" after firing.
- Fabricating a specific latency number not derivable from the input.
- Omitting the CallSphere failure-mode check or treating it as a throwaway line rather than a reasoned section.
