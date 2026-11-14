# Stay Current: A Freshness-Decay Hybrid Ranker for Multi-Step Agentic Retrieval

Single-pass RAG already knows how to prefer a fresh chunk over a stale one. What nobody has shipped is what happens when an agent re-queries the same index three, five, ten times in a row on its own — and one stale result at step two quietly steers every step that follows. That's not a worse answer. That's a wrong plan built on old information, and right now there's no off-the-shelf layer that catches it.

## The Gap

An r/AI_Agents thread puts it plainly: most agent RAG failures trace back to retrieval, not generation — "chunking errors, lack of freshness signals, and reliance on pure vector search" — and the fix the thread recommends is "structural chunking, decay-based ranking, and hybrid BM25 plus vector search." That's a diagnosis and a wishlist, not a shipped system. Meanwhile, hybrid BM25+vector search with a recency nudge is genuinely mature for the single-pass case: Ragie ships a built-in "recency bias" feature, and multiple public tutorials (theneuralbase, joinstash.ai) hand out working exponential and half-life decay code. So the primitives exist. But a Weaviate forum thread shows practitioners are still losing this fight in production — "hybrid search still favors a 3-year-old chunk over yesterday's" — which means even the mature single-pass version isn't fully solved in practice, let alone extended to the harder case.

That harder case is multi-step agentic retrieval, where an agent queries the same index repeatedly within one task instead of once per request. Nothing found across GitHub, web, and paper search addresses what happens when a stale or off-target chunk at step one doesn't just produce one wrong answer — it gets fed back into the agent's own reasoning and shapes what it searches for at step two, step three, and beyond. A single bad retrieval stops being an isolated miss and starts being a compounding error. That specific angle — decay and ranking that account for the agent's own retrieval history, not just document age — is the part nobody has built.

## The Project

The plan isn't a new vector database; it's a middleware layer that sits in front of a team's existing hybrid BM25+vector index (Weaviate, Qdrant, OpenSearch/Elasticsearch, pgvector — all of which already ship mature hybrid-search APIs) and adds two things today's recency features don't do.

First, a decay function that's calibrated per domain instead of a fixed half-life guessed once and left alone. A calibration tool fits the decay rate against a labeled eval set of "this fresher chunk should outrank that staler one" judgments, so the constant actually matches how fast a given corpus goes stale — support docs decay differently than a codebase, and a codebase decays differently than a legal corpus.

Second, and the real centerpiece: loop-aware re-ranking. Each subsequent query inside one agent task gets its rankings re-weighted using what the agent has already retrieved and acted on earlier in the same chain. A stale chunk that already misled step one doesn't get to re-surface unchanged at step three — it gets actively down-weighted because the system now knows it steered the agent wrong once already. It ships as an interception layer compatible with LangGraph- and LlamaIndex-style agent loops, so a team wires it in without migrating off their existing index.

## Tangible Impact

**Population**: Engineering teams building multi-step agentic retrieval systems over frequently-updated corpora — support agents over a changing knowledge base, coding agents over a codebase with daily commits, research agents over a document set that gets amended — where a single stale chunk retrieved early in a task compounds into a wrong final action rather than one wrong answer. This is the same population the r/AI_Agents thread and Weaviate forum thread describe directly, and agentic multi-step retrieval is the fastest-growing RAG deployment shape through 2025–2026 (as distinct from single-pass Q&A RAG).

**Mechanism**: Today, teams either accept a fixed recency-bias constant (which a Weaviate practitioner confirms "helps a little and then stops helping" as queries and corpora drift) or get no freshness signal at all, and nothing accounts for a stale result compounding across an agent's own retrieval history within one task. A calibrated, loop-aware decay layer catches that compounding before it reaches the agent's final action, converting "the agent acted on week-old information three steps ago and nobody noticed" into a measurably lower stale-chunk-surfaced rate.

**Measure**: rate of stale (superseded) chunks surfacing in top-k results across a multi-step agent task, before vs. after adoption, on a corpus with known update timestamps; downstream task success/accuracy delta on tasks requiring current information; calibration accuracy of the fitted decay function against the labeled eval set versus a fixed-half-life baseline.

## Try It

There's no companion skill for this one yet — it's filed as a PROJECT-format idea, not a skill-shaped prompt task. This is runtime infrastructure meant to sit inside a live retrieval loop, so there's nothing here to paste into a chat tool today. If that changes, this section will link it.

Worth knowing going in, straight from the idea's own risk list: the general recency-bias pattern already ships in multiple vendor products, so if any of them extend their existing feature to be agent-loop-aware before this gets built, the specific gap closes fast. And the loop-aware re-ranking requires tracking per-task retrieval state — a stateful component bolted onto what's otherwise a stateless ranking function — which is its own design risk if done sloppily. The core bet also hasn't been validated on real agent traces yet, only argued from a Reddit thread and a forum complaint; whether stale-result compounding is as common in practice as it's described remains an open question.

---

Surfaced from `research/2026-11-13-rag-techniques.md`, pattern `P4`.
