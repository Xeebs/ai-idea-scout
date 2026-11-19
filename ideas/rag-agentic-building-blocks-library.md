# Five Blocks: A Composable Library of Swappable Agentic-RAG Primitives

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: RAG techniques
- **Source**: research/2026-11-19-rag-techniques.md · P6
- **Maturity verdict**: PARTIAL — each individual block exists somewhere (JADE's query rewriter + serial decomposition module, arXiv 2601.21916; multiple blog-documented routing and self-check/reflection patterns; a dozen small GitHub repos — DualStack-Agent, Corax-RAG-Agent, artoo, Crux, RAGents, py-jrag — each implementing some subset), but no single maintained library offers all five as swappable, composable primitives. A futureagi.com guide states production systems "typically use three or four of its five patterns," corroborating the gap.
- **Format**: BOTH
- **Data Sources**: CONNECTED — integrates with the host application's existing retriever backend (vector DB client: Qdrant/pgvector/Pinecone/Weaviate) and tool-calling layer (the model provider's native function-calling API, or the framework's tool abstraction in LangChain/LlamaIndex) — all mature, already-deployed connectors. The library supplies the swappable reasoning-pattern logic on top; it does not require building any new external connector.

## The Gap
A latenode community forum thread asks, in explicitly complaint-shaped terms, "Has anyone actually made this work — can autonomous AI agents actually coordinate a RAG pipeline end-to-end," questioning whether multi-agent orchestration improves results or just relocates complexity. A futureagi.com guide frames query rewriting/decomposition, multi-hop retrieval, tool routing, and self-check/self-correction as the five patterns that ship in real production agentic-RAG systems — but notes a real system "typically uses three or four," implying teams skip patterns not because they're not useful but because each one is still bespoke, one-off engineering to add. `gh search repos "agentic RAG framework"` found a dozen small projects, each implementing a different narrow subset, none offering all five as one swappable set.

## The Project
A small library that packages the five named agentic-RAG patterns — query rewrite, query decomposition, multi-hop retrieval, tool routing, and self-check/self-correction — as independently swappable, composable steps in a pipeline, rather than a monolithic framework a team has to adopt wholesale. Each pattern ships as a drop-in step with a defined input/output contract so a team composes just the subset their task needs (e.g., decomposition + multi-hop for a research-assistant use case, routing + self-check for a support-bot use case) and can add or remove a pattern later without rewriting the pipeline around it.

The composability is the centerpiece: each individual pattern is already a solved, documented technique, so the project's actual contribution is the shared interface and adapter layer that lets a team mix any subset of the five without hand-building the glue — directly answering the forum's "has anyone made this work end-to-end" question with a tested library instead of a bespoke build per team.

## Tangible Impact
**Population**: small-to-mid engineering teams (roughly 2–20 engineers) building agentic RAG systems who currently hand-roll each pattern they adopt from scratch per project — the practitioner profile implied by the latenode forum question and the dozen narrow GitHub repos found in gap analysis, each a different team's partial, bespoke reimplementation.
**Mechanism**: lets a team adopt exactly the subset of the five patterns their task needs as tested, swappable primitives instead of re-implementing bespoke versions of each — directly targeting the documented pattern of production systems using only 3–4 of 5 patterns, by making the cost of adding the skipped one(s) a config change instead of a multi-week build.
**Measure**: number of the five patterns a team runs in production before vs. after adoption (target: closer to 5/5 instead of the documented 3–4/5 baseline); time to add a new pattern to an existing pipeline (target: hours via a swap-in step, versus the days-to-weeks of bespoke implementation the evidence implies); task success rate on multi-hop/complex queries before vs. after turning on a previously-skipped pattern.

## Why Now
Each of the five patterns now has mature, independently documented reference implementations (JADE's rewriter/decomposition module, multiple blog-level routing and self-check write-ups) — the individual techniques are de-risked and proven. What's missing is someone assembling them behind one swappable interface instead of requiring a team to find, adapt, and glue together five separate one-off implementations, which is now a tractable integration problem rather than a research problem.

## Skill Angle
An "Agentic RAG Pattern Fit" skill: given a description of a team's RAG use case, query types, and current pipeline, recommends which of the five patterns are actually worth adopting and in what order — a one-shot design/triage aid distinct from the runtime library itself, useful for a team deciding whether the composability investment is worth it before wiring anything up.

## MVP Sketch
2–4 weeks, 1–2 people. Scope: implement three of the five patterns first (query rewrite, multi-hop retrieval, self-check) as pluggable steps behind one shared interface, with adapters for raw function-calling and one framework (LlamaIndex). Validating experiment: build a sample pipeline composing two of the three implemented patterns, measure task success rate on a multi-hop eval set versus a single-shot retrieval baseline, and confirm swapping a pattern in or out takes minutes, not a pipeline rewrite.

## Risks & Open Questions
- Scope creep toward "another agent orchestration framework" is the same risk the digest's own evidence flags for adjacent RAG control-loop projects — this must stay a library of composable steps, not a competing orchestration layer, to avoid colliding with LangGraph/LlamaIndex rather than complementing them.
- The five patterns differ enough in interface shape (a router's signature looks nothing like a self-check step's) that designing a genuinely uniform swappable contract may be harder than the MVP assumes — worth prototyping the interface itself before committing to all five.
- If LlamaIndex or LangChain ship an equivalent "five-pattern module pack" first, this project's differentiator narrows to a thin, less-integrated wrapper.
- The underlying evidence is one forum thread plus a secondary guide, not a dense multi-source signal — worth a quick practitioner validation check before a full build.
