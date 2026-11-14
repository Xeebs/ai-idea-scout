# Vendor Switch: A Resilient, Evaluated Relay for Automatic Cross-Vendor Coding-Agent Handoffs

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-13-multi-agent-architectures.md · P7
- **Maturity verdict**: PARTIAL — the exact Show HN repo (saranyan/agent-relay) is essentially empty. A more substantial, actively-maintained implementation already exists: bethvourc/agent-relay (PyPI `agent-relay-tool`, Apache-2.0, Alpha status, 5 GitHub stars, ~20 releases since March 2026, last pushed 2026-11-09), handing off coding sessions between Claude Code, Codex, Gemini, Kimi Code, and OpenCode with context/decision preservation including automatic handoff on rate-limit. codervisor/agent-relay (1 star, stale since Dec 2025) is a separate abandoned attempt, and Coder's "Agent Relay" product (private preview) is a namesake solving a different problem (execution location, not cross-vendor handoff). A real but small, alpha, unevaluated implementation exists.
- **Format**: PROJECT — this requires a running watcher/middleware process tracking live session state and rate-limit signals across tools; there is no separable one-shot judgment task independent of the runtime.
- **Data Sources**: CONNECTED — reads each vendor CLI's own existing session output and status signals: Claude Code's session transcript/output-format logs, and equivalent CLI output or usage-API signals from Codex, Gemini CLI, Kimi Code, and OpenCode. These per-vendor read interfaces already exist today (each CLI already exposes session logs and exit/rate-limit signals); this project builds a per-vendor adapter on top of existing interfaces rather than inventing new ones, though each adapter must be built and maintained as part of this project since no shared cross-vendor API exists yet.

## The Gap
An engine-sourced Hacker News item, "Show HN: Agent-relay for multi-vendor coding sessions" (2026-10-27, 8 points, 1 comment, github.com/saranyan/agent-relay), surfaced this pattern, but the linked repo is essentially empty. Verification found a more substantial but still early project doing the same thing — bethvourc/agent-relay, alpha-stage with ~20 releases but only 5 stars — proving the mechanism (cross-vendor session handoff with context preservation and automatic rate-limit fallback) works well enough to ship, while remaining small, unevaluated, and far from a maintained, trusted tool.

## The Project
A watcher/middleware layer that wraps 2+ vendor coding-agent CLIs in one long-running autonomous session: when the active vendor's agent hits a rate limit, auth failure, or declared stop, the relay serializes the in-flight task state — the decision log, the diffs applied so far, and the remaining plan — into a vendor-neutral handoff envelope, and automatically resumes the exact same task in a second configured vendor's CLI agent, without the developer manually re-explaining the task from scratch.

Components: per-vendor adapters that read session output/transcript and detect rate-limit/failure signals; a vendor-neutral handoff-envelope format (decision log, applied diffs, remaining plan); an orchestrator that re-invokes the next configured vendor's CLI seeded with that envelope; a confirmation gate that surfaces the handoff to the developer before the second agent starts making further changes, rather than handing off silently.

## Tangible Impact
**Population**: Developers running extended, multi-hour autonomous coding sessions across 2+ vendor CLIs (Claude Code, Codex, Gemini CLI, Kimi Code, OpenCode) — the exact user base the Show HN post and the existing bethvourc/agent-relay alpha tool were built for, who today hit a rate limit or quota wall mid-task and either wait it out or manually re-explain the task's current state to a second tool from scratch.
**Mechanism**: Instead of a rate-limit event stalling a multi-hour agentic task until a human intervenes or restarts the explanation from zero, the relay automatically hands the task to a second vendor's agent with its decision history and current diff state intact, so the session continues without a human-authored re-briefing.
**Measure**: (1) session-continuation success rate — percentage of rate-limit/failure events resulting in a successful automatic handoff versus requiring manual developer intervention, benchmarked against bethvourc/agent-relay's informal claims; (2) context-fidelity score — an independent reviewer's assessment of whether the receiving agent's post-handoff work correctly incorporates the prior agent's decisions with no contradicted or duplicated work; (3) total session downtime (minutes stalled waiting on a human) per multi-hour task, before versus after.

## Why Now
Multiple vendor-specific coding CLIs (Claude Code, Codex, Gemini CLI, Kimi Code, OpenCode) reached broad simultaneous adoption through 2026 with persistent, widely-complained-about rate-limit friction, and at least one alpha-stage implementation already proves the core handoff mechanism works well enough to accumulate ~20 releases of real usage — this is a maturity-and-evaluation play against a validated mechanism, not a from-scratch feasibility bet.

## MVP Sketch
Wrap 2 vendor CLIs (e.g. Claude Code plus one OpenAI-compatible CLI) with a watcher that detects a rate-limit or auth-failure exit code, extracts the current git diff plus a structured decision summary, and re-invokes the second CLI seeded with that summary. Experiment: run a fixed, moderately long coding task against a public repo under an artificially lowered rate limit to force at least one handoff, then have an independent reviewer score whether the resulting PR is coherent and non-duplicative across the handoff boundary. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- bethvourc/agent-relay already exists in alpha with real release history — this only clears the bar if the new build meaningfully out-executes it on reliability, evaluation rigor, and vendor coverage rather than re-building the same thing.
- Each vendor CLI's internal session/transcript format is undocumented and can change without notice, making per-vendor adapters an ongoing maintenance burden.
- Automatically continuing a session across vendors risks silently compounding errors if the receiving agent "confidently" continues on a wrong assumption — a confirmation or sanity-check step is necessary, not optional, before the second agent keeps modifying files.
- If a vendor simply raises its own rate limits or ships its own model-fallback switching, demand for a cross-vendor relay specifically could shrink.
