# Whose Memory Wins: A Conflict-Resolution Layer for Multi-Agent Shared Memory

Two funded vendors just shipped the same product — a shared "brain" multiple AI agents can read and write to — and both left the exact same hole in it. Not a rough edge. The actual question of what happens when two agents disagree about a fact.

## The Gap

GreenNode's shared-memory design guide lays out what's become the standard fix for a familiar failure: flat shared memory where every agent reads and writes the same undifferentiated pool, and context from one agent's task pollutes another's. The fix is a "scope-chain" architecture — a privileged, read-mostly global layer of facts and business rules, plus per-agent namespaced working state kept separate from it. Reasonable, and increasingly standard.

But look at what's actually shipping on top of that pattern. VentureBeat's coverage of Tencent's Team Memory states plainly that there's no documented mechanism for resolving conflicting writes between agents — the piece calls it, bluntly, "whose memory wins." Mem0's own Organizational Memory page, still in private beta, markets a governance layer for shared memory without ever explaining how a write conflict actually gets resolved. Two shipped-or-beta'd products from two funded teams, both acknowledged-incomplete on the exact same governance question.

It's not for lack of looking. A GitHub search for multi-agent shared-memory governance turns up exactly one attempt — `liaiaaa/dsh-evolution-os`, created in September 2026, sitting at 0 stars. It claims drift detection and tiered write rules, but it's an unevaluated proof of concept, not a tested reference implementation anyone else is running. The scope-chain pattern itself is real and increasingly adopted. The governance layer on top of it — the part that decides who's right when two agents' writes contradict each other — is open.

## The Project

The centerpiece is a conflict-resolution middleware that sits in front of the global, privileged-write layer of a scope-chain memory architecture. When two agents try to write facts that contradict each other, or contradict an existing entry for the same key or entity, the layer doesn't silently overwrite the old value and doesn't block the write outright. It runs a structured resolution protocol instead: a confidence-weighted comparison across source provenance, recency, and agent-reported certainty, resulting either in an automatic resolution when the evidence is clearly decisive, or a "contested fact" state that preserves both versions with full provenance until a designated arbiter agent or a human resolves it. Every resolution — automatic or escalated — gets written to an audit trail that can answer, after the fact, what the system believed, when, and why that belief changed.

That audit trail matters as much as the resolution logic itself. The deliberate narrowness is the point: this isn't a general memory store and it isn't an access-control layer. It exists to answer the one question neither Tencent's nor Mem0's shipped product currently answers.

The pieces: a conflict detector that compares an incoming write against existing global-layer entries for the same key or entity, using embedding similarity plus a cheap-model contradiction check; a resolution-policy engine that routes each conflict to auto-resolve, escalate-to-arbiter, or human-review, configurable per fact category; a contested-fact store that holds both versions with provenance while a conflict is pending; and the audit log tying every decision back to the inputs that produced it.

## Tangible Impact

**Population**: Teams running production multi-agent systems where 5+ specialized agents (e.g., sales-ops, support, and research agents) draw on one shared global fact layer — the same population Tencent's Team Memory and Mem0's Organizational Memory beta are actively selling to, who today have no way to detect or resolve a write-write conflict between two of their own agents.
**Mechanism**: Without this, a contradiction either silently overwrites a possibly-correct earlier fact, or both versions coexist undetected in the store — so whichever agent happens to read the entry next acts on an arbitrary, non-deterministic version of "the truth," and the resulting inconsistent decisions are traceable today only through manual log archaeology after something has already gone wrong downstream. The resolution layer converts a silent, undetectable failure into a visible, policy-governed, auditable event resolved before it propagates to the next agent that reads the fact.
**Measure**: (1) Conflict-catch rate — detected write-write conflicts versus a baseline of silent overwrites, on a synthetic write-contention benchmark seeded with deliberately contradictory facts. (2) Time to resolution (auto-resolved vs. escalated-to-human cases), versus today's baseline of "discovered only after a wrong downstream decision is traced back." (3) Downstream decision-consistency rate — the fraction of agents reading the same contested fact that act on the same, resolved version — before vs. after adoption.

## Try It

A companion Claude Code skill, [`skills/shared-memory-write-conflict-resolver/`](../skills/shared-memory-write-conflict-resolver/), is already written: *"Drafts a conflict-resolution policy for a multi-agent system's shared/global memory layer — which fact categories auto-resolve by recency or confidence, which escalate to an arbiter agent or a human, and what provenance metadata each decision requires. Use when a team is designing or hardening shared memory for 2+ agents that write to the same fact store, before building (or while reviewing) the enforcement middleware itself."*

It's explicitly a planning tool, not the runtime middleware described above — it drafts the policy a human signs off on before anyone wires up live write interception. To use it: drop the `skills/shared-memory-write-conflict-resolver/` folder into `~/.claude/skills/` if you're running Claude Code, and describe your shared-memory setup — which agents write to it, what kinds of facts, and any past conflicts. No Claude Code install? Paste the skill's `README.md` into any AI chat tool as a prompt template; it stands on its own.

## Worth Knowing Before You Build

The most direct risk here is that Mem0 or Tencent simply ship this themselves — both have already named the gap publicly, which means both know exactly what to build next. Confidence-weighted auto-resolution is also a judgment call that can fail in either direction: miscalibrate it and you'll quietly bury a correct fact about as often as you catch a bad one. And at real production write volume, a centralized conflict arbiter sitting in the write path may need to become a proper CRDT-style conflict-free structure rather than a synchronous intercept-and-decide proxy — a genuinely different architecture if the simple MVP approach doesn't scale. It's also worth keeping this distinct from two mechanism-adjacent but population-different ideas already in this pipeline — a single-agent long-session memory-poisoning screen, and an ephemeral sub-agent task-return merger — both share "contradiction detection" DNA but solve a different problem for a different audience.

Surfaced from `research/2026-11-12-multi-agent-architectures-iii.md`, pattern `P4`.
