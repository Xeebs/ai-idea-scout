# LightMem: An Independently Benchmarked, Embedding-Free Memory Store for Local-First Agents

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-11-context-engineering-and-memory.md · P3
- **Maturity verdict**: PARTIAL — several solo/small open-source projects (Mind, OpenDB, Mnemosyne, agent-memory-engine, contextops) already attempt SQLite+FTS5 lexical memory with self-reported benchmarks (86.67%–96.3% on their own eval sets), but no independent third-party comparison against standard vector-RAG baselines exists, and the source thread's "do agents need embeddings?" question is still genuinely open.
- **Format**: PROJECT — a persistent, queryable memory store is runtime infrastructure, not a one-shot prompt task.

## The Gap
r/ContextEngineering's "Do AI agents actually need embeddings for good long-term memory? My open-source project scored 86.67% without them" (2026-10-27) names a real, unresolved question: whether SQLite+FTS5 lexical retrieval can match vector-embedding memory for agent long-term recall. Multiple solo projects have shipped self-reported numbers on their own eval sets, but none has been checked against a shared benchmark by anyone other than its own author — exactly the kind of "real gap, no settled winner" the methodology flags as PARTIAL.

## The Project
An open-source agent memory store built on SQLite+FTS5 (no embedding model required), paired with a public, third-party-run benchmark harness that evaluates it and the existing solo projects (Mind, OpenDB, Mnemosyne) against the same standard long-term-memory eval sets (e.g. LongMemEval, BEAM) using one methodology, one held-out test set, and one judge model — settling the "do agents need embeddings" question with evidence instead of competing self-reports. The store itself ships as a drop-in library (store/query/update memory records) that runs entirely on CPU, with no GPU, no embedding API calls, and no data leaving the host machine.

Components: SQLite+FTS5 memory store with a simple record/query API; adapters for common local-agent runtimes (Open WebUI, LM Studio plugins, a generic MCP memory server); an independently-run benchmark comparing it against 2–3 existing lexical projects and a standard vector-embedding baseline on the same test set.

## Tangible Impact
**Population**: Self-hosted/local-LLM users and builders — the audience explicitly scoped into this digest run via r/LocalLLaMA — who run personal AI assistants (via Ollama, LM Studio, Open WebUI) on consumer hardware (often 8–16GB RAM, no dedicated GPU) and want persistent memory without the extra VRAM, latency, or cloud-API dependency an embedding model requires.
**Mechanism**: Today, adding long-term memory to a local assistant usually means also running or calling an embedding model, which is the exact resource/privacy cost many local-first users are trying to avoid; a validated, embedding-free memory store lets them get comparable recall quality while keeping the whole stack local, light, and offline-capable.
**Measure**: (1) Recall@k / accuracy on a standard long-term-memory benchmark (e.g. LongMemEval) within a defined margin of a vector-embedding baseline, measured by an independent third party rather than self-reported. (2) Memory footprint and per-query latency on commodity CPU hardware (no GPU) versus the same task with an embedding model loaded. (3) Adoption: number of local-agent projects (Open WebUI plugins, MCP memory servers) integrating the store within 6 months.

## Why Now
r/LocalLLaMA's continued growth and this digest's own scoping of it as a relevant community signal reflect sustained demand for fully local agent stacks; FTS5-based lexical retrieval has matured enough (several solo projects now claim competitive numbers) that an independent, rigorous comparison is newly worth running rather than purely speculative.

## MVP Sketch
A Python library wrapping SQLite+FTS5 with a record/query/update API, plus a benchmark script that runs it, two existing public lexical-memory projects, and a standard embedding-based baseline against the same held-out LongMemEval-style test set, reporting accuracy, latency, and memory footprint side by side. Experiment: if the lexical store lands within ~5 points of the embedding baseline on recall while using a fraction of the resources, the hypothesis holds; if it falls far short on multi-hop or paraphrased queries, that's the real limit to publish. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Lexical retrieval is known to struggle with paraphrase and semantic (non-keyword) recall — the benchmark may simply confirm embeddings are necessary for a meaningful class of queries, which is still a useful, honest result but kills the "embeddings aren't needed" framing.
- Several solo projects already claim strong self-reported numbers; if independent benchmarking reproduces them, the differentiator shrinks to "someone finally verified it," which is valuable but smaller in scope than a new store.
- Local-first demand is real but the total addressable population for a memory *library* (versus a full assistant product) skews toward hobbyist/builder use, not end-user-facing impact.
- Hybrid lexical+embedding approaches (e.g. Mnemosyne's sqlite-vec+FTS5) may outperform pure-lexical on both axes, making "embedding-free" the wrong framing versus "embedding-optional."
