# Steady Memory: A Hardened, Packaged Persistent-Memory Layer for Local Small-Model Agents

- **Status**: EXPLORING (promoted 2026-11-14 cycle 78: evidence density — ≥2 independent threads within the digest, a Mem0+Ollama+Qdrant guide, an LM Studio community plugin, and a dev.to "why do local AI agents forget you" post, plus a dozen+ separate 0–1-star solo GitHub repos independently re-deriving the same fragile stack)
- **Date**: 2026-11-14
- **Topic**: Small & local models
- **Source**: research/2026-11-14-small-and-local-models.md · P4
- **Maturity verdict**: PARTIAL — GitHub search for "local agent persistent memory" / "mem0 ollama" / "sqlite-vec agent memory" returned a dozen+ repos (ollama-mem0-AI-chatloop-ts, self-learning-agent, mem0-broker, mem0-personal-ai-agent, ai-memory-assistant, mem0-persistent-ai-memory, etc.), but every one has 0–1 stars and is a solo DIY integration, confirming many hands have built this, none robustly — no packaged, widely-adopted solution found.
- **Format**: BOTH — a persistent, managed memory store is runtime infrastructure; auditing an existing DIY integration against known failure modes is a separable one-shot review task.
- **Data Sources**: CONNECTED — the project connects directly to the user's own local model runtime (Ollama/LM Studio) and manages its own local storage (SQLite/sqlite-vec/Qdrant or flat files on the user's disk) — not a third-party API, since the entire point is that nothing ever leaves the machine. No existing packaged tool does this robustly today (confirmed by the dozen 0–1-star repos above), so it would be built as part of this idea.

## The Gap
WebSearch surfaced a Mem0 + Ollama + Qdrant integration guide where the author explicitly notes it is "not the official @mem0/openclaw-mem0 plugin" and warns that "the embedding dimensions in config must match the embedding model, or writes silently fail"; an LM Studio community memory plugin stores memory as a plain markdown file, with the author noting reliability "depends on the model's tool-use ability, and larger models are more reliable." A LocalLLaMA-sourced finding that full-history context stuffing "actively harmed recall at every tested model size" suggests the community hasn't even converged on the right architecture, let alone a robust implementation of any one approach.

## The Project
A packaged, validated memory layer purpose-built for local small-model agents (Ollama, llama.cpp, LM Studio). It wraps storage/retrieval behind a simple record/query API, but — unlike the dozen solo DIY attempts — ships with built-in health checks that the community's own write-ups identify as missing: embedding-dimension-mismatch detection before a write is accepted, write-confirmation (never a silent failure), and a degraded-mode fallback to flat-file storage when the local model's own tool-calling reliability is too weak to trust structured memory calls (common at smaller model sizes, per the digest's own evidence).

## Tangible Impact
**Population**: Hobbyist and privacy-conscious individuals running personal AI assistants on local hardware via Ollama or LM Studio who want the assistant to remember context (journaling, personal projects, health or financial notes) across sessions without a cloud memory service touching that data. Ollama alone reported roughly 8.9 million monthly active developers as of July 2026 (TechCrunch), a substantial share of whom are individual/hobbyist builders rather than enterprise teams — exactly the audience building and re-building the fragile DIY memory stacks this digest documents.
**Mechanism**: Today these builders hand-wire Mem0/Qdrant/sqlite-vec integrations with documented fragility — silent write failures on dimension mismatch, reliability that degrades with model size — and every public attempt stops at a 0–1-star solo repo, meaning the next builder starts from zero again. A packaged layer with built-in failure detection and a degraded-mode fallback removes the silent-failure class entirely and gives these builders a working default instead of a DIY integration they must personally debug from scratch.
**Measure**: (1) Silent-write-failure rate on a fault-injection test harness (intentionally mismatched embedding configs, dropped writes, degraded tool-calling) versus the documented failure rate of the DIY stacks cited above. (2) Recall accuracy retained across a multi-session benchmark at varying local model sizes (1B/3B/7B/13B), showing the layer compensates for weaker tool-use reliability at small sizes. (3) Adoption — number of community integrations (Open WebUI plugins, LM Studio plugin ecosystem) within 6 months of release.

## Why Now
This digest's own evidence shows a dozen+ independent solo attempts within the current GitHub landscape, all hitting the identical fragility wall — strong, fresh validated demand with zero converged winner, which is the exact PARTIAL sweet spot: feasibility is de-risked by many prior attempts, but no one has executed the robustness layer well yet.

## Skill Angle
Given a pasted description or config dump of an existing DIY memory integration (e.g. Mem0+Ollama+Qdrant settings, or an LM Studio memory plugin's config), Claude audits it against the known failure modes documented in this digest — embedding dimension mismatch, no write confirmation, reliability assumptions tied to the local model's tool-calling consistency — and returns a concrete fix checklist. This is a review task separable from running the hardened memory service itself.

## MVP Sketch
2–4 weeks, 1–2 people: a Python library wrapping SQLite/sqlite-vec (optionally Qdrant) with a record/query/update API; a pre-write validation step that checks embedding dimensions against the configured embedding model and refuses a silent partial write; a degraded-mode flat-file fallback path triggered when a configurable number of structured-call failures occur in a session. Experiment: run the same multi-turn memory-recall benchmark across three model sizes (e.g. a 1B, a 7B, and a 13B Ollama model) with and without the hardening layer, measuring whether recall and write-success rate stay stable at the smaller sizes where the digest's evidence says reliability degrades.

## Risks & Open Questions
- The dozen existing 0–1-star attempts suggest either weak demand for a *packaged* solution specifically (vs. developers happy to DIY) or just weak execution so far — this MVP's adoption number is the test of which is true.
- A degraded-mode fallback adds complexity that could itself introduce new failure modes if not carefully bounded.
- The right memory *architecture* (the LocalLLaMA full-history-harms-recall finding) is still an open question this project doesn't resolve — it hardens whatever architecture is chosen, it doesn't pick the right one.
- Mem0, LM Studio, or Ollama itself could ship an official hardened plugin, which several of the cited DIY authors are explicitly working around the absence of today.
