# Task Anchor: A Compaction-Agnostic Task-State Guarantee for Coding Agents

- **Status**: EXPLORING (promoted 2026-11-13 cycle 35: evidence density — ≥2 independent threads, the `openai/codex` #57608 issue thread with independent cross-platform reproductions plus a separate claudeissues.com report of the identical failure mode in Claude Code's Auto-Compact)
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-and-memory.md · P3
- **Maturity verdict**: OPEN — WebSearch for a shipped fix turned up only more bug reports across tools (community.openai.com threads on "context compression caused Codex to attribute the previous approval error to this task", "automatic compaction does not trigger task-state recovery", `openai/codex` issues #19558/#22107/#29356, claudeissues.com reports of the same failure mode in Claude Code's Auto-Compact) and one third-party forum post describing an unofficial local patch that reattaches the active-goal prompt mid-compaction. No maintainer-shipped fix, library, or product found — only discussion and one person's private workaround, which does not rise to a credible implementation.
- **Format**: BOTH — the always-on task-state checkpoint/reinjection daemon is persistent runtime infrastructure; auditing one specific compaction event's transcript for whether task state survived is a separable one-shot forensic task.
- **Data Sources**: CONNECTED — hooks directly into the host agent harness's own session/compaction lifecycle events (e.g., OpenAI Codex's plugin hook interface, the same `compaction:before`/`compaction:after` hook surface `mindroom-ai/openviking-plugin` already uses against a different harness; Claude Code's hook system for Auto-Compact) to read the live task state and the harness's actual post-compaction continuation in real time — no pasting required. Per-harness hook surfaces already exist today; a uniform cross-harness abstraction over them does not and is what this project builds.

## The Gap

`openai/codex` issue #57608, "Automatic compaction loses active task: continuation receives environment-only user context despite preserved rollout" (2026-10-28, 5 reactions, 16 comments), shows independent reproduction across releases and platforms — one commenter reports an independent Windows occurrence the same day, another reports the bug "still occurring" after a newer release (0.165.0) by inspecting their 10 most recently active sessions. The same failure mode is independently reported in a second, unrelated harness (Claude Code's Auto-Compact, per claudeissues.com). No maintainer in either project has shipped a fix.

## The Project

A thin, framework-agnostic middleware layer that treats "what the agent is currently trying to do" as a protected, independently-tracked checkpoint instead of trusting it to survive whatever lossy compaction algorithm the host harness runs. It hooks the harness's compaction lifecycle, captures a structured task-state snapshot (active goal, acceptance criteria, last few concrete steps taken) as the agent works, and on the harness's own "after compaction" hook, verifies the continuation prompt the harness actually sent to the model still contains that snapshot — reinjecting it if not. This is deliberately not a replacement compaction architecture; it's a cheap, drop-in correctness guarantee layered on top of whatever compaction a harness already does, narrower in scope than a full versioned-context rewrite.

Components: a goal-tracker updating a single structured task-state record keyed off tool calls and user messages; harness adapters for Codex's and Claude Code's compaction hooks; a verifier that diffs the harness's actual post-compaction continuation against the tracked task-state and reinjects on mismatch; a regression-test harness reproducing the exact #57608 repro steps.

## Tangible Impact

**Population**: Developers running long, multi-hour unattended or semi-attended coding-agent sessions in OpenAI Codex and Claude Code — the population directly filing and independently reproducing #57608 across releases and platforms, plus claudeissues.com's independent reports of the same failure mode in a second harness; a conservative proxy is the subset of each tool's many thousands of daily active users whose sessions routinely run long enough to trigger at least one auto-compaction event.
**Mechanism**: Today, when auto-compaction fires mid-task, the agent silently receives only environment context afterward and abandons the active work without warning — the developer discovers this only once they notice drift or stalled progress, often well after the fact, costing diagnosis time plus a lost session. A reattached task-state checkpoint converts this from silent, undiagnosable drift into either a non-event (state survives automatically) or a loud, immediate flag the moment the actual continuation doesn't match what was tracked.
**Measure**: (1) Reproduction rate of the #57608 failure mode on a fixed benchmark of long sessions crossing at least one compaction boundary, with vs. without the middleware. (2) Time-to-detect a dropped task state (immediate flag vs. developer noticing drift later), in minutes. (3) False-positive reinjection rate on a held-out set of normal compaction events.

## Why Now

Multiple independent reproductions across Codex releases and platforms within October 2026, plus a second independent report of the same failure mode in a different widely-used harness, establish this as a general class of harness bug rather than a one-off — and neither maintainer has shipped a fix despite live, acknowledged bug threads, leaving a narrow, well-evidenced gap open for a cross-harness patch layer.

## Skill Angle

Given a session's pre-compaction task description (or transcript excerpt) and the harness's actual post-compaction continuation message, pasted directly, check whether the continuation still contains the active task/goal, acceptance criteria, and the last concrete steps — and if not, reconstruct a corrected continuation that reattaches them. This is a one-shot forensic/repair task useful today for any developer who's hit the bug once and wants a session resumed correctly, without the always-on middleware installed.

## MVP Sketch

A small daemon implementing Codex's plugin hook interface (modeled on `mindroom-ai/openviking-plugin`'s approach to `compaction:before`) plus a Claude Code hook adapter; a simple task-state tracker (one JSON record updated each turn); a verifier run on the "after compaction" hook that checks the continuation against the tracked record and reinjects via a follow-up system message if missing. Experiment: reproduce the `openai/codex` #57608 repro steps exactly, run 20 sessions with vs. without the middleware active, and measure whether task-state-loss drops to near zero. 2–3 weeks for 1–2 people.

## Risks & Open Questions

- OpenAI or Anthropic could ship a first-party fix to their own compaction logic at any time — both have live, acknowledged bug threads, making this the most direct already-being-worked-on risk.
- Hooking a closed-source harness's compaction lifecycle may only be possible where it exposes a plugin API (Codex does); it's unclear whether Claude Code's hook surface supports the introspection needed to verify a continuation message before it reaches the model.
- "Reinject if missing" could mask a deeper compaction bug rather than truly fixing it, papering over a problem that recurs in a different shape later.
- No data yet on whether developers will tolerate another always-on middleware layer for a bug that, while damaging, is intermittent.
