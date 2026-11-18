# Vendor Switch: A Resilient, Evaluated Relay for Automatic Cross-Vendor Coding-Agent Handoffs

Run a coding agent long enough and you will eventually hit a rate limit, an auth hiccup, or a flat "I'm done for now" mid-task — and the fix today is either to sit and wait, or to open a second tool and manually re-explain, from scratch, everything the first one already figured out. Nobody has shipped a trustworthy way to just hand the baton off.

## The Gap

A Show HN post from late October 2026 ("Agent-relay for multi-vendor coding sessions," github.com/saranyan/agent-relay) named exactly this problem, but the linked repo turned out to be essentially empty — a good idea with nothing behind it. Digging further turned up a more serious attempt: bethvourc/agent-relay, an alpha-stage PyPI package (`agent-relay-tool`, Apache-2.0) with roughly 20 releases since March 2026 and a last push on 2026-11-09, which does hand off coding sessions between Claude Code, Codex, Gemini, Kimi Code, and OpenCode — including automatic handoff when a vendor's rate limit hits. But it sits at just 5 GitHub stars. A separate project with the same name, codervisor/agent-relay, has been stale since December 2025. And Coder's own "Agent Relay" product, despite the name, solves a different problem entirely — where an agent executes, not how a session survives a vendor switch. So the mechanism is proven to work well enough that someone shipped real, iterated code for it — it just isn't evaluated, trusted, or maintained at any scale yet.

## The Project

The idea is a watcher/middleware layer that wraps two or more vendor coding-agent CLIs inside one long-running session. When the active vendor's agent hits a rate limit, an auth failure, or a declared stop, the relay doesn't just alert a human — it serializes the in-flight task state (the decision log, the diffs already applied, the remaining plan) into a vendor-neutral handoff envelope, and automatically resumes the exact same task in a second configured vendor's CLI, seeded with that envelope instead of a blank prompt.

The pieces that make this real rather than a wrapper script: per-vendor adapters that read each CLI's own session output and transcript to detect rate-limit or failure signals; a vendor-neutral handoff-envelope format covering the decision log, applied diffs, and remaining plan; an orchestrator that re-invokes the next configured vendor's CLI seeded with that envelope; and — deliberately not automatic-and-silent — a confirmation gate that surfaces the handoff to the developer before the second agent starts touching files, so a vendor switch mid-task is a visible event, not a surprise. Every piece reads from interfaces that already exist today (each CLI already exposes session logs and exit/rate-limit signals); the project is the adapter and handoff layer on top, not a new integration each vendor has to build.

## Tangible Impact

**Population**: Developers running extended, multi-hour autonomous coding sessions across 2+ vendor CLIs (Claude Code, Codex, Gemini CLI, Kimi Code, OpenCode) — the exact user base the Show HN post and the existing bethvourc/agent-relay alpha tool were built for, who today hit a rate limit or quota wall mid-task and either wait it out or manually re-explain the task's current state to a second tool from scratch.
**Mechanism**: Instead of a rate-limit event stalling a multi-hour agentic task until a human intervenes or restarts the explanation from zero, the relay automatically hands the task to a second vendor's agent with its decision history and current diff state intact, so the session continues without a human-authored re-briefing.
**Measure**: (1) session-continuation success rate — percentage of rate-limit/failure events resulting in a successful automatic handoff versus requiring manual developer intervention, benchmarked against bethvourc/agent-relay's informal claims; (2) context-fidelity score — an independent reviewer's assessment of whether the receiving agent's post-handoff work correctly incorporates the prior agent's decisions with no contradicted or duplicated work; (3) total session downtime (minutes stalled waiting on a human) per multi-hour task, before versus after.

## Try It

This one doesn't have a companion Claude Code skill yet — it's classified `Format: PROJECT` in the idea file. The handoff logic needs a running watcher process tracking live session state and rate-limit signals across multiple CLI tools at once; there's no separable one-shot judgment task you could hand to a chat assistant independent of that runtime. If that changes, a skill will show up at `skills/multi-vendor-coding-agent-relay/` and this page will be updated to link it.

One honest caveat worth carrying over from the idea file's own risk list: bethvourc/agent-relay already exists in alpha with real release history behind it. Building this only clears the bar if the result meaningfully out-executes that existing tool on reliability, evaluation rigor, and vendor coverage — not if it just re-builds the same thing with a different name.

---

Surfaced from `research/2026-11-13-multi-agent-architectures.md`, pattern `P7`.
