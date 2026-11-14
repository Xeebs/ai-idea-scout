# Scenario 1: Customer support agent with three distinct memory needs

## Input (what the user hands the skill)

> We're building a customer support AI agent for a B2B SaaS product. It needs to:
> 1. Remember each customer's name, company, and plan tier, indefinitely, across every future chat.
> 2. Remember the sequence of support issues a customer has had and roughly when each one happened, so it can answer "when did this problem first start" or "what changed since last time."
> 3. Occasionally summarize a long, messy dispute thread (50-plus messages) into a short recap for a human agent to read before taking over.
>
> Right now we're hand-storing everything in a single Postgres table and it's a mess — we lose track of *when* things happened versus just *what* happened. We can self-host, budget isn't the main constraint, no hard data residency requirement. Expected volume: a few thousand active customers, maybe tens of thousands of support events total.

## Pass criteria

- [ ] Normalizes all three stated needs into categories: (1) fast key-fact/preference recall, (2) temporal/event-sequenced history, (3) long-horizon narrative summarization. Does not merge them into one category.
- [ ] Recommends Mem0 for need (1), Zep (or Zep/Letta reasoned explicitly) for need (2), and Letta or Zep for need (3), each with a stated reason tied to the decision table — not a generic "any of these would work."
- [ ] Does NOT recommend a single-backend-only verdict here, since the three needs are genuinely different in kind and volume (this distinguishes it from Scenario 2's single-backend case) — explicitly reasons through single-backend sufficiency in step 3 and concludes it doesn't hold.
- [ ] Includes a Reconciliation Notes section identifying at least one plausible overlap (e.g., "plan tier" or "current status" appearing in both the fast-fact store and a narrative summary) and names one backend as authoritative for it with a reason.
- [ ] Produces a YAML config stub with at least 3 entries (one per memory need), each with memory_type, backend, ttl, scope, and authoritative fields populated (ttl indefinite/long for needs 1-2, shorter/session-scoped acceptable for the summarization draft in need 3).
- [ ] Caveats section explicitly tells the user not to treat any cited benchmark number as settled fact, and does not itself state a specific LoCoMo/DMR-style score as fact anywhere in the response.
- [ ] Does not claim to have actually connected to or tested Mem0/Zep/Letta — output reads as a design recommendation, not an integration report.

## Fail conditions

- Treating all three needs as satisfied by one backend without engaging with why that's wrong for this case.
- Fabricating a specific accuracy/benchmark percentage for any tool.
- Silently ignoring the overlap between the fact store and the summarization backend.
- Recommending Supermemory for any of these three needs without flagging its thinner-docs integration risk (it's not actually the best fit here anyway, so the correct behavior is simply not to recommend it — but if it does get mentioned at all, the risk flag must appear).
