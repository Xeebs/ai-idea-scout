# GraphRAG Freshness & Routing Audit

A paste-into-any-AI-chat prompt that screens a hybrid vector+graph GraphRAG deployment (any Neo4j/Memgraph-style graph store paired with any Qdrant/pgvector/Pinecone/Weaviate-style vector store) using a sample of real query logs and a description of your setup. It tells you whether your actual query mix and document-vs-graph update cadence justify building a dedicated query router and freshness auditor — before you spend engineering time building either.

This is a one-shot screening report, not a connector to your live stores and not a working router or auditor. It does not measure actual staleness lag or run any classifier against production traffic — it works entirely from what you paste in.

## When to use this

Use it when:
- You're hand-rolling ad hoc rules for whether a query should hit your vector index, your graph, or both, and want to know whether your real traffic mix even justifies formalizing that into a trained router.
- You've had an incident — a multi-hop question got a wrong answer — and you suspect either the graph was stale relative to your source documents, or the query got routed to the wrong backend.
- You're deciding whether to invest in building a freshness-auditor-plus-router sidecar and want a cheap, data-grounded read on your current situation first, instead of guessing.

Do not use this if you want help designing the router's classifier, building the freshness auditor's live comparison logic, or debugging a specific graph query — those are separate, larger implementation tasks this audit deliberately doesn't attempt.

## What you need to provide

This is manual input — there is no connector to your live graph database or vector database reading this for you. (If you're building the full sidecar described alongside this skill, that version does connect directly to your stores' client libraries; this audit is the lighter, pre-commitment step that works from what you paste.) Paste or describe the following:

1. **Setup description**: which graph store and vector store you're running, rough corpus size, how often your *source documents* change (daily edits, weekly batch, continuous stream), and how often your *graph* gets rebuilt or incrementally updated (nightly cron, manual rebuild last run some weeks ago, no fixed schedule — be specific).
2. **A sample of real recent queries** — at least 15, ideally 30-50+, as the actual question text your users asked (not categories or paraphrases). Redact anything sensitive first.
3. Optional: any known incidents where an answer was wrong and you suspect staleness or bad routing.
4. Optional: your current routing heuristic, if you have one, in your own words.
5. Optional: which topics or documents changed most recently, if you know — this lets the audit flag sampled queries that touch likely-stale territory.

If your query sample has fewer than 15 items, say so — the audit still runs, but caps its recommendation at a lower-confidence tier rather than giving you the strongest call.

## The procedure (what the AI should do with your inputs)

Paste this whole README plus your setup description and query sample into any AI chat tool and ask it to run the audit. Here is exactly what it should do:

1. **Classify each query** as `direct-lookup` (answerable from one document or entity, e.g. "what is X's return policy") or `multi-hop` (requires traversing a relationship or combining facts across entities, e.g. "which other customers who bought X also had issue Y"). Mark genuinely unclear ones `ambiguous` rather than forcing a label.
2. **Tally the mix**: what percentage of your sample is direct-lookup vs. multi-hop vs. ambiguous. A corpus where most traffic is direct-lookup doesn't need a graph router invested in yet, no matter how good the graph is.
3. **Assess a freshness-risk tier** from your two stated cadences:
   - **HIGH** — source documents change faster than or about as fast as the graph is rebuilt (e.g. docs updated weekly, graph rebuilt monthly or on no fixed schedule).
   - **MEDIUM** — the graph rebuilds faster than documents change, but there's still a real lag window of days where staleness is possible.
   - **LOW** — the graph rebuilds near-continuously or clearly faster than documents change, or the corpus is close to static.
   The AI should always cite the specific cadence numbers that drove the tier, never assign one without them.
4. **Cross-reference multi-hop queries against recently changed topics**, if you gave that info — flagging any multi-hop query that plausibly touches recently changed material as "elevated staleness risk," clearly labeled as a sampling flag, not a confirmed wrong answer.
5. **Give a build recommendation** using only the two measured factors — multi-hop share and freshness-risk tier:
   - Multi-hop share ≥25% AND freshness-risk HIGH or MEDIUM → **Build now** (both router and freshness auditor are justified).
   - Multi-hop share ≥25% but freshness-risk LOW → **Build router only**.
   - Multi-hop share <25% but freshness-risk HIGH or MEDIUM → **Build freshness auditor only, defer the router**.
   - Multi-hop share <25% AND freshness-risk LOW → **Not yet** — monitor and re-run this audit later.
   - If your sample was under 15 queries, the call is capped at "Build router only" or "Not yet" at most, with that caveat stated plainly — never "Build now" off a small sample.
6. **Write the report** in the format below.

## Output format

The AI should return a single report with these sections, in order:

1. **Setup Recap** — your stated graph/vector store, corpus size, both cadences, and the sample size (flagged if under 15).
2. **Query Classification** — a table of each query, its classification, and a one-line reason (or a representative subset with a stated total count if your sample is large).
3. **Routing Mix** — percentage direct-lookup, multi-hop, and ambiguous.
4. **Freshness Risk Assessment** — the tier (LOW/MEDIUM/HIGH) with the specific cadence numbers cited, plus any "elevated staleness risk" flags from step 4.
5. **Recommendation** — one of the four labels from step 5, with 1-3 sentences tying it directly to your measured multi-hop share and freshness tier, including the sample-size caveat if it applies.
6. **Open Questions** — anything you didn't provide that would sharpen the audit (no rebuild cadence, no recent-change list, sample under 15, etc.).

## Guardrails — what this should never do

- Never invent query content, cadence numbers, or store names you didn't provide — it should list missing pieces under Open Questions, not assume a typical setup.
- Never report a staleness lag as a measured fact — this works from stated cadences and sampled queries only. An actual measured lag requires reading live timestamps from your graph and document stores, which this skill doesn't do.
- Never classify a query without pointing to something visible in the query's own text — it shouldn't lean on assumed knowledge of what your corpus "probably" contains.
- Never recommend "Build now" off a sample under 15 queries — it should cap the call and say the sample is too small for the strongest recommendation.
- This is a screening report only. It will not design your router's classifier, specify your freshness auditor's implementation, or touch any live system. If you actually want that built, say so explicitly — that's a separate, much larger task.
- An "elevated staleness risk" flag on one query is a signal to go check, not a confirmed wrong answer — it shouldn't be reported as a verdict.

## Example opening message to the AI

> Run a GraphRAG Freshness & Routing Audit using the procedure in this README. Our setup: Neo4j for the graph, pgvector for the vector index, about 40,000 internal support/engineering wiki pages. Wiki pages get edited continuously by engineers (dozens of edits a day), but the graph is rebuilt via a manual script whenever someone remembers — last rebuild was about 7 weeks ago. Here are 22 real queries from last week's support-bot logs: "What's the rollback procedure for the payments service?", "Which teams were affected by the auth outage in March and what was the root cause chain?", "What is ticket INC-88213 about?", "How did the on-call escalation policy change after the Q2 incident, and does it apply to the current on-call rotation?" [...18 more]. We've had one incident where a multi-hop question about an escalation policy gave an answer referencing a policy that had since been superseded.
