---
name: deterministic-audit-grade-agent-memory
description: Audits an existing agent memory/recall setup to find which specific recall paths are non-reproducible (fuzzy vector similarity, approximate nearest-neighbor, LLM re-ranking/summarization) versus truly deterministic, and sketches a canonicalized key schema to migrate the risky paths to exact lookups. Use when a compliance, incident, or audit review needs to know why an agent recalled a given fact, or when identical queries have returned different memory results run-to-run.
---

# Deterministic Agent Memory Audit

## When to use this
Reach for this skill when someone says something like: "our agent gave a different answer when we re-ran the exact same query against its memory," "an auditor/compliance reviewer is asking why the agent recalled this specific fact and we can't give a precise answer," "we need to document which parts of our memory retrieval are reproducible before a model-risk or incident review," or "we're thinking about moving off vector similarity for some of our memory lookups but don't know which parts actually need it." This is a one-shot review of an *existing* memory setup — it does not build or operate a memory store.

## Inputs
**Data source**: Manual — the user pastes or describes (1) their current memory schema/config: what storage and retrieval mechanism is in use (e.g. mem0, Zep, Letta, a custom pgvector/Pinecone setup), the embedding model, similarity metric and threshold/top-k, any re-ranking or summarization steps, and any metadata filters; and (2) 2-3 concrete example query/recall pairs where results varied run-to-run (the query, what was recalled on each run, and — if known — what changed between runs, e.g. a reindex, new facts added, a different session). Optionally, the compliance/audit context driving the request (e.g. "SOC2 model-risk review," "HIPAA audit prep") — only use a named framework if the user actually states one.

## Procedure
1. **Inventory every distinct recall path** described in the schema. A "path" is any mechanism that decides what gets returned for a query — e.g. vector similarity search, a keyword/metadata filter, a recency-decay re-ranker, an LLM-based summarization or condensation step applied to retrieved results. List each one separately; do not collapse a multi-step pipeline into one entry.
2. **Classify each path's determinism**:
   - **DETERMINISTIC** — exact-key or fixed-rule match: same input always produces the same output regardless of corpus drift, reindexing, or model version (e.g. exact string match on a normalized key, a fixed tie-break rule on explicit timestamps).
   - **NON-DETERMINISTIC** — any similarity/threshold-based match (cosine similarity, ANN/approximate nearest-neighbor, embedding distance), and any LLM-based step in the recall path (re-ranking, summarization, condensation) even at temperature 0 — LLM calls and embedding-space neighbors can both shift with model/index updates, so never classify these as deterministic just because a threshold number looks fixed.
   - **CONDITIONAL** — deterministic only within a stable corpus state (e.g. exact match that nonetheless silently depends on an unversioned embedding re-index somewhere upstream); name the specific condition that breaks it.
3. **Cross-check against the supplied query/recall examples.** For each variance example, identify which inventoried path(s) plausibly produced it. If the evidence given doesn't clearly implicate a specific path, say so explicitly as an open question rather than asserting a cause.
4. **Rank paths by audit risk**, highest first: a path that already produced an observed variance in the user's examples ranks above a merely theoretical risk. A content-dropping step (e.g. summarization that can omit a fact) ranks above a pure-ranking step (e.g. which of several true facts surfaces first), because the former can make an audit answer wrong, not just imprecise.
5. **For each NON-DETERMINISTIC or CONDITIONAL path, sketch a migration option** — but only if the path is a matching/lookup mechanism:
   - Propose a canonicalization key built from structured fields visible in the user's schema/examples (e.g. `entity_id + fact_type + effective_date`), not embeddings.
   - Name explicitly what the key loses — e.g. paraphrase tolerance, synonym matching — as a stated tradeoff, never hidden.
   - If the non-deterministic path is a re-ranking/summarization step rather than a lookup, do not force a "canonicalization key" fix onto it — recommend the actual fix for that failure mode instead (e.g. return raw structured facts from the critical recall path and move summarization downstream, outside the audited path).
6. **List open questions** — any part of the schema or examples that was ambiguous or missing and blocked a firm classification.

## Output format
A markdown report with exactly these sections, in order:
1. **Recall Path Inventory** — table: `Path | Mechanism | Classification | Evidence/reasoning`.
2. **Audit Risk Ranking** — numbered list, highest risk first, each entry one sentence on why it would fail an audit question (e.g. "Vector similarity search — ranks #1: this is the exact path that produced different results on identical queries in the supplied example after corpus reindex").
3. **Migration Sketch** — one subsection per non-deterministic/conditional path that got a proposal in step 5, each with: proposed key fields, what it covers, and what it explicitly does not cover.
4. **Open Questions** — bullet list; empty/omitted only if genuinely nothing was ambiguous.

## Guardrails
- Never classify a similarity-threshold or ANN-based match as deterministic just because the threshold value itself is fixed — the set of neighbors it matches against can still change with reindexing, corpus growth, or embedding-model updates.
- Never assert a specific regulation (HIPAA, SOC2, GDPR, etc.) applies unless the user actually named it; default to generic reproducibility/explainability framing.
- Never recommend wholesale replacement of the entire memory store with keyed lookups — scope the migration sketch only to the paths actually implicated as non-deterministic or audit-risky; fuzzy recall may be the right tool for paths the user didn't flag as a problem.
- Never present a canonicalization key sketch as implementation-ready or tested — it is a directional starting point for the user's own engineering work, and must say so.
- Never force a "keying" fix onto a non-lookup failure mode (e.g. an LLM summarization step that drops facts) — name the actual mechanism causing the variance and the fix appropriate to it instead.
- If the schema/config or examples given are too sparse to identify even one concrete non-deterministic path, say that plainly in Open Questions rather than inventing detail to fill out the report format.
