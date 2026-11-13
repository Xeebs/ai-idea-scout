---
name: agent-memory-decision-provenance-trace
description: Forensic, one-shot reconstruction of the memory-write/session chain behind a single flagged AI agent action, from whatever logs/transcripts/memory dumps the team already has — classifying each upstream fact as verified, inferred, or untrusted-tool-output, and marking where the chain goes dark. Use after something an agent did (a bad merge, a wrong account action, an incorrect message) needs a "why did it do this, and what did it know" answer, not for live monitoring or for who-may-read-what access control.
---

# Agent Memory Decision-Provenance Trace

## When to use this

Reach for this immediately after a consequential, hard-to-reverse agent action turns out to be wrong or surprising — a coding agent merged a PR based on a stale requirement, a support agent took an account action on outdated account state, a workflow agent sent a message based on a fact that was never true — and someone needs to answer "why did it do this, and what did it believe at the time" using only logs, transcripts, and memory-store exports that already exist. This is a post-incident forensic read of data you already have, not a live monitoring dashboard and not an always-on recorder — if nothing was logged in the first place, this skill cannot manufacture a chain, and it will say so rather than guess.

Do not reach for this to decide who is allowed to read or write a given memory (that's an access-control/governance question, a different tool entirely) and do not reach for it to debug a live, in-progress failure — it only reasons over logs from before the flagged action.

## Inputs

**Data source**: Manual — the user pastes or uploads whatever logs/exports they already have; this skill has no live connector into mem0, Letta, Zep, or any other memory backend and does not call any API. Specifically, collect:

1. **The flagged action itself** — what the agent did, roughly when, and why it's considered wrong or surprising (e.g. "merged PR #412 at 14:02 UTC citing a requirement that was actually dropped two weeks earlier").
2. **A memory-store export or write log covering the lookback window** — whatever format exists: a mem0/Letta export, a plain JSON/CSV dump of writes with timestamps and session IDs, or even a manually kept changelog. If the export has no timestamps or session IDs, say so up front — the trace will be weaker.
3. **Session transcripts or chat logs** for the sessions that plausibly fed the action, if available — these are what let a memory write be traced back further to the tool output, user message, or model inference that produced it.
4. **Tool-call/tool-output logs**, if the agent calls external tools/APIs — needed to classify a fact as verified (came from an authenticated, trusted API response) versus untrusted (unauthenticated scrape, third-party content, unverified user input).
5. Optional: a **lookback window** (default: all available logs) and a list of **known-trusted sources** (e.g. "our internal ticketing API is always verified; web search results are never verified") to speed up classification.

If input 1 or 2 is missing entirely, do not proceed — ask for them; without a described action and some write log there is nothing to trace. Inputs 3–5 missing are not blockers — note the chain will be partial and proceed with what exists.

## Procedure

1. **Pin the target.** Restate the flagged action in one line with its timestamp and the session/agent-run ID it occurred in, if known. If no session ID is given, infer the nearest bounding session from the transcripts and flag that inference explicitly.
2. **Build the candidate set.** From the memory export, list every write that occurred before the flagged action and within the lookback window whose content plausibly relates to it (keyword/semantic overlap with the action's stated justification). Do not include writes with no plausible textual link — padding the chain with irrelevant writes defeats the point.
3. **Walk back one hop per candidate.** For each candidate write, find in the session transcripts/tool logs what produced that specific write: a tool-call response, a user message, a prior memory read combined with model inference, or nothing findable in the provided logs.
4. **Recurse until you hit a root or a gap.** Repeat step 3 on whatever produced each hop, continuing backward until you reach: (a) an explicit user-provided fact, (b) a tool/API response you can mark verified or untrusted, or (c) a point where the logs simply don't say — mark that node `UNKNOWN PROVENANCE` and stop recursing on that branch.
5. **Classify every node's source**, using exactly three labels:
   - `VERIFIED` — traced to an explicit, authenticated/trusted tool or API response, or a direct, attributable user statement.
   - `INFERRED` — the agent derived or summarized this itself from other memory/context, with no fresh external confirmation at that step.
   - `UNTRUSTED` — traced to an unauthenticated scrape, third-party/web content, or user input the team has flagged as unverified.
   Never assign `VERIFIED` on confidence of tone or phrasing alone — only on an actual logged trusted source.
6. **Assemble the chronological chain**, root-to-action, noting at each link the timestamp, session ID (or "inferred: <nearest bounding session>"), what was written/said, and its source classification.
7. **Call out every break.** Anywhere step 4 stopped at `UNKNOWN PROVENANCE`, state plainly what log/instrumentation gap caused it (no session boundary logged, no tool-call log retained, transcript not provided) so the team knows what to add before the next incident.
8. **Self-check before returning**: every node in the chain cites a specific log line/timestamp/session ID actually present in the provided materials — if you cannot point to where in the user's pasted data a node came from, delete it or mark it `UNKNOWN PROVENANCE` instead of asserting it.

## Output format

```markdown
# Decision-Provenance Trace — <flagged action, one line>

## Flagged action
<what happened, when, which session/run>

## Provenance chain
| Timestamp | Session/run | Event (write / tool call / user input) | Source classification | Note |
|---|---|---|---|---|

(chronological, root cause first, flagged action last)

## Root cause assessment
<1-3 sentences: the earliest identifiable fact/event that set this chain in motion, and its classification>

## Gaps — unknown provenance
- <node> — chain breaks here because <specific missing log type>

## Recommendations to close the gap next time
- <specific instrumentation: e.g. "log session ID on every memory write", "retain tool-call response bodies for 90 days">
```

## Guardrails

- Never invent a log entry, timestamp, session ID, or tool response that isn't present in what the user provided — if the provided materials don't cover a step, mark it `UNKNOWN PROVENANCE`, never a plausible-sounding guess.
- Never classify a node `VERIFIED` without pointing to the specific trusted source in the logs that justifies it; default to `INFERRED` or `UNTRUSTED` when in doubt.
- Never present this as a live or automatic system — it is a one-time manual reconstruction from whatever logs exist at the moment it's run; if the team wants this to run automatically going forward, that's the always-on provenance-recorder project, a different build, not this skill.
- Never fold access-control or "who may read this memory" reasoning into the trace — this skill only answers "how did this happen," not "who was allowed to see it."
- If the provided logs lack session boundaries or timestamps entirely, say explicitly that full reconstruction is not possible and only produce whatever partial chain the available text actually supports — do not pad a thin trace to look complete.
