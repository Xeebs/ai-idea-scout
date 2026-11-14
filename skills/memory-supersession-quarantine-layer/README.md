# Memory Supersession Quarantine Review

A self-contained prompt template for reviewing whether an append-only agent memory, rules, or notes store is vulnerable to the "stale rule still wins" failure — where an old entry marked superseded still gets read and followed by the agent because nothing actually changed its position, rank, or weight relative to its replacement. This happened in production to at least one shared-memory product builder in late 2026: they marked an old rule "superseded" without changing where it sat in assembled context, and the agent still acted on it.

This is a **design review**, not a working fix. It produces a risk assessment and a concrete policy you can hand to an engineer — it does not modify your actual system.

## When to use this

Use this when:
- You run (or are evaluating) an agent memory/rules store where old entries are marked `superseded`/`deprecated` instead of being deleted, **and**
- Either you've already hit the failure (the agent followed an old rule despite a newer one existing in the store), **or** you want to check for the risk before it bites you, before building any live enforcement.

Don't use this for: concurrent multi-writer conflicts (two sources disagreeing about what the current rule even is — that's a different problem), or for stale cached projections/views going out of date (also different).

## What to hand over

**Data source**: Connected — this is a review of your existing, already-connected memory backend (custom database, vector store, or a shared memory product). You don't need to grant live access for this review; just describe it in text, because no mature off-the-shelf connector exists yet to read these stores directly across different backends.

Provide, as plain text:

1. **Schema shape** — the field(s) that mark supersession (e.g. `status: active/superseded`, a `superseded_by` pointer), and any timestamp/ordering field in your table or store.
2. **Context-assembly logic** — how entries actually get picked and ordered when building a prompt: strictly chronological, similarity/embedding-ranked (RAG-style retrieval), top-K truncated, or some combination. A rough description of the retrieval code or query is enough if you don't have exact logic memorized.
3. **2-3 real example entries that have been superseded** — the original text, its replacement's text, and (if you know it) how the two currently render relative to each other when context gets built. Use real entries from your own store, not hypothetical ones.
4. *(Optional)* Which model(s) consume this context — useful later for testing, not needed for the review itself.

If you don't have at least one real example on hand, pull one before starting — a review without a real example is just speculation.

## What happens next (the procedure)

1. **Classify your assembly mechanism** into one of: chronological (sorted by time, no status check), relevance-ranked (embedding similarity retrieval, no status check), status-aware (already does something with the status field), or unknown.
2. **For each example you provided**, assess risk:
   - *Chronological, no reorder step*: HIGH risk by default — older (superseded) entries sort earlier than their replacement unless something explicitly moves them.
   - *Relevance-ranked, no status filter on the index*: HIGH risk — a superseded entry can score higher similarity to a query than its replacement simply because of wording drift, independent of which one is newer. If superseded entries are excluded from the main index but reachable via a separate audit query, that's MEDIUM instead.
   - *Status-aware but label-only* (the status field exists but nothing changes position): still HIGH — a label nobody repositions is exactly the failure that's already happened in the wild. Only a real structural divider with active entries always placed first earns LOW.
   - *Unknown*: flagged as UNKNOWN with a clarifying question, never guessed.
3. **A drafted quarantine policy**, specific to your setup:
   - Which field marks supersession (reusing yours if you have one).
   - Rule: active entries always render first / most prominently, regardless of timestamp or similarity score.
   - Rule: superseded entries move below an explicit, literal reference divider (e.g. `--- SUPERSEDED (audit only — do not follow) ---`) — never deleted, just demoted.
   - For similarity-ranked backends specifically: exclude superseded entries from the primary retrieval index; serve them only through a separate audit path.
   - A recommendation to pair the divider with an explicit instruction-level cue (a line telling the model entries below the divider are historical and must not be acted on) — because it's genuinely unproven whether position alone is enough, or whether the model needs to be told.
4. **2-3 concrete test scenarios**, built from your own real examples, in "old rule says X / new rule says Y / correct behavior is Y" form — ready to run through an eval once you implement the policy.
5. **An explicit reminder** that this review is a design artifact, not a verified fix. The real test is measuring the stale-rule-still-followed rate with the policy on vs. off, on your actual model.

## Output you'll get

A single report with four sections, always in this order:

1. **Risk Summary** — one line per example: mechanism, verdict (HIGH/MEDIUM/LOW/UNKNOWN), why.
2. **Recommended Quarantine Policy** — the concrete, implementable rules from step 3.
3. **Conflict Test Scenarios** — 2-3 scenarios built from your real examples.
4. **Validation Note** — a reminder that this is unverified until measured, naming the metric to track.

## Rules this review always follows

- Never produces a verdict without at least one real example entry — it will ask for one rather than invent a plausible-sounding one.
- Never claims the drafted policy is proven — reordering alone vs. needing an explicit instruction cue is flagged as an open question every time, not just once.
- Never recommends deleting superseded entries. If you ask for a deletion-based fix, it will explain why that loses your audit trail and offer quarantine instead.
- Never treats this as the same problem as concurrent multi-writer conflicts or stale cached-projection invalidation — if that's what you actually have, it will say so and point you elsewhere instead of forcing a quarantine framing onto the wrong problem.
- Never assumes it can query your store directly — everything here works from your text description of an already-connected backend.
