# Vigil: An Attention-Budget Signal for Supervising Autonomous Agents

- **Status**: EXPLORING
- **Date**: 2026-11-18
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-18-agentic-ai-autonomous-agents.md · P7
- **Maturity verdict**: PARTIAL — WebSearch found several policy/approval-escalation frameworks (Microsoft's open-source Agent Governance Toolkit, AwaitHuman, LangGraph's `interrupt()`, Gravitee's GAPL) that implement allow/deny/escalate mechanics, but none targets the specific gap the community names: a UX/cognitive-load-aware signal for "when does a human actually need to look." The burnout framing itself only turned up commentary/surveys (HBR "AI brain fry", Forrester analyst notes), no product. Adjacent tooling exists, so PARTIAL over OPEN per the tie-break rule.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the target agent runtime's own existing action/tool-call event stream (whatever the team's framework already emits — LangGraph traces, a Claude Code session transcript, an OpenAI Agents SDK run log) directly off disk or the framework's logging API; no new telemetry needs to be instrumented by hand, and no paste-in required for the daemon mode.

## The Gap

An HN thread, "You'll need nerves of steel to work with AI agents" (59 pts, 82 comments, 2026-11-05), frames staying vigilant for silent failures, unexpected tool calls, and scope creep as an endurance problem the human has to toughen up for — not a tooling gap someone has already closed. WebSearch supplements confirm existing escalation frameworks (Agent Governance Toolkit, AwaitHuman, LangGraph `interrupt()`, GAPL) are all policy/authorization layers that gate specific actions against rules a team writes in advance. None of them scores or signals the *aggregate cognitive load* of supervising a running agent, or distinguishes "this session needs a close look right now" from "this one is coasting fine" — the thing the HN thread's commenters are actually describing as exhausting.

## The Project

Vigil sits alongside an agent's existing action stream (no new instrumentation) and computes a rolling "attention budget" score per session from signals already present in the log: rate of novel tool calls vs. the session's established pattern, frequency of self-corrections or retries, time since the last human check-in, and divergence between the agent's stated plan and its actual next action. Instead of a binary interrupt gate (the existing frameworks' model), it renders a small live status — green/yellow/red per running session — so someone supervising five concurrent agent sessions knows which one to actually look at next, instead of context-switching into all of them equally or trusting none of them until a hard failure forces attention. A yellow→red transition pushes a single, specific notification ("session 3: four consecutive tool-call retries, plan hasn't advanced in 6 turns") rather than a generic alert.

## Tangible Impact

**Population**: Developers and ops engineers running multiple concurrent semi-autonomous agent sessions day-to-day — the same population the HN thread's 82 comments show self-organizing around informal coping tactics (checking in on a fixed timer, keeping a second monitor open "just in case"), now large enough that JetBrains' 2026 survey puts 90% weekly AI-coding-agent usage among 15,000+ developers surveyed, many running more than one session at once per the thread's own framing.
**Mechanism**: Today a supervisor either checks every session on a fixed interval regardless of whether anything is actually wrong (wasted attention), or waits for a hard failure to notice something drifted (missed attention). Vigil's rolling score reallocates a fixed attention budget toward the sessions that statistically need it, so the same supervision time catches more real problems with less constant low-grade vigilance.
**Measure**: (1) self-reported vigilance fatigue/check-in frequency before vs. after adoption, surveyed against the HN thread's own framing; (2) time-to-notice for an injected or naturally-occurring drift/scope-creep event, Vigil-flagged vs. unflagged baseline; (3) false-positive rate of yellow/red transitions (alerts the supervisor dismisses as noise) — needs to stay low enough that the signal doesn't just become a second thing to tune out.

## Why Now

Running several concurrent agent sessions per person is now common enough (per the HN thread and JetBrains' adoption numbers) that the bottleneck has visibly shifted from "can an agent do this" to "can a human keep up with watching several agents do this" — exactly the framing the thread's 82 comments converge on. Every existing escalation framework answers "should this specific action be allowed," which is a solved-enough problem; nothing yet answers "which of my running sessions should I actually be looking at right now," which is the newer, still-open complaint.

## Skill Angle

A "Session Triage" skill handles the no-daemon, point-in-time case: trigger is a supervisor about to check in on several running agent sessions and unsure which to prioritize. Input is each session's recent action log (pasted or read from a local session-transcript file) plus its original task description. The skill scores each session's drift/retry/plan-divergence signals the same way the daemon would and returns a ranked "look at this one first, and here's why" list — useful standalone, and a way to validate the scoring heuristic's usefulness before committing to the always-on daemon build.

## MVP Sketch

A lightweight log-tailing process that ingests one framework's existing trace format (start with LangGraph or Claude Code session transcripts, since both already emit structured per-turn events), computes the four signals above over a sliding window, and renders a single-page status board across however many sessions are registered. Single experiment: run it against one developer's real multi-session week, compare Vigil's red-flagged moments against the developer's own end-of-day recollection of which sessions actually needed intervention, and check precision/recall on that self-report.

## Risks & Open Questions

- The four proposed signals (novel-tool-call rate, retry frequency, check-in staleness, plan divergence) are a first guess at what predicts "needs a look" — they need validation against real incidents, not just face validity.
- Alert fatigue is the exact failure mode this project is trying to fix elsewhere in the pipeline (voice-agent and guardrail ideas hit the same wall) — a noisy Vigil is worse than no Vigil, since it adds a new thing to tune out on top of the agent itself.
- Framework trace formats are not standardized, so each new agent runtime integration is custom work; this could fragment the same way the long-horizon benchmark landscape (P4, this same digest) already has.
- The existing escalation-policy products (Agent Governance Toolkit, AwaitHuman, LangGraph `interrupt()`) could plausibly add an attention-scoring layer themselves before this ships independently — worth checking their roadmaps.
