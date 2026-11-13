# Scenario 2 — Small customer-support KB team, missing input then thin sample, build is NOT justified

## Setup
A 3-person support-tooling team built a customer-support knowledge-base bot on always-RAG. A PM asks them to "add a long-context fallback and route between the two" after reading about it online. The team pastes what they have, but — realistically — forgets the pricing on the first attempt, and even once that's supplied, their log sample is small and heavily skewed toward one query type.

## Inputs provided to the skill (in two turns, as a real user would)

**Turn 1 (incomplete):**
- Query log sample (18 queries from the last week, unlabeled): mostly things like "how do I reset my password," "where's my refund," "how do I cancel my subscription" — 16 of the 18 are short single-fact lookups against one help-center article; 2 are "can you summarize my last 3 support tickets" (needs a few documents, not the whole KB).
- Corpus token distribution: p50 800 tokens, p90 6,000 tokens, p99 15,000 tokens (the whole KB is small — a few hundred short articles).
- (Pricing is NOT included in this turn.)

**Turn 2 (after the skill asks for it):**
- Pricing: input $1 per million tokens, output $5 per million tokens, no separate retrieval cost (already amortized/negligible).

## Expected output (pass/fail criteria)

PASS requires that:
1. On Turn 1, the skill does NOT compute anything — it explicitly stops and asks for the missing pricing input, per the guardrail against guessing numbers. It should not silently assume a "typical" price.
2. On Turn 2, once pricing is supplied, it proceeds and infers complexity buckets for the unlabeled queries (correctly flagging them as inferred, not given), landing on roughly 16 single-fact / 2 narrow-multi-doc, with no full-corpus-summarization bucket needed since the corpus is tiny.
3. The cost comparison shows both paths are already cheap in absolute terms (sub-cent per query on either path) given the small corpus — always-long-context here is not 26x more expensive, because this corpus's p99 is only 15,000 tokens, much smaller than the digest's cited benchmark corpus. The output must derive this from the supplied numbers, not assume the idea's generic "26x" figure applies.
4. The build-or-skip recommendation says building a full router is NOT justified — correctly citing at least one of: the sample is below the ~30-query guardrail (18 < 30), the query mix is heavily skewed to one bucket (16/18 single-fact), and/or the absolute cost savings available are too small in dollar terms to justify the engineering effort.
5. It still states what a simple static rule would look like as a cheaper alternative to a full router (e.g., "default to RAG; only use long-context for the rare multi-ticket summary request"), rather than leaving the team with no actionable answer.
6. Accuracy caveat is present and correctly labeled as a literature estimate, since no eval data was given.

FAIL if: it computes a cost estimate before pricing is supplied in Turn 1, it recommends building a full always-on router despite the thin/skewed sample, or it reuses the idea's "26x"/"128K" figures as if they apply to this much smaller corpus instead of deriving numbers from what was actually given.
