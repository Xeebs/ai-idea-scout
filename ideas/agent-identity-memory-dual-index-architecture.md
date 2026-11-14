# Stable Self: A Dual-Index Identity/Memory Architecture for Model-Swap-Resilient Agents

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-14-context-engineering-and-memory.md · P7
- **Maturity verdict**: PARTIAL — no exact match for a dual-FAISS read-only-identity/read-write-memory design surviving model swaps, but several adjacent partial implementations exist: `cpersona` (PyPI MCP persona-memory server) documents that a same-dimension model swap "silently invalidates the stored corpus" — it has the identity-persistence problem but not this fix; "Orion" keys agent identity by name and generates a "transition brief" on model change, a different mechanism for the same motivating problem; "Docdex v2.1" separates technical/behavioral memory into a "Dual-Lobe Memory Architecture"; the MENTOR paper (ACL 2026 Findings) uses a dual-chain (global + role) memory to limit identity drift. Independently-converging partial attempts, no shipped match for this specific architecture.
- **Format**: BOTH — the dual-index runtime and migration adapter are persistent infrastructure; drafting a migration plan for an existing agent's memory setup is a one-shot design task.
- **Data Sources**: CONNECTED — the agent's own existing vector-store client (FAISS, pgvector, or a hosted vector DB such as Pinecone/Weaviate, whichever the agent already uses for memory) and its embedding-model API (OpenAI, Anthropic, or a local embedding endpoint already in use). No new external data connector is needed; this project restructures and re-validates data the agent's own stack already holds.

## The Gap
A same-day (2026-11-14) r/ContextEngineering post describes a 6-layer prompt pipeline using two separate FAISS indexes — one read-only for identity/persona facts, one read-write for ordinary memory — specifically to keep an AI's identity stable across model swaps. This is thin, single-thread evidence (zero visible engagement at capture time), but several independent teams are visibly groping toward the same split without a shipped answer: `cpersona` has the identity-persistence problem (a model swap silently corrupts the stored persona corpus) with no fix; Orion patches around it with a post-hoc "transition brief"; Docdex v2.1 and the MENTOR paper each separate identity-adjacent memory from ordinary memory in their own bespoke way.

## The Project
A reusable library splitting an agent's memory into two independently-governed indexes: a read-only (or append-only-with-review) identity index for persona/personality/relationship facts, and an ordinary read-write index for working memory. On a model swap, a migration adapter re-embeds or re-validates only the identity index — cheap and bounded — instead of letting a full-corpus re-embed silently distort the agent's persisted personality, and a drift-detection check runs a fixed set of persona-probe queries before and after the swap to flag when it has, in fact, destabilized the persona despite the split.

Components: dual-index schema wrapper (atop FAISS, pgvector, or a hosted vector DB); a migration/re-embed adapter scoped to the identity lane only; an identity-stability drift check (pre/post-swap similarity probes); a fallback "transition brief" summary for cases migration can't fully preserve identity.

## Tangible Impact
**Population**: Builders and operators of persistent AI companion/persona products — long-running custom personas, character.ai-style companion apps, and personal-assistant products with a named, maintained persona — and, downstream, the users of those products who form a real continuity expectation with "their" AI's personality. This is a documented consumer pain point: Replika's 2023 forced-model-change backlash, widely covered in mainstream press, is the canonical example of users distressed by a visible personality shift after a provider-side model swap.
**Mechanism**: Today a model swap risks the agent's persona drifting or breaking because identity and ordinary memory sit in one undifferentiated store re-embedded or re-validated as a single blob. Splitting the lanes means a swap only has to re-validate the small identity index, making persona continuity a bounded, testable operation instead of an all-or-nothing gamble — and the drift check gives the builder an actual pass/fail signal before shipping the swap to users.
**Measure**: (1) Identity-index re-validation cost (time/tokens) after a model swap, target: a small bounded fraction of a full-corpus re-embed. (2) A before/after persona-consistency score (similarity probe on a fixed set of persona-defining prompts) staying above a set threshold across a swap, versus today's unmeasured drift. (3) Support-ticket/complaint rate about "my AI changed" in a pilot product, before vs. after adopting the split architecture.

## Why Now
This exact architecture surfaced as fresh community signal in the last 30 days, while four independent adjacent attempts (cpersona, Orion, Docdex v2.1, MENTOR) show the field actively groping toward the same split without a shipped, reusable answer — and the underlying primitives (swappable embedding models, dual vector-store collections) are already mature and cheap to combine today.

## Skill Angle
Given a description of an existing agent's memory setup (one combined store, or already-separate stores) and its persona-defining facts, draft a migration plan: which facts belong in the identity lane, a re-validation probe set (fixed test prompts) to check persona stability after a future model swap, and a go/no-go checklist — a one-shot design task distinct from the always-on dual-index runtime and migration adapter.

## MVP Sketch
A thin wrapper exposing `identity.read()` (read-only) and `memory.read/write()` over two FAISS collections, with a `migrate-identity --new-model <x>` command that re-embeds only the identity collection and runs 10-20 fixed persona probe queries before/after, reporting a similarity-drift score. Experiment: seed a toy agent persona, swap its embedding model, and verify the identity probe-drift score correctly flags a genuine persona change while ordinary memory re-embedding proceeds unaffected and untested by the same gate. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- Validated on genuinely thin single-post evidence per the gap-analyst's own note — worth confirming real demand beyond one low-engagement Reddit thread before investing past the MVP.
- cpersona, Orion, or a hosted memory vendor (Mem0, Letta) could ship native dual-lane support first, since they already control both the read and write paths.
- "Identity" and "memory" may not cleanly separate for agents whose persona itself evolves through accumulated experience, undermining the split's core assumption.
- A vector-similarity drift probe is an imperfect proxy for "does this still feel like the same AI to a real user" — would need actual user studies to validate, not just embedding-space scores.
