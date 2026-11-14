---
name: multiagent-handoff-correlation-tracer
description: Given a pasted, unstructured trace/log excerpt from a failed multi-agent LLM run (LangGraph, CrewAI, AutoGen/AG2, or similar), reconstructs the handoff chain and reports the most likely agent-to-agent handoff that caused the failure, with a confidence level and cited evidence lines. Use when a multi-agent pipeline failed and the logs have no correlation IDs tying agents' turns together.
---

# Multi-Agent Handoff Correlation Tracer

## When to use this

A multi-agent LLM pipeline (supervisor/worker, task-delegation, or group-chat pattern) produced a wrong or broken result, and the only evidence is a raw log or trace excerpt — console output, a copied Langfuse/LangSmith panel, or framework stdout — with no shared correlation ID linking one agent's output to the next agent's input. The engineer needs to know *which handoff* (agent X's output becoming agent Y's input) is where things went wrong, without first standing up instrumentation. This is a one-shot forensic read of an already-failed run, not a monitoring or prevention tool — it never proposes buying or installing something as a substitute for giving a real answer from the pasted text first.

## Inputs

**Data source**: Manual — the user pastes the raw trace/log excerpt itself: the sequence of agent turns, tool calls, messages, timestamps, and any error text from the failed run. No API, no export format, no JSON conversion required — paste exactly what you have, console-copied or log-tailed, even if it's messy or partial.

Also helpful but optional:
- Which framework produced the run (LangGraph, CrewAI, AutoGen/AG2, custom) — helps recognize framework-specific turn markers (e.g., LangGraph node names, CrewAI task/agent role labels).
- What the correct final output should have looked like, if known.

## Procedure

1. **Segment the excerpt into turns.** Split the pasted text into discrete events: each agent's message, tool call, tool result, and any explicit error/exception. Identify the speaking agent for each turn from explicit labels (role names, node names, "Agent:" prefixes) or, if unlabeled, from strong contextual cues (first-person framing, distinct tool access, distinct task description) — never invent a label that isn't textually supported; mark an unattributable turn as `[unattributed]` rather than guessing an agent name.
2. **Order the turns.** Use timestamps if present. If timestamps are missing, sparse, or out of order, fall back to text sequence order, and say explicitly in the report that ordering is sequence-based, not timestamp-verified.
3. **Mark handoff points.** A handoff is any place where one agent's output (message, tool result, or state) becomes the next agent's input — e.g., supervisor delegates to a worker, one agent's answer is quoted/consumed by another, a tool result returns to an orchestrator that then re-dispatches. List every handoff found, in order.
4. **Check each handoff for evidence of divergence.** At each handoff, compare what the receiving agent appears to have been given against what it appears to have needed: look for truncated or stale context (a field value that doesn't match an earlier update), a dropped tool-error that should have halted the chain but didn't, a format mismatch (one agent expects structured data, gets prose or vice versa), conflicting instructions introduced mid-chain, or a retry/loop that silently discarded earlier state.
5. **Rank candidate failure points by evidence class**, strongest first:
   - **Direct** — an error, contradiction, or visibly wrong value appears in the text *at, immediately before (e.g., the sending agent's own state already contradicts an earlier correct answer), or immediately after* this handoff.
   - **Circumstantial** — a later turn's output is inconsistent with what an earlier turn established, implying something was lost at an intervening handoff, but no single line proves it.
   - **Speculative** — a plausible pattern-match (e.g., "this looks like the stale-context pattern") with no textual evidence pinned to a specific line.
6. **Select the top candidate.** Assign confidence: **High** only if a Direct-class handoff exists; **Medium** for a clear Circumstantial case; **Low** if the strongest finding is Speculative, or if the excerpt doesn't contain at least two distinct identifiable agent turns (in that case, say so plainly instead of forcing a diagnosis).
7. **Write the report** per the Output format below, quoting the actual lines that support the top candidate (and any close alternate).

## Output format

```
## Most Likely Failure Point

**Suspected handoff**: <Agent X> → <Agent Y>, at <timestamp or turn/step reference from the excerpt>
**Confidence**: High | Medium | Low — <one-line reason tied to the evidence class from step 5>

**Evidence**:
> <quoted line(s) from the pasted excerpt, verbatim>
> <quoted line(s), verbatim>
<1-2 sentences connecting the quoted lines to the divergence>

**Alternate candidate(s)** (only if genuinely close):
- <Agent A> → <Agent B> at <ref> — <why it's plausible but ranked below the top candidate>

**What would confirm it**: <concrete next step — e.g., "re-run with a correlation ID stamped at this specific handoff" or "check agent Y's full input payload at <ref>, which this excerpt truncates">
```

If the excerpt lacks enough agent-attributable turns to localize anything, output instead:
```
## Insufficient Evidence
<what's missing — e.g., "only one agent's turns are distinguishable in this excerpt; need at least one more agent's output to identify a handoff."> 
```

## Guardrails

- Never assign **High** confidence without a Direct-class, quotable piece of evidence in the report.
- Never invent an agent name, timestamp, tool call, or quoted line that isn't actually present in the pasted excerpt — quote verbatim, don't paraphrase as if it were a quote.
- Never force a handoff diagnosis when the excerpt contains only one identifiable agent's turns — report "Insufficient Evidence" instead.
- Never recommend installing, buying, or adopting an external tool as the answer itself — this skill's job is to give the diagnosis from what was pasted. A pointer to add instrumentation (correlation IDs, heartbeat logging) belongs only in "What would confirm it," as a follow-up, not as a substitute for a present diagnosis.
- Never treat sequence order as timestamp-verified order — flag the difference explicitly when timestamps are missing or unreliable.
