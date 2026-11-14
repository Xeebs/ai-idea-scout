---
name: agent-memory-tool-interop-adapter
description: Recommends which agent-memory backend(s) (Mem0, Letta, Zep, Cognee, Supermemory) to use for each distinct memory need an AI agent has, flags conflicts between backends, and outputs a ready-to-use declarative routing config. Use when someone is choosing or combining memory tools for an AI agent and describes more than one kind of thing it needs to remember.
---

# Memory Stack Advisor

## When to use this
A user is building or operating an AI agent and says something like "which memory tool should I use," "I need my agent to remember both X and Y and I don't know if one tool does both," "I'm hand-wiring two memory SDKs together and it's a mess," or "my agent forgot something it should have remembered three sessions ago." The trigger is the moment *before* they commit to a memory architecture — this is a design/decision aid, not a running system.

## Inputs
**Data source**: Manual — the user describes their agent's memory needs in prose (what kinds of facts/history/context it must retain, how long, current pain points, deployment constraints like self-hosted vs. managed and budget, and any backend already in use). This skill never calls any memory backend's live API itself — it only reasons over the user's own description. (Note: a related "Memory Mesh" runtime adapter project that this skill's config stub is designed to feed into would be CONNECTED — reaching into Mem0, Letta, Zep, and Cognee's mature documented REST/SDK APIs, plus Supermemory's newer, thinner-documented API. But that live-API integration work belongs to the separate runtime project, not to this advisory skill, which is why its own classification here is Manual rather than Connected.)

Ask for, or extract from what's given:
1. Every distinct *kind* of thing the agent must remember (list each separately — don't let the user lump them together).
2. Retention: how long each kind needs to persist (session-only, weeks, indefinite).
3. Scale: rough query/write volume if known (fine to skip — flag as unknown rather than guessing).
4. Deployment constraints: self-hosted vs. managed acceptable, budget sensitivity, data residency requirements.
5. Current pain point or existing setup, if any (what's broken or manual today).

If any of 1, 2, or 4 is missing, ask one clarifying question before producing a recommendation — do not guess at retention or deployment constraints.

## Procedure
1. **Normalize each memory need** into one of these five categories (state which category each need maps to, don't skip this step even when it feels obvious):
   - Fast key-fact / preference recall (e.g., "what's the user's name, plan tier, settings")
   - Temporal / event-sequenced history (e.g., "when did X start," "what changed between visit 3 and visit 7")
   - Long-horizon narrative summarization (e.g., "summarize this 200-message dispute")
   - Graph-structured relationship recall (e.g., "how is entity A connected to entity B")
   - Cross-source retrieval spanning docs + chat + other data (e.g., RAG-style lookup across heterogeneous sources)
2. **Map each category to a backend** using this fixed decision table (do not invent capabilities not listed here; if the user names a sixth tool not on this list, say so explicitly and ask for its characteristics instead of force-fitting it):
   | Category | Best-fit backend | Why | Maturity/risk note |
   |---|---|---|---|
   | Fast key-fact / preference recall | Mem0 | Purpose-built for fast per-user fact storage with update-in-place (corrects rather than duplicates) | Mature, widely documented, managed or self-hosted |
   | Temporal / event-sequenced history | Zep (Graphiti) | Temporal knowledge graph designed for "what changed when" queries | Mature API; graph backend adds real operational overhead to self-host |
   | Long-horizon narrative summarization | Letta or Zep | Letta persists full reasoning/message history for agents that manage their own memory; Zep's temporal layer also supports this if already in use for history | Letta is a fuller agent runtime, not just a memory library — bigger commitment |
   | Graph-structured relationship recall | Cognee | Graph-structured retrieval across many data sources; runs fully local/air-gapped on Postgres | Mature Python library, good for self-hosted/budget-constrained setups |
   | Cross-source retrieval | Cognee or Supermemory | Both target multi-source ingestion | Supermemory docs are visibly thinner publicly — flag higher integration risk if recommending it for anything load-bearing |
3. **Check for single-backend sufficiency first.** If every normalized need maps to the same backend, or one backend plausibly covers all stated needs even if another is a marginally "better fit," stop here and recommend that single backend — do not recommend a multi-backend combination just because more than one memory *type* was described. State this explicitly as the verdict.
4. **If multiple backends are genuinely warranted**, check for overlap risk: does any single real-world fact plausibly get written to or queried from more than one recommended backend (e.g., a "current plan tier" that's both a fast fact and part of a narrative summary)? For each overlap found, name one backend as authoritative for that fact and state why — never leave two backends with equal claim on the same fact unresolved.
5. **Produce a declarative config stub** listing, for every normalized memory need: `memory_type`, `backend`, `ttl`, `scope`, `authoritative` (true/false, only relevant when overlap exists). This is deliberately shaped to be droppable into a routing/reconciliation layer (such as a `remember()`/`recall()`-style adapter) if one exists or gets built — but it's equally useful as a standalone decision record if the user just hand-wires two SDKs themselves.
6. **Flag caveats** explicitly: never state a specific benchmark number (LoCoMo, DMR, or similar) as fact — vendor and third-party benchmarks for these tools disagree with each other and several are self-reported; tell the user to verify against current docs rather than citing a number. Flag any pre-1.0 or thin-docs tool (currently: Supermemory) as higher integration risk wherever recommended.

## Output format
Always produce these sections, in order, skipping only the ones marked optional:
1. **Memory Needs Summary** — table: stated need → normalized category.
2. **Backend Recommendation** — either a single-backend verdict with reasoning, or a table: category → backend → why → risk note.
3. **Reconciliation Notes** (optional — only if 2+ backends recommended AND an overlap exists) — which backend is authoritative for which overlapping fact, and why.
4. **Config Stub** — a fenced YAML block with one entry per memory need: `memory_type`, `backend`, `ttl`, `scope`, `authoritative`.
5. **Caveats** — benchmark-verification reminder, and any thin-docs/pre-1.0 risk flags that apply.

## Guardrails
- Never recommend combining backends when one backend's documented capabilities already cover every stated need — that's over-engineering dressed up as architecture.
- Never cite a specific accuracy/benchmark number for any of these tools as settled fact; different sources disagree and some are vendor-self-reported.
- Never recommend a tool outside the five covered here without flagging that it's outside this skill's researched decision table and asking the user for its documented characteristics first.
- Never treat this as a substitute for actually calling any memory backend's API — this skill produces a design decision and a config stub, not a working integration.
- Never leave a cross-backend fact conflict unresolved — if two recommended backends could plausibly hold conflicting data about the same real-world fact, name an authoritative backend for it or flag it as an open question needing a human decision, but never stay silent on it.
