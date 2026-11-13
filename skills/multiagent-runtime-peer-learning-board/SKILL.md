---
name: multiagent-runtime-peer-learning-board
description: Turns one agent's raw fail-then-succeed trace into a generalized, confidence-scored lesson card ready to broadcast to teammate agents (or a human reviewing a multi-agent run), so the same mistake isn't repeated by every agent on the same task separately.
---

# Lesson Extractor for Multi-Agent Runs

## When to use this
Use this the moment an agent on a multi-agent task (parallel fan-out, pipeline, or triage team) hits a failed action and then succeeds on a retry or correction — and you want that fix turned into something a teammate agent (or a human reviewing the run) can use *before* hitting the same wall. Typical triggers:
- A coding-agent fan-out where one subagent's API call, test run, or build step failed and then passed after a parameter/approach change, and other subagents are still mid-run on similar subtasks.
- A multi-step research or data-extraction pipeline where one stage's parser/tool failed on a document and a different approach worked.
- A post-mortem on a finished multi-agent run, done manually before any live shared lesson board exists, to seed a lessons file for the next run.

Do not use this for lessons about a single agent's own long-term memory/self-improvement (e.g. "update my own CLAUDE.md") — this skill is specifically about packaging a lesson for *other* agents working the same or a similar live task, not for persisting personal habits.

## Inputs
**Data source**: Connected — in its full form this reads directly from the orchestration framework's own execution trace/tool-call log (e.g. a Claude Code subagent transcript, a LangGraph node's state history) to detect the fail-then-succeed pattern automatically; no mature, named connector for "live multi-agent execution trace" exists as a product today, so until a framework-specific adapter is built, this skill works from a pasted trace excerpt (manual fallback) — see README for the exact format to paste.

What you hand over:
1. **The trace excerpt** — the failed attempt (action taken, exact error/output) followed by the attempt that succeeded (what changed, exact output). Paste raw tool-call logs, terminal output, or a plain description if logs aren't available — more verbatim detail (exact error strings, exact parameters) produces a more useful lesson.
2. **(Optional) Task type** — e.g. "REST API auth," "PDF table extraction," "flaky test retry." If omitted, infer it from the trace.
3. **(Optional) Output target** — "lesson card for a shared board," "one-line broadcast message," or "both." Default to both.

## Procedure
1. **Isolate the fail→fix pair.** Identify the specific action that failed (the exact tool/API/command call), its exact failure signature (error message, wrong output, timeout — verbatim, not paraphrased), and the specific action that then succeeded. If the input contains multiple unrelated fail→fix pairs, process each as its own separate lesson card — never merge unrelated failures into one lesson.
2. **Diff the failed and successful attempts.** Name precisely what changed between them (a parameter, a library, an ordering, a retry delay, an auth header format, a different tool entirely). This diff is the actual "fix" — if you cannot identify a concrete diff (e.g. the trace shows the fix but not what was different about the setup), say so explicitly rather than guessing.
3. **Assess confidence.** Mark the lesson **HIGH** confidence only if the diff has a plausible causal mechanism explaining why it worked (e.g. "the API requires `Bearer` prefix; the first call omitted it"). Mark it **LOW** confidence if it's a single data point with no clear causal story (e.g. "retried and it worked" with no explanation) — a coincidental retry success (flaky network, race condition) must never be presented as a reliable fix.
4. **Generalize and strip specifics.** Rewrite the fix as a transferable rule ("when calling this API, use header format X") stripped of run-specific identifiers: file paths unique to this run, ticket/task IDs, specific payload values, secrets, or user data. Keep the structural pattern (API name, error class, parameter type) so a teammate hitting a similar-but-not-identical case can still use it.
5. **Tag the task type.** Assign a short task-type tag (e.g. `api-auth`, `pdf-table-extraction`, `flaky-retry`) so the lesson is filterable/queryable by subtask type on a shared board.
6. **Scope it.** State explicitly how narrow the lesson is — "applies to calls to this specific API" vs. "applies to any REST call requiring bearer auth" — don't claim broader applicability than the evidence supports.
7. **Produce the output(s)** per the requested target (see Output format).

## Output format
For each fail→fix pair, produce a **Lesson Card**:

```
LESSON CARD
Task-type tag: <short tag>
Trigger / context: <what the agent was trying to do>
Failure signature: <verbatim error/symptom>
Fix: <the generalized, transferable fix>
Scope: <how broadly this applies>
Confidence: HIGH | LOW — <one-line reason>
Note: <anything missing from the input that would strengthen confidence, if applicable>
```

If a one-line broadcast message is requested (or defaulted to), also produce:

```
BROADCAST: Before attempting <action type>, check <condition> — <team member> hit <failure> and fixed it with <fix>. (confidence: HIGH/LOW)
```

If multiple fail→fix pairs were found in the input, output one full set (Lesson Card + broadcast line) per pair, clearly numbered.

## Guardrails
- Never mark a lesson HIGH confidence from a single occurrence with no causal explanation — default to LOW and say why.
- Never fabricate trace details (error text, parameter values, outcomes) not present in what was pasted. If the trace is missing a piece needed to generalize (e.g. no error message was captured), state that gap explicitly and either ask for it or output the lesson flagged "incomplete — use with caution," never guess and present it as fact.
- Never include secrets, credentials, internal ticket numbers, user data, or run-specific file paths in the generalized lesson text — strip these before output, every time.
- Never merge two unrelated fail→fix pairs into a single lesson card, and never split one coherent fail→fix pair into multiple unrelated cards.
- Never claim a lesson applies more broadly than the evidence supports — when in doubt, scope narrower, not wider.
