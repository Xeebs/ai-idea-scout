# Vigil: An Attention-Budget Signal for Supervising Autonomous Agents

"You'll need nerves of steel to work with AI agents" isn't a complaint about agents failing — it's a complaint about watching them. An HN thread with that title pulled 59 points and 82 comments in early November, and almost none of it was about capability. It was about the toll of staying alert for silent failures, rogue tool calls, and scope creep, session after session, with no signal for when to actually look up from your other work.

## The Gap

Go looking for the tool that fixes this and you find plenty of adjacent machinery, but nothing that answers the actual question. Microsoft's open-source Agent Governance Toolkit, AwaitHuman, LangGraph's `interrupt()`, and Gravitee's GAPL all do the same job: gate a specific action against a policy a team wrote in advance. Allow, deny, escalate. That's a solved problem now — rules-as-code for "should the agent be allowed to do this."

None of them scores the aggregate cognitive load of *supervising* a running session. None of them distinguishes a session that's coasting fine from one that's quietly drifting off its plan. The burnout angle itself only turns up commentary — HBR's "AI brain fry" piece, a Forrester analyst note — never a product. Tellingly, the HN thread's own framing is "toughen up," not "here's what fixed this for me." That's the gap: not whether an action should be allowed, but which of several already-running sessions deserves a human's limited attention right now.

## The Project

Vigil sits alongside an agent's existing action stream — no new instrumentation, no SDK to bolt on — and computes a rolling "attention budget" score per session from signals already sitting in the log: how often the agent is calling tools it hasn't used before in this session, how often it's retrying or self-correcting, how long it's been since a human last checked in, and whether its stated next step actually matches what it does next.

Instead of the binary interrupt gate every existing framework offers, Vigil renders a live green/yellow/red per session. Someone watching five concurrent agents stops context-switching into all of them equally, or — worse — trusting all of them until one breaks hard enough to force attention. A yellow-to-red transition fires one specific notification: "session 3: four consecutive tool-call retries, plan hasn't advanced in 6 turns" — not a generic alert that becomes one more thing to tune out.

## Tangible Impact

**Population**: Developers and ops engineers running multiple concurrent semi-autonomous agent sessions day-to-day — the same population the HN thread's 82 comments show self-organizing around informal coping tactics (checking in on a fixed timer, keeping a second monitor open "just in case"), now large enough that JetBrains' 2026 survey puts 90% weekly AI-coding-agent usage among 15,000+ developers surveyed, many running more than one session at once per the thread's own framing.
**Mechanism**: Today a supervisor either checks every session on a fixed interval regardless of whether anything is wrong — wasted attention — or waits for a hard failure to notice something drifted — missed attention. Vigil's rolling score reallocates a fixed attention budget toward the sessions that statistically need it, so the same supervision time catches more real problems with less constant low-grade vigilance.
**Measure**: (1) self-reported vigilance fatigue / check-in frequency before vs. after adoption, surveyed against the HN thread's own framing; (2) time-to-notice for an injected or naturally-occurring drift/scope-creep event, Vigil-flagged vs. unflagged baseline; (3) false-positive rate of yellow/red transitions — alerts the supervisor dismisses as noise — which needs to stay low enough that the signal itself doesn't become a second thing to tune out.

## Why Now

Running several concurrent agent sessions per person is common enough now — per the HN thread and JetBrains' adoption numbers — that the bottleneck has visibly shifted from "can an agent do this" to "can a human keep up with watching several agents do this." Every existing escalation framework answers "should this specific action be allowed," which is a solved-enough problem. Nothing yet answers "which of my running sessions should I actually be looking at right now" — the newer, still-open complaint.

## Try It

A standalone skill version already exists: **[agent-supervision-attention-budget-signal](../skills/agent-supervision-attention-budget-signal/)** — "Ranks several concurrently-running autonomous-agent sessions by how urgently a human supervisor should check in on each one, using retry/novelty/staleness/plan-divergence signals from each session's own transcript."

This is the no-daemon, point-in-time version of Vigil: instead of a live always-on status board, you hand it each session's recent transcript (a file path, or pasted text if that's all you have) plus its original task, and it scores and ranks them the same way the full daemon would — "look at this one first, and here's why." Paste the skill's `README.md` into any AI chat tool to use it anywhere, or drop the `skills/agent-supervision-attention-budget-signal/` folder into `~/.claude/skills/` for Claude Code.

## Worth Knowing Before You Build

The four scoring signals — retry rate, staleness, tool-call novelty, plan divergence — are a first guess at what predicts "needs a look," not a validated model; they need checking against real incidents, not just face plausibility. Alert fatigue is the exact failure mode this project exists to fix, so a noisy Vigil would be strictly worse than no Vigil at all — it just adds a second thing to tune out. Trace formats aren't standardized across agent frameworks, so each new runtime integration (LangGraph, Claude Code, a custom loop) is custom work, the same fragmentation problem already visible in the long-horizon benchmark landscape. And it's entirely plausible the existing escalation-policy vendors — Agent Governance Toolkit, AwaitHuman, LangGraph itself — add an attention-scoring layer on top of what they already ship before this gets built independently; that's worth checking before investing further.

Surfaced from `research/2026-11-18-agentic-ai-autonomous-agents.md`, pattern `P7`.
