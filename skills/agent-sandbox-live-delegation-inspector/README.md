# Delegation Isolation & Live-Inspection Auditor

A prompt template for auditing a multi-agent/autonomous-agent system's delegation setup before you trust it with an unattended run. It answers three questions for every place your system hands a task off to a sub-agent: if that agent misbehaves, is the damage contained to its own sandbox, would you see it happening while it happens, and could you stop or redirect just that one agent without killing the whole job?

This is a **one-time, point-in-time audit** of your current setup. It does not sandbox anything, watch a live run, or pause a running agent itself — it tells you exactly where those capabilities are missing and what to build to close each gap.

## When to use this

Use it when:
- You're about to let a multi-agent system (Claude Code subagents, OpenHands, a Devin-style delegation setup, a custom orchestrator) run unattended overnight or for a long unsupervised stretch, and want to know what happens if one of the delegated agents goes wrong.
- You're doing a postmortem after a sub-agent did something it shouldn't have, and want to know exactly which gap let it happen.
- You're deciding whether to invest engineering time in building a real-time "pause and inspect one agent" control plane, and want a prioritized list of what's actually missing first.

## What to hand over

This audit needs your **actual configuration and code**, not a prose description of it. Paste in:
1. Your container/sandbox setup for delegated agents — `docker-compose.yml`, Kubernetes manifests, Dockerfiles, or whatever defines what environment each sub-agent runs in.
2. The delegation code itself — wherever a parent process hands a task to a child agent (a subagent-spawn call, a task-queue dispatch, a `delegate()`/`spawn_agent()` function, Claude Code subagent config files).
3. Any logging, hook, or event-stream code already wired up to watch what a delegated agent does (if any).
4. Any existing "stop/cancel/kill" mechanism for a running delegation (if any).

If you only have a description of your setup rather than the files themselves, paste the files anyway if you can get them — "we use Docker" without the actual compose file isn't enough to classify isolation accurately, since a container that mounts your whole filesystem read-write provides essentially no isolation at all.

If you have none of this yet (no delegation system built), say so — this audit has nothing to audit until there's a real delegation point to look at.

## How it works

For every delegation point found in what you provide, the audit scores three independent axes:

**Isolation** — how contained is a misbehaving child agent?
- `NONE`: same process/host/filesystem as everything else.
- `PARTIAL`: some separation, but a shared Docker socket, shared network namespace, or a read-write mount of the host filesystem still lets a child reach outside its own sandbox.
- `CONTAINERIZED`: a dedicated container per agent with a scoped filesystem, no shared write access to the host or siblings, and resource limits — verified from the actual mount/network config, not assumed from "it's in Docker."

**Observability** — would you see trouble while it's happening?
- `NONE`: no record of the child's actions beyond its final output.
- `PASSIVE`: actions are logged, but only reviewable after the run finishes.
- `LIVE`: a human or parent agent can watch the child's tool calls, reasoning, or file diffs in real time while it's still running.

**Intervenability** — could you act on just the one problem agent?
- `NONE`: no way to act on a running child at all.
- `KILL_ONLY`: you can kill the entire run (including unrelated agents and progress) but not isolate and stop just the one.
- `PAUSE_REDIRECT`: you can pause, inspect, and redirect or kill the one misbehaving agent without tearing down the rest. Pausing at the next tool-call boundary counts — it doesn't need to freeze mid-instruction.

Each delegation point then gets a risk score:
- **CRITICAL**: no isolation and no way to stop just the one agent — a bad action can reach your host or other agents, and your only remedy is killing everything or nothing.
- **HIGH**: isolation is missing or partial, and you wouldn't know something went wrong until after the fact, regardless of containment.
- **MEDIUM**: damage would be contained (containerized), but you're either blind in real time or stuck with all-or-nothing response.
- **HEALTHY**: containerized, live-observable, and individually pause/redirect-able.

## What you get back

A markdown report with:
1. A one-line verdict: how many delegation points were found and how many fell into each risk tier (or `NO_DELEGATION_FOUND` if none were found).
2. A findings table — one row per delegation point, with its location, its isolation/observability/intervenability ratings, its risk tier, and a specific, named fix (not a generic "add monitoring" — an actual recommendation tied to that exact spot in your code/config).
3. A priority order for which gap to fix first when there's more than one, including any ordering dependency (e.g., fix isolation before building a live dashboard on top of an agent that can still escape its sandbox).
4. A closing note reminding you this is a read of your stated configuration, not a penetration test — it can't verify a sandbox holds against an actual exploit attempt, only that the configuration claims to provide one.

## Rules this audit follows

- It never credits containerized isolation just because a Dockerfile exists — it checks whether the mount/network config actually scopes the container, since a container with a read-write bind mount of your whole repo is barely isolated at all.
- It never credits live observability from a logging statement alone — logging that's only readable after the run ends is "passive," not "live," even if it's thorough.
- It never credits real intervenability from a generic "stop" button that kills the whole run rather than one agent.
- It never invents a delegation point, file, or line that wasn't in what you provided — if something referenced isn't available (an imported module, a missing config file), it says so and asks for it rather than guessing.
- It never claims to provide ongoing protection — it's a one-time audit of what you showed it, not a running safeguard.
- If you ask it to go further and actually build the sandboxing/live-inspection system, it will say that's a separate, larger engineering project rather than quietly expanding the audit into implementation work.

## Related but different

If your concern is specifically about a sub-agent getting **more permission/credential scope than it should have**, or a sub-agent's **failure being silently swallowed** rather than reported back to the parent, that's a different audit (focused on credential narrowing and failure propagation, not on sandbox containment or live observability). This README's audit is about physical/runtime containment and visibility — whether a bad action stays inside its box and whether anyone can see and stop it while it's happening.
