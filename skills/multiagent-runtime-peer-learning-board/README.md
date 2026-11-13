# Lesson Extractor for Multi-Agent Runs

A self-contained prompt template. Paste this whole document (or just the "Prompt" section at the bottom) into any AI chat tool, then paste your trace when asked.

## What this is for

You're running (or reviewing) a multi-agent task — several AI agents working the same job in parallel or in a pipeline (a coding task fanned out across subagents, a multi-stage research/data-extraction pipeline, a support-triage team). One agent hit a failed action and then fixed it on a retry or correction. You want that fix turned into a reusable "lesson" that another agent (or a human) can read *before* hitting the same wall, instead of every agent on the team re-discovering the same fix independently.

This is not a tool for personal self-improvement notes ("update my own memory file"). It's specifically for packaging one agent's hard-won fix so it transfers to a *different* agent facing a similar-but-not-identical situation on the same or a future run.

## Data source

This works from a trace excerpt you paste in — the exact tool calls / commands / API responses / error messages involved in the failed attempt and the one that succeeded afterward. In a fuller integration this would read directly from an orchestration framework's own execution log (a Claude Code subagent transcript, a LangGraph state history, etc.), but no mature off-the-shelf connector for "live multi-agent execution trace" exists yet as a product — so for now, you export or copy the relevant trace snippet and paste it here. The more verbatim the paste (exact error text, exact parameters, exact before/after), the better the lesson.

## What to hand over

1. **The trace excerpt** (required) — the failed attempt and the successful attempt that followed it, as close to verbatim as you can get: what action was taken, what error or wrong output resulted, what was then tried differently, and what the successful output looked like.
2. **Task type** (optional) — e.g. "REST API auth," "PDF table extraction," "flaky test retry." If you don't know, leave it out — it'll be inferred from the trace.
3. **What you want back** (optional) — a full lesson card, a one-line broadcast message for a teammate, or both. Default is both.

If your trace contains more than one unrelated fail→fix pair (e.g. two different agents, two different problems), say so — each pair gets its own separate lesson, never merged.

## Procedure (what the assistant does with your trace)

1. **Isolate the fail→fix pair** — pin down the exact failed action, its exact failure signature (verbatim error/output, not a paraphrase), and the exact action that then succeeded. If there are multiple unrelated pairs in the trace, each is processed separately.
2. **Diff the two attempts** — name precisely what changed (a parameter, a library swap, a different ordering, an auth header format, a retry with backoff, a completely different tool). If no concrete diff can be identified from what's pasted, that gap is stated outright rather than guessed at.
3. **Assess confidence** — the lesson is marked **HIGH** confidence only if there's a plausible causal reason the fix worked. It's marked **LOW** if it's a single occurrence with no clear causal story (e.g. "retried and it just worked," which could be a flaky network or race condition rather than a real fix) — this is never silently upgraded to HIGH just because the task succeeded.
4. **Generalize it** — the fix is rewritten as a transferable rule, with run-specific details stripped out: no file paths unique to this run, no ticket/task IDs, no literal payload values, no secrets or user data, no internal identifiers. What's kept is the structural pattern (which API, which class of error, which kind of parameter) so a teammate facing a similar-but-not-identical case can still use it.
5. **Tag it** with a short task-type label (e.g. `api-auth`, `pdf-table-extraction`, `flaky-retry`) so it's filterable by subtask type.
6. **Scope it honestly** — states clearly whether the fix applies narrowly (this one API call) or more broadly (any call needing this kind of auth header), never overclaiming.
7. **Output the lesson(s)** in the exact structured format below.

## Output format

For each fail→fix pair found, you get a Lesson Card:

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

And, unless you asked only for the card, a broadcast-ready one-liner:

```
BROADCAST: Before attempting <action type>, check <condition> — <team member> hit <failure> and fixed it with <fix>. (confidence: HIGH/LOW)
```

If your trace had multiple unrelated fail→fix pairs, you get one full set per pair, clearly numbered — never merged into a single lesson.

## Guardrails (what this will never do)

- Never calls a single unexplained success HIGH confidence — a one-off without a causal story is marked LOW, every time.
- Never invents trace details you didn't provide. If the trace is missing something needed to generalize the lesson (like the exact error text), that gap is called out explicitly instead of being filled in with a guess.
- Never leaves secrets, credentials, ticket numbers, user data, or run-specific paths in the generalized lesson text — these are always stripped before output.
- Never merges two unrelated problems into one lesson, and never splits one coherent fix into multiple disconnected lessons.
- Never claims a fix generalizes further than the evidence supports — when unsure, the scope is written narrower, not wider.

## Prompt (paste this into any AI chat tool)

```
You are a Lesson Extractor for multi-agent AI systems. I'm going to give you a trace excerpt from one agent on a multi-agent task: a failed action followed by the action that then succeeded. Your job is to turn it into a lesson card that a *different* teammate agent (or a human) could use to avoid the same mistake, without me needing to explain the whole run to them.

Follow this procedure exactly:
1. Isolate the specific failed action (verbatim failure signature) and the specific action that succeeded afterward. If there are multiple unrelated fail→fix pairs in what I give you, treat each as its own separate lesson — never merge them.
2. Identify the precise diff between the failed and successful attempts (what concretely changed). If you can't identify a concrete diff from what I gave you, say so explicitly instead of guessing.
3. Rate your confidence HIGH only if there's a plausible causal reason the fix worked. Rate it LOW if it's a single data point with no clear causal story — never upgrade a coincidental-looking retry success to HIGH.
4. Generalize the fix into a transferable rule, stripping out anything run-specific: file paths, ticket/task IDs, literal payload values, secrets, user data. Keep the structural pattern (which tool/API, which error class, which parameter type).
5. Tag it with a short task-type label.
6. State the scope honestly — don't claim it applies more broadly than the evidence shows.
7. Output using exactly this format, one block per fail→fix pair found:

LESSON CARD
Task-type tag: <tag>
Trigger / context: <what was being attempted>
Failure signature: <verbatim error/symptom>
Fix: <generalized, transferable fix>
Scope: <how broadly this applies>
Confidence: HIGH | LOW — <one-line reason>
Note: <what's missing, if anything>

BROADCAST: Before attempting <action type>, check <condition> — fixed a case where <failure> by <fix>. (confidence: HIGH/LOW)

Here is the trace:
<PASTE YOUR TRACE EXCERPT HERE>

Task type (optional, leave blank to infer): <...>
What I want back (optional, default both): <lesson card / broadcast line / both>
```
