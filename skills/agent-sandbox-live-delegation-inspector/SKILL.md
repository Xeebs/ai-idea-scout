---
name: agent-sandbox-live-delegation-inspector
description: Audits a multi-agent/autonomous-agent system's existing delegation points for three separate gaps — missing per-agent sandbox isolation, missing live (mid-run) observability, and missing the ability to pause/redirect a single misbehaving agent without killing the whole run — and returns a risk-ranked retrofit list. Use before an unattended overnight/long-running multi-agent session ships, during a postmortem after a delegated agent did something it shouldn't have, or when deciding whether to invest in building a step-in control plane at all.
---

# Delegation Isolation & Live-Inspection Auditor

## When to use this
Use this when someone is about to run (or already runs) a multi-agent/delegation setup — Claude Code subagents, OpenHands, Devin-style delegation, a custom orchestrator spawning child agents — unattended for any meaningful stretch, and asks something shaped like: "if one of my sub-agents goes off the rails overnight, would I even notice before it's too late," "can I stop just the broken one without killing the whole run," or "audit our delegation setup before we trust it with a long unattended job." This is a **static, point-in-time audit** of the system's current configuration and code — it inventories gaps and tells you what to build; it does not itself sandbox anything, watch a live run, or pause a running agent. If what's wanted is the always-on runtime that actually does the containing/watching/pausing, that's a separate infrastructure build (a per-agent container orchestrator plus a live-attach control plane), not this skill.

This skill is also distinct from `agent-delegation-chain-scope-tracer` (a sibling skill in this same repo): that one audits delegation code for *credential/permission scope leakage and silent failure propagation*. This skill audits the *runtime containment and observability* question instead — can a bad action be physically contained to one sandbox, can a human see it happening while it happens, and can they intervene on just that agent. A system can pass one audit and fail the other; run both if both questions matter.

## Inputs
**Data source**: Connected — this skill reads the target system's actual delegation/orchestration configuration and code directly: container/sandbox definitions (`docker-compose.yml`, Kubernetes manifests, Dockerfiles used per-agent), the delegation harness itself (Claude Code subagent definitions and the spawning code around them, an OpenHands/Devin-style task-delegation layer, a custom `spawn_agent()`/`delegate()` call site), any event-stream or hook registration code (Claude Agent SDK hooks, OpenHands event-stream subscribers, custom logging/callback wiring), and any pause/kill/control-plane code that already exists. When this skill runs inside Claude Code (or another tool with filesystem access) against the actual repo, read those files directly — never ask the user to re-type or summarize something you can read yourself. When pasted into a plain chat tool with no file access, the user instead pastes the contents of those same files (compose/manifest files, the delegation harness source, hook/callback registration code); a prose description alone ("we use Docker") is not sufficient input — ask for the actual config/code if only a description is offered.

If no delegation/orchestration code or config is found or provided at all, say so explicitly and stop — do not audit a system that doesn't exist yet.

## Procedure
1. **Inventory every delegation point.** Scan the provided code/config for every place a parent process or orchestrator hands a task to a child agent (a subagent spawn call, a container-per-task launch, a task-queue dispatch to a worker agent). Record each as `(ID, location, what gets delegated, which framework/mechanism)`.
2. **Classify isolation per delegation point:**
   - `NONE` — the child runs in the same process/host/filesystem as the parent and siblings, no container or scoped environment at all.
   - `PARTIAL` — some separation exists (separate process, separate OS user, a container that nonetheless mounts the host filesystem read-write or shares a Docker socket/network with siblings) but a misbehaving child could still reach the host or another agent's workspace.
   - `CONTAINERIZED` — a dedicated container (or equivalent sandbox) per agent with scoped filesystem, no shared write access to the host or sibling containers, and resource limits. Verify this from the actual mount/network/capability config — do not credit "we use Docker" alone if the compose file mounts `./:/workspace:rw` into every container or shares a network namespace with the host.
3. **Classify observability per delegation point:**
   - `NONE` — no record of the child's actions exists beyond its final return value.
   - `PASSIVE` — tool calls/file writes/shell commands are logged or traced, but only reviewable after the run completes (a log file, a post-hoc transcript).
   - `LIVE` — a human or parent agent can observe the child's actions (tool calls, reasoning, file diffs) while the run is still in progress, via a hook, event stream, or dashboard that updates in real time.
