# Memory Wall: A Pre-Retrieval Sanitizer for Prompt Injection Arriving Through Agent Memory and RAG Content

- **Status**: EXPLORING (promoted 2026-11-13 cycle 39: evidence density — 5+ independent early-stage packages plus 3 academic papers all attacking the same memory/retrieval-boundary injection gap)
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-guardrails-in-production.md · P8
- **Maturity verdict**: PARTIAL — WebSearch found several small, early-stage open-source packages targeting exactly this boundary (`rag-poison-guard`, `rag-sanitizer` v0.1.0, `RAGWall`'s regex-only OSS tier, `LightShield` v0.1.0, `enclawed`) plus active academic research (AM-Sentry, MemPoison, MEMSAD) on retrieval-stage memory-poisoning defense. All are narrow, single-maintainer, or v0.1.0-stage rather than mature or widely adopted, so the gap for a serious, evaluated build remains real.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the agent's existing memory store or vector database (e.g., Chroma, pgvector, or Mem0) intercepted via middleware at the retrieval call, before content reaches prompt assembly. These backends have mature client libraries today, but no single cross-backend connector exists yet, so the project ships adapters per backend as part of the build.

## The Gap
GitHub issue `Sumit-ai-dev/Adaptive-Agent-Memory-OJT-G146#39` (resolved in PR #43) built a prompt-injection sanitizer encapsulating bilateral memory injections within strict delimiter tags (`<experiential_strategy>`, `<prohibited...>`) specifically for the memory/retrieval boundary. Nearly every other guardrail item in this run's evidence (Spring AI Privacy Guardrails, CanaryGuard, OpenPrep-AI's rate limiter) targets the live user-input boundary; this is the only item addressing memory/retrieval specifically, and it's a single student/OJT-labeled project-level fix rather than a named, reusable library.

## The Project
A middleware layer sitting between an agent's memory/vector store and its prompt-assembly step: every chunk of retrieved memory or RAG content is encapsulated in strict, model-enforced delimiter tags before entering the prompt, scanned for instruction-shaped content (imperative phrasing addressed to "the assistant," known delimiter-escape patterns, nested-injection attempts trying to break out of the tag), with flagged content either stripped, tagged for human review, or passed through with a reduced-trust annotation the system prompt instructs the model to treat accordingly. Ships as adapters for a few common vector-store/memory backends (Chroma, pgvector, Mem0) rather than a bespoke per-project integration, consolidating a pattern five early-stage packages are each independently reinventing at v0.1.0.

## Tangible Impact
**Population**: teams running agents with persistent memory or RAG retrieval where the stored or retrieved content itself may not be fully trusted — agents that write their own memory from prior interactions (making memory a write-once, read-many attack surface for a poisoned earlier turn), and RAG agents retrieving from any corpus that includes third-party or user-contributed content. This is distinct from this index's existing `rag-knowledge-base-poisoning-scanner` idea, which targets documents at ingestion time, rather than an injected instruction surviving inside already-indexed or already-stored content as it's pulled into context on a given turn.
**Mechanism**: closes a boundary every other guardrail in this run's evidence misses — a live user-input filter does nothing to catch an injection planted in memory three turns ago, or buried inside a retrieved chunk that passed ingestion-time scanning but still carries an instruction-shaped payload. Strict delimiter encapsulation plus a scan at the retrieval boundary stops that payload from being read by the model as an instruction regardless of how it entered memory or the index in the first place.
**Measure**: bypass rate on a labeled test set of memory/RAG-delivered injection payloads (adapting known delimiter-escape and nested-injection techniques), before/after the sanitizer; false-positive rate on legitimate memory/RAG content that happens to contain imperative or instructional language; latency overhead added per retrieval call (must stay low enough not to undermine agentic-loop responsiveness).

## Why Now
Agent memory and RAG retrieval are now common enough in production that this attack surface is actively being probed — five independent early-stage packages plus three arXiv papers surfaced in this run's search alone — but every attempt remains v0.1.0/research-stage: there's a validated technique (delimiter encapsulation) and real demand, just no maintained, multi-backend implementation yet.

## Skill Angle
A "Memory Injection Audit" skill — given a sample export of an agent's stored memory entries or a batch of RAG corpus chunks (pasted or uploaded), the skill scans for instruction-shaped content and delimiter-escape patterns and reports a risk-ranked list of entries that look like a planted or surviving injection payload, as a one-time retroactive check before committing to the full middleware integration.

## MVP Sketch
2-4 weeks, 1-2 people. Implement the delimiter-encapsulation wrapper and a regex/heuristic scan pass first (fast, catches the known pattern class demonstrated in the evidenced OJT project), add one vector-store adapter (Chroma, the most common lightweight choice), assemble a labeled test set combining the evidenced delimiter-tag technique with known nested-injection/escape patterns from the academic papers (AM-Sentry, MemPoison), and validate bypass rate and false-positive rate before adding further backend adapters.

## Risks & Open Questions
- Overlaps conceptually with pre-ingestion scanning (this index's existing `rag-knowledge-base-poisoning-scanner`) but targets a genuinely different layer (retrieval-time, content already in the store) — needs clear positioning so the two aren't perceived as redundant.
- A sufficiently clever injection could still escape strict delimiters if the underlying model is itself vulnerable to delimiter-confusion attacks, a model-level weakness middleware alone doesn't fully close.
- All five comparable early-stage packages are v0.1.0 — a real risk is that one (most likely RAGWall, which has an OSS tier) matures into the de facto standard before this ships; worth re-checking adoption before committing.
- Thin single-project evidence (one OJT-labeled student project) for the core technique — validating that production teams beyond academic/early-stage packages actually want this is the key open question.
