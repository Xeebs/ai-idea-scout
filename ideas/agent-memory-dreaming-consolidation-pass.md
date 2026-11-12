# Dream Pass: A Validated Offline Memory-Consolidation Service for Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-memory-ii.md · P6
- **Maturity verdict**: PARTIAL — scattered implementations exist (a research prototype, KasimVali2207/active-dreaming-memory; an indie Rust framework nexo-rs with a scheduled sweep promoting memories into MEMORY.md; a Go package voocel/codebot with a background idle-triggered "dream" step; an OpenClaw community skill; academic papers Auto-Dreamer arXiv 2605.20616 and MindMemOS arXiv 2608.12428) — none is mature, well-adopted, or independently evaluated. Anthropic's own headline figures (Sonnet 4.6 "nearly doubled" its CL-Bench score; a dreaming-built wiki raised one test from 13% to 48%) come from its own single-run research blog, not independently reproduced.
- **Format**: BOTH — the scheduled/automatic consolidation service is persistent infrastructure; running a one-off consolidation pass on a single session's transcript is a self-contained judgment task.
- **Data Sources**: CONNECTED — reads the agent's own prior-session transcripts/logs directly from local storage (e.g. Claude Code's session history directory, a custom agent framework's log files) and writes consolidated notes back into the project's memory files (AGENTS.md or a linked wiki). No third-party API is involved; a small per-framework log-reader adapter needs to be built, since no portable cross-framework version exists today.

## The Gap
Anthropic's "The Components of Agent Memory" (2026-11-06) describes "dreaming" — an agent reviewing its own prior-session logs between sessions, fixing hindsight-visible mistakes, judging what's worth keeping, and writing structured notes — as distinct from in-context learning, compaction, or weight updates, with striking self-reported gains. But secondary coverage explicitly flags "I couldn't confirm elsewhere," and the handful of independent implementations that exist are a research prototype, an indie framework's side feature, and a community skill — exactly the "demos, narrow, unevaluated" profile that keeps this PARTIAL rather than solved, despite a major lab publicly describing and benchmarking the mechanism.

## The Project
A standalone consolidation service that runs between agent sessions regardless of framework: it reads the just-finished session's transcript, judges which facts, decisions, and corrected mistakes are worth keeping (versus noise), and writes them as structured notes into the project's existing memory artifact (an AGENTS.md section or a linked wiki page) rather than appending raw log dumps. The judgment step — deciding salience, not just summarizing — is the centerpiece, paired with an independent evaluation harness that measures whether consolidated memory actually improves next-session task performance, closing the "self-reported only" gap in every existing attempt including Anthropic's own.

Components: a transcript-reader adapter per target framework (Claude Code session logs, a generic JSONL transcript format); a salience-judging pass (what to keep, what to discard, what mistake to flag for correction) with an explicit, inspectable rationale per kept item; a writer that merges new notes into the existing memory artifact without unbounded growth (dedup/prune old entries); an evaluation harness that runs the same multi-session task with and without dreaming enabled and scores downstream task success.

## Tangible Impact
**Population**: Developers and small teams running long-horizon coding agents across multiple sessions on the same project (multi-day or multi-week feature work, the norm for any nontrivial agentic coding engagement) — a population directly overlapping with every Claude Code, Cursor, or custom-framework user whose agent currently starts each new session flat or relying on manual memory-file upkeep.
**Mechanism**: Today, between-session continuity depends on either a flat, manually-maintained memory file (which degrades as it grows, per Anthropic's own framing) or nothing at all (the agent re-derives everything each session); an automated, validated consolidation pass means mistakes made and corrected in session N are actually retained and not repeated in session N+1, without the developer manually curating a growing memory file.
**Measure**: (1) Rate of previously-corrected mistakes repeated in the next session, before versus after adopting the consolidation pass, on a pilot multi-session task set. (2) Independently reproduced task-performance delta (a CL-Bench-style eval run by someone other than Anthropic) comparing dreaming-enabled versus flat-memory baselines. (3) Memory-artifact size and noise over 10+ sessions (does consolidated memory stay bounded and useful, or bloat the way raw logs would).

## Why Now
A major lab just published both the mechanism and striking (if self-reported) results in the last 30 days, giving the pattern real legitimacy and a concrete benchmark (CL-Bench) to reproduce against — but every existing implementation is a solo prototype or buried framework feature, leaving the "independently validated, portable, maintained" version wide open to build right now while interest is highest.

## Skill Angle
Given a single session's transcript (pasted or exported), run a consolidation pass on demand: identify what's worth keeping, flag any mistake made and later corrected, and draft the structured notes to merge into an AGENTS.md or wiki page — without needing the scheduled service running. This is immediately useful standalone for anyone who wants a one-off "what did I learn this session" pass before the automated version exists.

## MVP Sketch
A CLI that reads a Claude Code session transcript, runs the salience-judging pass via an LLM call with an explicit "keep/discard/correct" rationale per candidate note, merges results into a target AGENTS.md section with basic dedup, and a small eval harness running 3–5 multi-session coding tasks with dreaming on versus off, scoring whether session N+1 repeats a mistake from session N. Experiment: if dreaming-enabled runs don't measurably reduce repeated mistakes versus flat-memory baseline, the independent-validation gap the digest found is confirmed rather than closed, and that's the honest result to publish. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- Anthropic itself could ship "Dreaming" as a native, polished feature across its own agent products, absorbing most of the demand before an independent version gains traction.
- Salience judgment is itself an imperfect LLM task — a consolidation pass that keeps the wrong things or discards something important could make memory worse than no consolidation at all.
- Reproducing CL-Bench-style gains independently may simply fail to replicate Anthropic's single-run numbers, which is a valid but much smaller result than the headline figures suggest.
- Unbounded growth of "kept" notes across many sessions could eventually recreate the same context-bloat problem dreaming is meant to solve, if pruning logic isn't genuinely robust.
