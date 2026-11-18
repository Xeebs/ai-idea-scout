# Deterministic Agent Memory Audit — Prompt Template

Paste this whole template into any AI chat tool (ChatGPT, Claude, Gemini, etc.), fill in the bracketed sections with your own details, and send it. No installation or connected tools required.

## When to use this

Use this when:
- An agent's memory/retrieval system returned different results for the exact same query on two different runs, and you need to know why.
- A compliance, model-risk, or incident reviewer is asking "why did the agent recall this specific fact" and the honest current answer is "the embedding similarity was high enough that day."
- You're preparing for an audit (internal or regulatory) of an AI agent that relies on memory, and need to document which parts of its recall are reproducible versus probabilistic before the review happens.
- You're considering migrating some of your vector-based memory lookups to deterministic/keyed lookups and want to know exactly which parts actually need it, without ripping out everything.

This is a one-shot review of memory you already have running — it does not build, install, or operate any memory store itself.

## What to give it

Paste or describe, as completely as you can:

1. **Your current memory schema/config** — what storage and retrieval mechanism you use (e.g. mem0, Zep, Letta, a custom Pinecone/pgvector setup), the embedding model, the similarity metric and threshold or top-k setting, any re-ranking step, any LLM-based summarization/condensation applied to retrieved results, and any metadata filters in play.
2. **2-3 concrete examples of query/recall variance** — the exact query text, what got recalled on each run that produced a different result, and anything you know changed between the runs (new facts added, a reindex, a different session, a model/version bump).
3. **(Optional) The compliance or audit context** driving this — e.g. "SOC2 model-risk review," "HIPAA audit prep," "incident reproduction for a customer complaint." Only mention this if it's real — don't guess at a framework that doesn't apply to you.

## The prompt

```
You are auditing my AI agent's memory/recall system for reproducibility, ahead of a compliance or incident review. Here is my setup:

MEMORY SCHEMA/CONFIG:
[paste your config: storage backend, embedding model, similarity metric/threshold/top-k, any re-ranking step, any LLM summarization of retrieved results, any metadata filters]

QUERY/RECALL VARIANCE EXAMPLES:
[paste 2-3 examples: the query, what was recalled on run 1 vs run 2 (or more), and what you know changed between runs, if anything]

AUDIT CONTEXT (optional):
[e.g. "SOC2 model-risk review" — leave blank if none, don't assume one]

Do the following:

1. INVENTORY every distinct recall path in my setup (e.g. vector similarity search, metadata filter, recency re-ranker, LLM summarization step) — list each separately, don't collapse the pipeline into one item.

2. CLASSIFY each path as:
   - DETERMINISTIC: exact-key or fixed-rule match, same input always gives the same output regardless of corpus or model changes.
   - NON-DETERMINISTIC: any similarity/threshold/ANN-based match, or any LLM-based step (re-ranking, summarization) — even at temperature 0, since embedding neighborhoods and LLM outputs can both shift with reindexing or model updates. Don't call a path deterministic just because a threshold number is fixed.
   - CONDITIONAL: deterministic only within a stable corpus/index state — name exactly what condition breaks it.

3. CROSS-CHECK my variance examples against the inventory: which specific path(s) plausibly produced each one? If it's unclear, say so as an open question instead of guessing.

4. RANK the paths by audit risk, highest first. A path that already produced observed variance in my examples ranks above a theoretical one. A path that can drop or alter a fact's content (e.g. summarization) ranks above one that only affects ordering among true facts.

5. For each NON-DETERMINISTIC or CONDITIONAL path that is a matching/lookup mechanism, SKETCH a canonicalization key — structured fields from my own schema (e.g. entity_id + fact_type + effective_date) that could replace the embedding for that specific lookup — and explicitly state what that key would NOT catch (e.g. paraphrases, synonyms). If the risky path is instead an LLM summarization/re-ranking step, don't force a "key" fix onto it — tell me the fix appropriate to that failure mode instead (e.g. return raw structured facts and move summarization outside the audited recall path).

6. List OPEN QUESTIONS — anything in my config or examples that was too ambiguous to classify firmly.

Format your answer as:
1. Recall Path Inventory (table: Path | Mechanism | Classification | Evidence)
2. Audit Risk Ranking (numbered, highest risk first, one sentence why each)
3. Migration Sketch (one subsection per flagged path, with what the proposed fix covers and doesn't cover)
4. Open Questions

Rules: Don't assume a specific regulation applies unless I named one. Don't recommend replacing my whole memory store — only touch the paths you actually flagged as risky. Don't present any canonicalization key as implementation-ready — it's a directional sketch for me to build and test myself. If my input is too sparse to find even one concrete non-deterministic path, say so plainly instead of inventing detail.
```

## What you get back

A four-section markdown report: a table of every recall path in your system and whether it's actually reproducible; a ranked list of which paths are the real audit risk and why; a sketch (where applicable) of what a deterministic replacement key could look like and what it would give up; and a list of anything the assistant couldn't pin down from what you gave it. It is a starting point for your own engineering and audit-prep work, not a finished migration plan or a certified compliance opinion.