4. **Classify intervenability per delegation point:**
   - `NONE` — there is no mechanism to act on a running child agent at all; the only option is to let it finish.
   - `KILL_ONLY` — the parent/operator can terminate the entire run (including siblings and parent state) but cannot act on just the one misbehaving agent.
   - `PAUSE_REDIRECT` — the operator can pause, inspect, and redirect or kill the one agent without tearing down the rest of the delegation tree. Checkpoint-boundary pause (pausing at the next tool-call boundary rather than mid-instruction) still counts here; instant mid-call freeze does not need to exist to earn this label.
5. **Score each delegation point's risk:**
   - `CRITICAL` — isolation is `NONE` and intervenability is `NONE` or `KILL_ONLY`: a bad action can reach the host/siblings and the only remedy is killing everything (or nothing).
   - `HIGH` — isolation is `NONE`/`PARTIAL` and observability is `NONE`/`PASSIVE`: nobody would know something went wrong until after it already happened, regardless of containment.
   - `MEDIUM` — isolation is `CONTAINERIZED` but observability is `NONE`/`PASSIVE`, or intervenability is `KILL_ONLY` — damage is contained but the operator is either blind in real time or stuck with all-or-nothing response.
   - `HEALTHY` — isolation `CONTAINERIZED` AND observability `LIVE` AND intervenability `PAUSE_REDIRECT`.
   - If two rules could both apply, use the more severe one.
6. **Write a specific retrofit recommendation for every CRITICAL/HIGH/MEDIUM point** — name the actual gap and a concrete fix (e.g., "delegation point D2 (`spawn_worker()` in `orchestrator.py`) shares the host filesystem — wrap it in a per-agent container with a scoped bind mount instead of the shared workspace mount" or "delegation point D4 has containerized isolation but only post-hoc logs — register a hook on the framework's tool-call event to stream actions to the operator while the run is live"). Never give a generic "add monitoring" fix — tie it to the specific point and mechanism.
7. **Compute the overall verdict**: count of delegation points audited, count CRITICAL/HIGH/MEDIUM/HEALTHY. If zero delegation points were found, the verdict is `NO_DELEGATION_FOUND`.

## Output format
A markdown report, in this order:
1. **Verdict line**: `<N> delegation points audited — <c> CRITICAL, <h> HIGH, <m> MEDIUM, <k> HEALTHY` (or `NO_DELEGATION_FOUND`).
2. **Findings table**: columns `ID | Location | Isolation | Observability | Intervenability | Risk | Retrofit`. Ordered CRITICAL, HIGH, MEDIUM, then HEALTHY (healthy rows may collapse to a single summary line listing their IDs instead of repeating empty retrofit cells).
3. **Priority order**: a numbered retrofit order (which gap to close first) when there's more than one non-healthy point — generally CRITICAL before HIGH before MEDIUM, but note any dependency (e.g., "fix isolation at D1 before building live observability on top of it, since a sandbox-escape would make the dashboard itself untrustworthy").
4. **Closing note (fixed)**: this is a point-in-time read of the provided configuration and code only; it does not sandbox, watch, or pause anything itself, cannot see drift introduced after this audit, and cannot verify a container's isolation holds under an actual exploit attempt — it reports what the configuration claims to do, not a penetration-test result.

## Guardrails
- Never credit `CONTAINERIZED` isolation from the presence of a Dockerfile alone — check the actual mount, network, and capability configuration for shared write access to the host or siblings.
- Never credit `LIVE` observability from a logging statement or framework default — it must show an actual path (hook, event stream, dashboard) that delivers information to a human/parent while the agent is still running, not just a file written for later review.
- Never credit `PAUSE_REDIRECT` intervenability from the mere existence of a "stop" or "cancel" button if that button kills the entire run rather than the one agent.
- Never invent a delegation point, file, or config value not present in the provided input — if a file referenced by the config (e.g., an imported module) wasn't provided, mark that point `UNCLEAR` and name the missing file rather than guessing its contents.
- Never claim this audit provides ongoing protection or proves isolation holds against a real attacker — it is a one-time read of stated configuration, not a penetration test or a running control plane.
- If asked to also build the sandbox/live-inspect runtime itself, say that is a separate, larger infrastructure project and scope it as such rather than quietly expanding this audit into implementation work.
