# Pin It: An Invariant-Retention Library for Context Compaction

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-13-context-engineering-memory.md · P3
- **Maturity verdict**: PARTIAL — the "sticky slots" branding is one author's blog post (tianpan.co, April 2026), but the underlying technique recurs independently under other names: "constraint pinning" (a Codex CLI/Claude Code write-up with violation-rate numbers), a per-type retention policy (agentpatterns.ai), an academic "Structured Context Eviction" paper (HuggingFace 2606.11213), and a referenced `pi-smart-compact` package's architecture doc. No single widely-adopted library implements it as a named, reusable feature.
- **Format**: BOTH — the compaction-hook middleware and pinned-slot store are PROJECT-shaped; classifying what's invariant for a specific workflow is a one-shot judgment task.
- **Data Sources**: CONNECTED — reads the host agent framework's own live session/context state directly via its compaction hook (e.g. Claude Code's PreCompact hook, LangGraph's checkpointer API, or a generic wrapper around any OpenAI/Anthropic-compatible agent loop). These hook points already exist and are mature in Claude Code and LangGraph today; no external connector needs to be built, only the hook integration.

## The Gap
tianpan.co's "Compaction Traps" names the specific failure: a compaction summary drops what the agent already tried, so it repeats failed approaches on long-running sessions. Four independently-named prior-art threads surfaced in the same search window — constraint pinning, per-type retention, an academic eviction paper, and one package's architecture doc — confirm real, validated demand, but none has shipped as a single reusable, drop-in library.

## The Project
A middleware library that sits in front of any agent framework's compaction pipeline. Before a summarization pass runs, it extracts a bounded "invariant set" — approaches already tried and their outcomes, hard task constraints, and key decisions — into a protected slot that survives every later compaction untouched, while everything else still gets normal lossy summarization. The centerpiece is a pluggable invariant classifier (rule-based plus a cheap-model judgment) that decides what's invariant versus summarizable, paired with a hard token budget on the pinned slot so the fix can't itself balloon back into context rot.

Components: compaction-hook adapters (Claude Code PreCompact, LangGraph checkpoint, generic wrapper); invariant classifier (tried-approaches extractor + constraint extractor); pinned-slot store with a fixed budget and internal eviction; a violation-rate eval harness measuring how often a compacted session re-attempts something already tried.

## Tangible Impact
**Population**: Teams and solo developers running long-horizon autonomous coding or research agents that execute for hours to days and hit automatic context compaction multiple times per session — the cohort reporting "agent repeats failed approaches after compaction" across the tianpan.co post, the constraint-pinning write-up, and the Structured Context Eviction paper's benchmark subjects.
**Mechanism**: Today each compaction pass produces a fresh lossy summary with no memory of what's already been protected, so an agent can re-attempt a fix it tried and failed three compactions ago, burning time and tokens. Pinning the tried/constraint set outside summarization means every future compaction inherits that protected context for free, turning "agent forgot it already tried X" from a recurring tax into a one-time classification cost.
**Measure**: (1) Repeated-failed-approach rate per session before vs. after, on a benchmark of long-running coding tasks with forced compaction. (2) Task completion rate and wall-clock time on multi-hour agent runs. (3) Pinned-slot overhead as a percentage of total context budget, to confirm the fix doesn't just relocate the bloat.

## Why Now
This digest's 30-day window surfaces at least four independently-named attempts at the same underlying technique — real validated demand, no consolidated library — and Claude Code/Codex CLI's compaction hooks now give a stable integration point that didn't exist a year ago.

## Skill Angle
Given a description of an agent's task and its compaction config (or a sample transcript showing a compaction boundary), review and draft the invariant-classification rules for that specific workflow — what counts as "already tried," what's a hard constraint, what's safe to summarize — plus a recommended pinned-slot token budget. A one-shot design/review task useful before anyone wires in the live middleware.

## MVP Sketch
A Python library wrapping Claude Code's PreCompact hook: before each compaction, run a cheap-model pass extracting approaches tried and their outcomes plus explicit hard constraints, write them to a fixed-budget pinned block prepended to every future prompt, and exclude them from the summarizer's input. Experiment: run 10 multi-hour coding tasks designed to force 3+ compactions each, with and without the pinned slot, and measure repeated-failed-approach rate. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- The technique already has 4+ independent namings in 30 days; whichever framework vendor (Anthropic, LangChain) ships this natively first absorbs the idea.
- The invariant classifier is itself an LLM judgment call and can mis-classify — a stale "already tried" pin could block a retry that would now succeed under changed conditions.
- No existing eval harness measures "repeated-failed-approach rate" directly (see this same digest's P4) — the MVP must build its own measurement.
- A sufficiently long session could still accumulate enough invariants to blow the pinned-slot budget, pushing the same compaction-under-pressure problem up one level.
