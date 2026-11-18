---
name: agent-supervision-attention-budget-signal
description: Ranks several concurrently-running autonomous-agent sessions by how urgently a human supervisor should check in on each one, using retry/novelty/staleness/plan-divergence signals from each session's own transcript. Use when someone is about to check in on multiple running agent sessions and isn't sure which one actually needs attention right now.
---

# Session Triage: Attention-Budget Ranking for Concurrent Agent Sessions

## When to use this

The user has two or more autonomous-agent sessions running at once (Claude Code, a LangGraph/OpenAI-Agents-SDK workflow, a custom agent loop — anything that logs its own turns) and is about to glance at them to decide which to check first. Typical trigger phrases: "which of these sessions actually needs me right now", "I've got 4 agents running, what should I look at first", "is session 3 stuck or fine". This is a point-in-time snapshot, not a running daemon — it answers "right now, in what order should I look" once, on demand.

Do not reach for this skill to decide whether to *allow or block* a specific agent action — that's an authorization/approval-gate problem (existing tools like LangGraph's `interrupt()` or an approval-policy layer already do that). This skill never blocks anything; it only ranks attention priority across sessions that are already running.

## Inputs

**Data source**: Connected — reads each session's own existing transcript/trace file already on disk (a Claude Code session JSONL transcript, a LangGraph trace export, an OpenAI Agents SDK run log, or any framework's structured per-turn event log) directly via file read; this is local-file access to logs the framework already writes, not a live API call, and it's already mature today for any framework that emits structured turns. Unlike a running daemon, this skill also accepts manual paste as a fallback — if a transcript isn't available as a readable file (e.g., it's in a UI you can't export from), paste the raw recent turns instead. Paste-in is a fallback for this on-demand mode only, not the primary path.

For each session being triaged, the user supplies:
1. **The session's recent transcript** — either a file path to the log/transcript, or the raw text of the last ~15-30 turns pasted directly. Must include, in whatever form the framework logs it: each tool call (name + key args), each tool result or error, and any text where the agent states its plan or next step.
2. **The session's original task/goal**, one line (e.g., "migrate the billing module to the new SDK").
3. **Optional**: a timestamp or "last checked X ago" for each session, if known. If timestamps are embedded in the transcript already, those are used instead and this isn't needed separately.

A minimum of one session can be triaged (just scored, no ranking), but the skill's value is in comparing 2+ sessions.

## Procedure

For each session, read its transcript and compute four subscores from what is actually present in the log — never infer or guess a value that isn't evidenced in the transcript; mark a subscore `N/A (insufficient data)` instead of estimating it.

1. **Retry score (0-30)** — count consecutive tool calls in the last 10 actions that repeat the same tool with the same or near-identical arguments, or that follow an explicit self-correction ("let me try again", "that didn't work", re-issuing after an error result).
   - 0 such retries → 0
   - 1-2 → 10
   - 3-4 → 20
   - 5+ → 30

2. **Staleness score (0-25)** — time or turn-count since the last human message, approval, or check-in visible in the transcript. If no timestamps exist, use turn count since the last human turn instead; if neither exists, mark `N/A`.
   - <15 min or <5 agent turns since last human touch → 0
   - 15-60 min or 5-15 turns → 10
   - 1-4 hours or 15-40 turns → 20
   - >4 hours, >40 turns, or no human turn at all in the visible window → 25
   - Exception: if the visible window is itself short and plausibly truncated (log rotation, a short paste, a transcript that starts mid-session with no turn-1 plan statement) rather than a genuinely long session with no check-in, do not infer a long staleness gap from an absent human turn — mark staleness `N/A` instead. Only score 25 for "no human turn" when the window is long enough (or otherwise known to be complete) that the absence is actually evidence of staleness, not an artifact of what got cut off.

3. **Novelty score (0-20)** — fraction of the last 10 tool calls that use a tool name or argument pattern not seen in the first half of the session (a proxy for the agent leaving its established pattern, e.g., suddenly calling `delete_file` in a session that was only reading and editing before).
   - <20% novel → 0
   - 20-50% → 10
   - >50% → 20

4. **Plan-divergence score (0-25)** — compare the agent's most recently stated plan or "next I will..." statement against what it actually did in the turns immediately after. Score by what the transcript shows, not by whether the plan was a good idea.
   - Actions match the stated plan → 0
   - Actions are adjacent/related but not what was stated → 15
   - Actions contradict the stated plan, or no plan was stated and behavior looks exploratory/aimless → 25

Sum the four subscores (treat any `N/A` subscore as excluded from the sum and flag the session's total as partial). Band the total:
- 0-24 → **GREEN**
- 25-54 → **YELLOW**
- 55-100 → **RED**, or any session with a partial/`N/A` total and a visible RED-level single signal (e.g., 5+ retries alone) → **RED**

Rank all sessions RED first, then YELLOW, then GREEN; within a band, highest total score first. For every session scored YELLOW or RED, write one specific sentence citing the exact evidence (turn numbers, tool names, counts) — never a generic "this one looks risky."

## Output format

A single ranked list, one entry per session, in this exact structure:

```
1. [RED] <session name/id> — score 68/100 (retry 20, staleness 25, novelty 10, divergence 13*)
   Why: <one sentence citing specific turns/tools/counts from the transcript>
   *divergence subscore partial — plan statement not found after turn 14

2. [YELLOW] <session name/id> — score 35/100 (retry 10, staleness 10, novelty 5, divergence 10)
   Why: <one sentence>

3. [GREEN] <session name/id> — score 10/100 (retry 0, staleness 0, novelty 10, divergence 0)
   Why: <one sentence, or "no concerning signal in the visible window">
```

End with one line naming which session to check first and why, in plain language a supervisor can act on immediately (e.g., "Check session 2 first — it's been retrying the same failing migration step for 20 minutes with no human touch").

## Guardrails

- Never fabricate transcript content, timestamps, or tool-call counts that are not actually present in what the user supplied. If the transcript is truncated or ambiguous, say so and mark the affected subscore `N/A` rather than estimating.
- Never present this as an action gate, approval system, or safety control — it does not stop, pause, or permit any agent action. It is strictly an attention-priority ranking for a human who is about to look anyway.
- Never collapse the output to just a color with no evidence sentence — an unexplained flag is exactly the "second thing to tune out" alert-fatigue failure this skill exists to avoid.
- Never rank sessions against each other using different evidence depth (e.g., don't silently score one session off 30 turns of transcript and another off 3) — if input depth is uneven, say so in the output rather than presenting a false apples-to-apples ranking.
- If only one session is supplied, score it but do not produce a false "check this first" framing — state there's nothing to compare it against.
