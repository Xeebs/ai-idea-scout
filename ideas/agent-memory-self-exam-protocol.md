# Self-Exam: A Drop-In Memory Integrity Protocol for Long-Running Agent Staff

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-12-agentic-ai-autonomous-agents-ii.md · P7
- **Maturity verdict**: PARTIAL — academic self-testing memory-compression research exists (SelfMem arXiv 2607.03726, Agent Cognitive Compressor arXiv 2601.11653, AgentMemBench, DreamBench-SWE) but none is packaged as a deployable, drop-in self-checking protocol for a persistent multi-agent "staff"; the only real-world instance found is one solo operator's bespoke, untested-at-scale system.
- **Format**: BOTH

## The Gap
A 2026-11-10 r/aiagents field report from a non-programmer running "a company staffed by two AI models" for three months describes a memory-compression protocol — designed by the agents themselves — that "makes compressed memory pass exams," and reports that this month the system's own self-check caught a failure for the first time. This surfaces a real gap: agents that compress memory are common, but agents that can *prove* their compression didn't silently lose something are not, and academic self-testing work hasn't reached a form any small operator could actually install.

## The Project
A reusable protocol and harness that wraps an existing agent memory/compression layer with a periodic self-exam: after every compression event (or on a schedule), the harness generates probe questions against the pre-compression source material, asks the agent to answer them using only the post-compression memory, and scores the answers against the known-correct source. A failing score flags the specific compression event as degraded, rolls back to the last known-good memory snapshot, and surfaces the failure to the operator — instead of the degradation silently persisting until something downstream breaks, as happened in the source field report.

Core components: a probe-question generator (templated against the pre-compression content), a scoring comparator, a memory-snapshot versioning store for rollback, and an alerting hook.

## Tangible Impact
**Population**: Small operators and teams running persistent, long-horizon multi-agent "staff" — AI agents that run a business function continuously over weeks or months, as in the source report — who have no engineering team to build or audit a memory-integrity check themselves and are currently relying on either no check at all or a bespoke, unvalidated one they built ad hoc.
**Mechanism**: A drop-in self-exam turns "we found out our memory was degraded when something went wrong downstream" into "we found out before anything downstream was affected," with an automatic rollback path that recovers the last verified-good state rather than requiring manual forensic reconstruction.
**Measure**: time from a compression event to detection of any resulting degradation (target: before the next decision relying on that memory, not after); false-positive rate of the self-exam (flagging good compressions as bad); percentage of degradation incidents caught by the self-exam versus discovered downstream in production use.

## Why Now
The source field report shows this gap being hit in live, ongoing operation right now (a non-expert operator stumbled into needing exactly this and built a crude version themselves), while the academic building blocks (self-coverage testing, drift-judge evaluators) already exist and just need to be packaged into something installable rather than left as research code.

## Skill Angle
A companion skill, "Memory Audit Once," takes a snapshot of an agent's current compressed memory plus the original source material it was compressed from, generates a one-time exam, scores it, and reports which facts were lost or distorted — useful as a one-off health check or pre-adoption diligence step, distinct from the harness's job of running this continuously and automatically rolling back inside a live system.

## MVP Sketch
Two to three weeks, one person: build the probe-generator and comparator against one memory-compression library (pick whichever the target early-adopter community already uses), wire in snapshot versioning with a simple rollback command, and validate by deliberately injecting three known types of compression-induced information loss (dropped fact, contradicted fact, merged-and-confused facts) and confirming the self-exam catches all three.

## Risks & Open Questions
- Probe-question generation quality is the whole product — a weak generator that only tests trivial recall won't catch the subtle degradations that matter (the ones the source report's own system apparently missed for three months before catching one).
- Single-evidence-source risk: this pattern rests on one field report; worth a lightweight search for other solo-operator "agent staff" builds hitting the same wall before committing past MVP.
- Overlap risk with general RAG-evaluation tooling already in this ledger (e.g., ClaimTrace, MemLeak Bench) — this project must stay scoped to compression-integrity self-testing for persistent agent memory, not re-become a generic RAG eval harness.
- Rollback granularity (per-event snapshot) could get expensive in storage for very long-running agents; needs a retention/pruning policy from day one.
