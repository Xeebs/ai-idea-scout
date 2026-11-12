# No Dead Air: Parallel Specialist Dispatch Middleware for Voice Agent Handoffs

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-ii.md · P7
- **Maturity verdict**: OPEN (`gh search repos` found only serial/graph-based orchestration repos, e.g. `haytham042/Multi-Agent-Voice-Orchestration-System` using LangGraph routing; the pattern was found in exactly one practitioner's bespoke blog post (craftedbydaniel.com) plus vendor commentary recommending it in theory; a CallSphere benchmark that tried enabling parallel tool calls found it cut p50 latency only 18% — not the expected 60% — and increased wasted calls, so they disabled it in production; OpenAI Agents SDK, LangGraph, and CrewAI all document serial handoff as their default)
- **Format**: BOTH

## The Gap
The mainstream pattern for routing a voice call to the right specialist agent — a triage agent sequentially classifying intent, then handing off — adds a full LLM round-trip of latency before the right agent even starts talking, exactly inside the budget where every extra hundred milliseconds is audible dead air. FutureAGI's 2026 multi-agent voice post states plainly that "serial dispatch to several workers blows the per-turn budget, so parallel variants are preferred for voice," yet OpenAI's Agents SDK, Vapi, and Trillet's Crews all ship serial triage-then-handoff as their documented default. The one practitioner who built a parallel-dispatch alternative (craftedbydaniel.com) did it as a bespoke, unshared hack, and the one benchmark that tried a naive version (CallSphere) found mixed results and disabled it — meaning the open problem isn't just "nobody built this," it's "building it well (arbitration, cancellation, avoiding wasted calls) is itself unsolved."

## The Project
A stack-agnostic middleware that, on receiving a call, dispatches to multiple candidate specialist agents in parallel rather than waiting on a single triage decision, then arbitrates and cancels the losers once enough signal exists to commit to one — explicitly designed to avoid the CallSphere benchmark's failure mode (wasted calls, marginal latency gain) by making the arbitration/cancellation logic itself a first-class, tested component rather than an afterthought.

Components: a parallel-dispatch coordinator that fires N candidate specialists with partial-transcript context, an arbitration policy that commits to one specialist once confidence crosses a threshold (balancing latency gain against wasted-call cost), a cancellation protocol so losing specialists stop cleanly, and a benchmark replicating CallSphere's test conditions to measure whether this implementation actually beats the 18%-and-worse result their naive attempt got.

## Tangible Impact
**Population**: callers to voice support lines that route across multiple specialist agents (billing, technical, sales) — the direct beneficiaries of shorter or eliminated dead-air during handoff, which is the specific moment call-center UX research consistently flags as a top driver of perceived call quality and abandonment risk.
**Mechanism**: parallel dispatch with disciplined arbitration removes the full round-trip of serial triage from the critical path, shortening the silence between a caller stating their issue and a competent agent responding, without reproducing the wasted-call/marginal-gain failure the one known naive attempt (CallSphere) hit.
**Measure**: time-to-first-specialist-response (p50/p95) vs. serial-triage baseline; call abandonment rate during the handoff window; wasted-compute/cost overhead from parallel dispatch, explicitly reported (not hidden) to be honest about the tradeoff CallSphere's benchmark surfaced.

## Why Now
Cheap, fast LLM inference makes firing multiple candidate specialists in parallel economically viable in a way it wasn't when per-call-leg cost was higher, and CallSphere's public benchmark gives this project a concrete known failure mode to engineer around rather than rediscovering it from scratch.

## Skill Angle
A Claude Code skill that, given a description of an existing serial triage-then-handoff voice agent architecture, reviews it and drafts a parallel-dispatch redesign plan — which specialists are safe to fire in parallel, what arbitration threshold to use, and where cancellation needs to be clean versus where it risks side effects (e.g., a specialist that already started a billing lookup). This is a one-shot architecture-review task distinct from the runtime coordinator itself, useful to a team deciding whether the migration is worth it before building it.

## MVP Sketch
Build the parallel-dispatch coordinator and arbitration/cancellation logic as a plugin for an existing voice-agent framework (Pipecat or LiveKit Agents); replicate CallSphere's benchmark conditions as closely as possible; compare time-to-first-specialist-response and wasted-call rate against both the serial baseline and CallSphere's reported naive-parallel numbers. The single experiment: does disciplined arbitration/cancellation beat CallSphere's 18%-and-worse naive-parallel result, closing enough of the gap to the theoretical 60% latency reduction to justify the wasted-compute cost.

## Risks & Open Questions
- CallSphere's own benchmark is the strongest reason this might not work as hoped — a naive version of exactly this idea already underperformed and got disabled in production.
- Specialists that take real side-effecting actions (starting a payment lookup, writing to a CRM) can't simply be "cancelled" cleanly, which may force a narrower scope (read-only triage dispatch only) than the full vision.
- Wasted-call cost scales with the number of parallel candidates; the arbitration threshold tuning is itself a hard optimization problem with a real cost/latency tradeoff, not a one-time setting.
- If model inference costs rise or per-call-leg pricing changes, the economics that make this viable now could reverse.
