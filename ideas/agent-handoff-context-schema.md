# Handoff Envelope: a Typed Context Schema for Agent-to-Agent Handoffs

- **Status**: PROPOSED
- **Date**: 2026-06-10
- **Topic**: Multi-agent architectures
- **Source**: research/2026-06-10-multi-agent-architectures.md · P1
- **Maturity verdict**: PARTIAL — `gh search` finds ~8 handoff-protocol repos all at 0–3 stars (eugene001dayne/chain-thread 3★, Lutren/agent-handoff-protocol 2★, junkyard22/AHP 1★, dakshjain-1616/Agent-Handoff-Protocol 0★ — typed envelopes, none with traction); WebSearch confirms A2A/ACP cover transport but "no universally adopted standard" for handoff context, and OpenAI Agents SDK handoffs pass raw conversation history rather than a typed decision/artifact schema. Many fragmentary attempts, no maintained spec.
- **Format**: BOTH — the schema/validation library is PROJECT-shaped, but drafting a schema instance for someone's specific pipeline is a one-shot judgment task.

## The Gap
Three independent Show HN reinventions in 30 days — Open Envelope (52pts, 2026-05-28), TeamOlimpo (2026-06-07), Agents-Collab.md (2026-05-29) — all attack the same seam: when one agent hands work to the next, decision history, artifacts, error logs, and open questions arrive as a raw text dump, and the receiving agent starts amnesiac. Practitioners describe protocols as "interoperable at the protocol layer but amnesiac at the intelligence layer" and state flatly that "nobody has one" — a formal spec doesn't exist. A2A/ACP standardize transport; nothing standardizes what's inside the envelope.

## The Project
A typed, queryable handoff schema plus a validation/serialization library: a `Handoff` object with structured fields for decisions made (and rejected alternatives), artifacts produced, errors encountered, open questions, and budget consumed — versioned and JSON-Schema-validated. The schema is the centerpiece: adapters render the same envelope into OpenAI Agents SDK handoffs, LangGraph state, and CrewAI task contexts, so heterogeneous agents exchange a contract instead of prose. A conformance test suite ("did the receiver actually get the decision history?") makes the schema falsifiable rather than aspirational.

Components: schema spec (JSON Schema + docs); Python/TypeScript envelope library with validation; adapters for OpenAI Agents SDK, LangGraph, CrewAI; a handoff-fidelity eval (does the downstream agent answer questions about upstream decisions correctly with the envelope vs. raw transcript).

## Tangible Impact
**Population**: Engineering teams operating multi-agent pipelines that cross framework or team boundaries — the cohort generating the failure data in the digest's taxonomy sources, where inter-agent misalignment accounts for 32.3% of 1,642 annotated failure traces (Ema/Redis/orq.ai taxonomies, P5 evidence); concretely, the hundreds of teams represented by the three independent Show HN authors and the ~8 zero-traction handoff repos, each of whom hand-rolled this in the last 30 days.
**Mechanism**: Today a handoff failure means the downstream agent re-derives or contradicts upstream decisions, and debugging means reading two raw transcripts side by side; a typed envelope makes the handoff inspectable (validate before send, query after receive), converting the single most failure-dense seam in multi-agent systems from prose archaeology into a schema check.
**Measure**: (1) On the handoff-fidelity eval, downstream agents answer ≥90% of questions about upstream decisions correctly with envelopes vs. a measured baseline on raw transcripts. (2) Inter-agent misalignment failures in pilot teams' traces drop ≥30% after adoption. (3) ≥2 of the existing fragmentary-repo authors or Show HN builders adopt the spec instead of their own within 90 days.

## Why Now
Three independent reinventions inside one 30-day window is peak duct-tape convergence — the demand is proven and no attempt has won. A2A/ACP shipping transport-layer interop makes the missing content layer newly conspicuous, and OpenAI Agents SDK handoffs (raw history pass-through) give a mainstream integration point to improve upon.

## Skill Angle
Given a description of a multi-agent pipeline (what each agent does, what it hands the next one today, in the user's own words or a code excerpt), draft a tailored Handoff Envelope schema instance — decisions-made, rejected alternatives, artifacts, errors, open questions, budget — plus a short validation checklist the user can apply at each handoff point. This is a one-shot drafting task independent of whether anyone adopts the library; it's useful the moment someone describes their pipeline.

## MVP Sketch
JSON Schema spec + a Python library (`handoff-envelope`) with validate/serialize, one adapter (OpenAI Agents SDK), and the fidelity eval on three multi-step pipeline tasks. Experiment: run the same two-agent pipeline with raw-history handoff vs. envelope handoff; if envelope runs don't measurably reduce downstream decision contradictions and re-work, the schema is ceremony — kill it. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- OpenAI or the A2A project could add a typed context schema to their handoff primitives and absorb this overnight — the strongest already-solved risk.
- Schemas may be inherently lossy for LLM context: the raw transcript sometimes carries nuance a typed envelope strips, and the eval could show raw history wins.
- Standards need adopters; eight zero-star repos suggest everyone wants *their* schema, and a ninth may just join the graveyard.
- Filling the envelope reliably requires the upstream agent to introspect its own decisions — itself an LLM task that can fail.
