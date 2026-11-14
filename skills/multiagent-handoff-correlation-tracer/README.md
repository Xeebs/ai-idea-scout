# Multi-Agent Handoff Correlation Tracer

A self-contained prompt template for diagnosing which agent-to-agent handoff broke a multi-agent LLM run, from a raw, messy log excerpt — no correlation IDs, no JSON conversion, no tool installation required. Paste this whole prompt plus your log into any chat-based AI tool.

## When to use this

Your multi-agent pipeline (a supervisor/worker setup, a task-delegation crew, or a group-chat pattern built with something like LangGraph, CrewAI, or AutoGen/AG2) produced a wrong or broken result. You have a log or trace excerpt — copied from a terminal, a tracing dashboard, or a log file — but nothing in it ties one agent's turn to the next with a shared ID, so you can't tell at a glance *which handoff* between agents is where things went wrong. You want a diagnosis now, from the text you already have, not a new tool to install first.

## What to hand over

Paste, in your message:
1. The raw trace/log excerpt itself — agent turns, tool calls, tool results, timestamps, and any error text. Exactly as captured; it's fine if it's messy, partial, or missing some fields.
2. (Optional) Which framework produced it (LangGraph, CrewAI, AutoGen/AG2, custom), if known.
3. (Optional) What the correct output should have looked like.

## The procedure to follow

1. **Segment** the excerpt into discrete turns: each agent's message, each tool call, each tool result, each error. Identify the speaking agent from explicit labels or strong contextual cues only — if a turn can't be attributed to a specific agent from the text, mark it `[unattributed]` rather than guessing.
2. **Order** the turns by timestamp if present; otherwise fall back to the text's own sequence order, and say so explicitly — don't present sequence order as if it were timestamp-verified.
3. **Mark every handoff** — every point where one agent's output becomes another agent's input (a delegation, a consumed answer, a tool result that gets re-dispatched).
4. **Check each handoff for divergence**: stale or truncated context, a swallowed tool error, a format mismatch between what one agent produced and the next expected, conflicting instructions introduced mid-chain, or a retry that silently dropped earlier state.
5. **Rank findings by evidence strength**:
   - *Direct* — an error or visibly wrong value appears right at, immediately before (the sending side's own state already contradicts an earlier correct answer), or immediately after this handoff.
   - *Circumstantial* — a later turn contradicts an earlier one, implying loss at some handoff in between, without a single line proving which.
   - *Speculative* — a plausible pattern match with no specific line of evidence.
6. **Pick the top candidate.** Confidence is **High** only with Direct evidence, **Medium** for a clean Circumstantial case, **Low** for Speculative-only or if there aren't even two distinct agents' turns to compare.

## Output you should get back

A short report with exactly this shape:

- **Suspected handoff**: which agent handed off to which agent, and roughly where (timestamp or turn number)
- **Confidence**: High / Medium / Low, with a one-line reason
- **Evidence**: the actual quoted lines from your pasted excerpt that support the diagnosis — never a paraphrase presented as a quote, never an invented line
- **Alternate candidate(s)**: only if a second handoff is genuinely close in plausibility
- **What would confirm it**: a concrete next step (e.g., re-run with a correlation ID at that specific handoff, or pull the full untruncated payload at that point)

If the excerpt simply doesn't contain enough distinguishable agent turns to localize anything, the output should say "Insufficient Evidence" and explain what's missing — not force a guess.

## Guardrails to hold the output to

- No "High" confidence without an actual quoted, Direct piece of evidence.
- No invented agent names, timestamps, tool calls, or quoted lines — everything quoted must be verbatim from what you pasted.
- No forced diagnosis when only one agent's turns are distinguishable — it should say so plainly instead.
- No pitching you a tool or product as the answer — the diagnosis itself is the deliverable; a suggestion to add correlation-ID/heartbeat instrumentation belongs only in "what would confirm it," as a forward-looking step, never as a dodge of giving you an actual read on the log you already pasted.
- No treating guessed sequence order as if it were verified by timestamps.

This is a one-shot diagnostic for a run that already failed — it doesn't replace adding real instrumentation (correlation IDs, per-wave heartbeats) if these failures keep recurring; it just gets you an answer today, from the log you already have.
