# Glass Box: Per-Agent Sandboxed Delegation With Live Step-In Inspection

Right now, running a multi-agent system unattended means picking one of two bad options: let it run fully autonomous and find out what went wrong only after the session ends, or babysit it the whole time and lose the point of delegating in the first place. Nobody has shipped the third option — watch it happen, and step into just the one agent going sideways.

## The Gap

A Hacker News poster put it bluntly in June 2026: "I don't see any good orchestration system for AI agents." They described wanting exactly this — hand a task to a sandboxed sub-agent, then be able to step in mid-run, inspect what it's doing, and redirect it — and said they'd only found scattered component pieces, nothing that combined them. They weren't alone. An independently published blog post titled "Agent orchestrators are bad" and MindStudio's own framing of orchestration as "the biggest unsolved problem in the AI stack" corroborated the same complaint within the same 30-day window, from three unconnected sources. That's not hype-shaped signal ("X is the future") — it's the complaint-shaped kind: people who tried to build this and hit a wall.

The pieces exist. OpenClaw documents a per-agent sandbox-scope model with override/inheritance rules. Docker ships an `Agent` config with a `sub_agents` delegation primitive. Arcade has written about why "Docker sandboxes aren't enough for agent safety" on their own. OpenAI's sandboxing guide warns against running the harness inside the sandbox itself. Every one of these is a component. None of them is wired into a single control plane that gives you isolation *and* a live view *and* the ability to intervene on one agent without nuking the whole run.

## The Project

A delegation runtime that gives every agent in a multi-agent system its own isolated container — one sandbox per agent, following OpenClaw's scoping model — paired with a control plane that lets a parent agent or a human delegate a task, watch that sandboxed agent's live actions (shell commands, file writes, tool calls) as they happen, and step in: pause, inspect its current reasoning state and queued tool calls, then resume, redirect, or kill that one agent without tearing down the rest of the delegation tree.

The centerpiece isn't isolation — several vendors already ship that — and it isn't passive observability dashboards either — several more ship that too. It's the combination: containment *and* a live window *and* the ability to actually do something about what you're seeing, mid-run, scoped to the one agent that's misbehaving.

Four components do the work: a per-agent container orchestrator handling Docker lifecycle for each delegated agent; a live-attach protocol with pause/resume semantics and a state snapshot of in-flight reasoning plus queued tool calls; an inspection UI that renders the delegation tree with a live action feed and file diffs per node; and a delegation API that parent agents call to hand off work and later re-attach to it.

## Tangible Impact

**Population**: Developers and small teams running autonomous coding/ops agents in multi-step unattended sessions — the overnight-refactor-agent and on-call-remediation-agent crowd, on frameworks like Claude Code subagents, OpenHands, or Devin-style delegation. This is the exact population behind the HN poster's "has anyone built" ask and the corroborating "biggest unsolved problem" framing from vendor blogs in the same window.

**Mechanism**: Today, this group faces a binary choice — full autonomy with zero visibility until the run finishes (risking a wasted session or a damaging action nobody catches in time), or constant supervision that defeats the purpose of delegating at all. A per-agent sandbox with live step-in turns "kill the whole run and restart" into "pause the one agent that's off the rails, see exactly what it was doing and why, and redirect it" — containing the damage to one sandbox and salvaging everything the rest of the delegation chain already got right.

**Measure**: (1) Time to detect and intervene in a misbehaving agent, in minutes, versus "never, until the run ends" today. (2) Fraction of sessions salvaged — continued after a targeted intervention — versus fully restarted, measured on a benchmark of injected-fault delegation scenarios. (3) Containment rate: in fault-injection tests, the fraction of a sandboxed agent's bad actions (attempted writes outside its scope, for instance) that never reach the host or a sibling agent's sandbox.

## Why Now

Per-agent container sandboxing primitives — OpenClaw's scope model, Docker's native agent delegation config — only matured in the last several months. Combine that with the explicit "has anyone built" ask and multiple vendor posts calling orchestration unsolved, all landing inside the same 30-day digest window, and the read is simple: the pieces now exist to wire together, and nobody has done it yet.

## Try It

A companion skill, `agent-sandbox-live-delegation-inspector`, ships alongside this idea: **"Audits a multi-agent/autonomous-agent system's existing delegation points for three separate gaps — missing per-agent sandbox isolation, missing live (mid-run) observability, and missing the ability to pause/redirect a single misbehaving agent without killing the whole run — and returns a risk-ranked retrofit list."**

It's a static, point-in-time audit, not the runtime itself — it won't sandbox, watch, or pause anything for you. What it does do is take your actual delegation config and code (container manifests, the spawning harness, hook/event-stream wiring) and tell you exactly which delegation points are `CRITICAL`, `HIGH`, or `MEDIUM` risk, with a specific retrofit for each. Use it before an unattended multi-agent run ships, or as a postmortem after one of your sub-agents did something it shouldn't have.

To use it: paste the [README](https://github.com/Xeebs/ai-idea-scout/tree/main/skills/agent-sandbox-live-delegation-inspector/README.md) into any AI chat tool along with your delegation config and source, or drop the whole `skills/agent-sandbox-live-delegation-inspector/` folder into `~/.claude/skills/` if you're running Claude Code.

## The Catch

The strongest reason this might not stay open for long: Arcade, Docker, and OpenAI have all already published posts naming this exact gap — any one of them could ship the combination themselves before an independent build gets there. There's also a real technical ceiling on the "live" half of the ask: true mid-tool-call pause is hard for stateful agents, since an in-flight API call or shell command often can't be safely frozen — a real build likely has to settle for pausing at the next checkpoint, which is weaker than what the original HN poster actually wanted. And running one container per agent adds genuine infrastructure overhead once you're coordinating dozens of concurrent sandboxes rather than a handful — that's unproven at scale.

Surfaced from `research/2026-11-12-multi-agent-architectures-iii.md`, pattern `P2`.
