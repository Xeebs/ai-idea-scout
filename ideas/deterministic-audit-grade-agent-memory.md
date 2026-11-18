# Exact Recall: A Deterministic, Audit-Grade Memory Store for Regulated Agent Deployments

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-18-context-engineering-memory.md · P6
- **Maturity verdict**: PARTIAL — GitHub search found a small cluster of independent, very recent repos (`tensemem/tensemem`, `Traceless-zero/AI-MemoryHub`, `ssmurfgg04-gif/context-m`, `Retsumdk/agent-memory-compression-engine`, all created within weeks of each other) pitching deterministic/glass-box alternatives to fuzzy vector retrieval. All are single-author, near-zero stars/forks, with no evaluation or adoption signal — real, fresh independent demand, but nothing has matured past a weekend-project stage.
- **Format**: BOTH — the project is the deterministic memory store/service itself (persistent runtime infrastructure); auditing an existing memory setup for which recall paths are non-reproducible is a separable one-shot review task.
- **Data Sources**: Project mode is CONNECTED — the store becomes the system of record an agent's own tool calls write to and read from directly (via an MCP server or SDK), sitting alongside or replacing the agent's existing vector memory backend. No mature "deterministic agent memory" connector exists today (per the maturity verdict, only weekend-project-stage repos) — this is net-new infrastructure, not a wrapper on an existing mature API. Skill mode is MANUAL: the user describes or pastes their current memory schema/config and 2-3 example query/recall pairs showing where results vary run-to-run.

## The Gap
A cluster of independent developers — `tensemem/tensemem` ("deterministic memory for AI agents," Show HN, 7 stars), `Traceless-zero/AI-MemoryHub` ("glass-box alternative to RAG"), `ssmurfgg04-gif/context-m` ("Deterministic agent memory... Mem0-compatible"), and `Retsumdk/agent-memory-compression-engine` — all started building the same pitch within the last few weeks, independently of each other: that similarity-based vector retrieval is the wrong foundation when an agent's memory recall needs to be exact and reproducible, not probabilistically "close enough." None has matured past a solo weekend project, and no mature memory vendor (mem0, Letta, Zep — the crowded category this digest's P4 confirms) offers a non-fuzzy recall mode today.

## The Project
A memory store that replaces nearest-neighbor similarity search with canonicalized, keyed lookups and an explicit, auditable match rule: the same query, run twice against the same corpus state, always returns the same stored facts, and every match decision is logged with the specific rule that produced it (exact key match, or a stated rule-based fuzzy match — never "cosine similarity happened to be high enough"). It ships Mem0-compatible on the write/read API surface (following `context-m`'s own positioning) so it's a drop-in alternative rather than requiring agents to re-integrate from scratch, and as an MCP server so any agent framework can call it directly.

Components: a canonicalization/slot-extraction layer (turns raw facts into structured keys instead of embeddings); a deterministic match engine (exact + explicit rule-based fuzzy matching, no ANN in the critical path); an audit/explain log (what matched, and the exact rule that matched it); a Mem0-compatible API shim; an MCP server wrapper.

## Tangible Impact
**Population**: Engineering teams building memory-augmented agents for regulated or otherwise auditable use cases — financial-services copilots subject to model-risk-management documentation expectations, healthcare agents subject to HIPAA-style audit-trail requirements, and legal/compliance assistants where "why did the agent retrieve this specific fact" must be answerable on demand. This is the same population already adopting the mature vector-memory stores this digest's P4 confirms are a crowded category, who hit a wall the moment an auditor or incident reviewer asks why a fact surfaced and the honest answer is "the embedding was close enough that day."
**Mechanism**: Today, every mature memory framework uses similarity-based retrieval, so the same query run twice against a drifted or reindexed corpus can return a different memory set — making "replay this decision exactly" impossible and leaving compliance reviews dependent on re-running a probabilistic pipeline and hoping it reproduces. A deterministic store guarantees the same query always surfaces the same facts, via a rule a reviewer can actually point to, turning memory recall from a probabilistic step into a reproducible, explainable one.
**Measure**: (1) Recall-reproducibility rate — percentage of repeated identical queries, run after a corpus update/reindex, returning byte-identical memory sets, measured against a vector-store baseline. (2) Audit/incident-review time — how long it takes a reviewer to answer "why did the agent recall X," deterministic-rule lookup vs. re-running embeddings and hoping to reproduce. (3) Task-accuracy parity on a standard retrieval benchmark, confirming determinism isn't bought at the cost of recall quality.

## Why Now
Four independent developers started building toward exactly this within the last 30 days, with zero prior entrenched competitor and real, fresh demand validation — but also a closing window before one of them matures first, or a major vendor (mem0, Zep) adds a "deterministic mode" of its own now that the gap is visible across multiple independent Show HN-style launches at once.

## Skill Angle
Given a description or pasted config of an existing memory schema, plus 2-3 example query/recall pairs that have varied run-to-run, review it for which specific recall paths are fuzzy/non-reproducible and would need migrating to a deterministic keyed lookup — and sketch what the canonicalization key would look like for that data. A one-shot audit-readiness review, independent of building the always-on store.

## MVP Sketch
Build a minimal keyed memory store: canonicalize incoming facts/queries into normalized structured keys; support exact match plus one explicit rule-based fuzzy match (e.g. edit-distance threshold on canonicalized keys, never embedding cosine similarity); log every match decision with its rule. Wire it as an MCP server a coding or support agent can call for write/read. Validate with (a) 50 repeated-query reproducibility tests across a simulated reindex event, and (b) a small retrieval-quality benchmark comparing accuracy against a vector-store baseline. 3-4 weeks, 1-2 people.

## Risks & Open Questions
- Deterministic/keyed matching may not generalize to genuinely fuzzy recall needs (paraphrased queries, synonyms) where vector similarity's flexibility is the right tool — real risk of trading usefulness for auditability.
- The regulated-industry audit need is inferred from the determinism pitch, not yet validated by a direct complaint from a compliance team in this cycle's evidence — the MVP should include outreach to at least one real compliance-adjacent user before over-investing.
- A major memory vendor could add a "deterministic mode" feature rather than ceding the space to a new entrant.
- The four early repos are all within roughly five weeks old; worth checking their trajectory (do any gain real users/stars fast) before investing deeply in a competing build rather than contributing to one of them.
