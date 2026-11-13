# Agent Memory Decision-Provenance Trace

A paste-into-any-AI-chat-tool prompt for answering one question after an AI agent does something wrong: **"why did it do this, and what did it believe at the time?"** It reconstructs the chain of memory writes, sessions, and tool outputs that led to one flagged action, using only logs you already have — it does not connect to any live system, does not monitor anything going forward, and cannot manufacture a chain if nothing was ever logged.

## When to use this

Use it right after a consequential, hard-to-reverse AI agent action turns out to be wrong or surprising — a coding agent merged a bad PR, a support agent took a wrong account action, a workflow agent sent a message based on a fact that was never true. You want to know what memory, session, or context fed that decision, and you have some combination of a memory-store export, chat/session transcripts, and tool-call logs already sitting around, just not organized into an answer.

Don't use it to decide who is allowed to read or write a given memory (that's a different problem — access control/governance) and don't use it to debug something still in progress (it only works backward over logs from before the flagged action already happened).

## What to hand it

Before running the prompt below, gather:

1. **The flagged action** — what the agent did, roughly when, and why it's wrong/surprising. Example: "Agent merged PR #412 at 14:02 UTC citing a product requirement that was actually dropped two weeks earlier."
2. **A memory-store export or write log** covering the period before the action — any format: a mem0/Letta/Zep export, a JSON/CSV dump of writes with timestamps and session IDs, or a manually kept changelog. If it has no timestamps or session IDs, say so — the trace will be weaker but still worth running.
3. **Session transcripts or chat logs**, if you have them, for sessions that plausibly fed the action. These let a memory write be traced back further to the tool output, user message, or inference that actually produced it.
4. **Tool-call/tool-output logs**, if the agent calls external APIs/tools — needed to tell a verified fact (confirmed by an authenticated, trusted API) from an untrusted one (an unauthenticated scrape or unverified input).
5. Optional: a lookback window, and a short list of which of your sources are always trusted vs. never trusted (e.g. "our internal ticketing API = trusted; raw web search results = never trusted").

If you don't have item 1 (a description of the flagged action) or item 2 (some kind of write log), this exercise can't run — there's nothing to trace back from. Missing items 3–5 just means a thinner chain, not a blocker.

## The prompt

Paste this into any AI chat tool along with your logs:

```
You are performing a forensic decision-provenance trace on an AI agent's memory
and session logs. I will give you: (1) a flagged action the agent took that
turned out wrong or surprising, (2) a memory-write log/export, and optionally
(3) session transcripts and (4) tool-call logs.

Do the following, in order:

1. Restate the flagged action in one line with its timestamp and session/run ID
   if known. If no session ID is given, infer the nearest bounding session from
   the transcripts and say explicitly that it's inferred.

2. From the memory write log, list every write that happened before the flagged
   action (within my stated lookback window, or all available history if I
   didn't give one) whose content plausibly relates to the action's stated
   justification. Don't include writes with no plausible textual link.

3. For each candidate write, use the session transcripts/tool logs to find what
   produced it: a tool-call response, a user message, a prior memory read
   combined with model inference, or nothing findable in what I gave you.

4. Keep walking backward from each of those sources the same way, until you hit
   either (a) an explicit user-provided fact, (b) a tool/API response you can
   classify, or (c) a point where the logs just don't say. Mark (c) as
   UNKNOWN PROVENANCE and stop that branch there — do not guess.

5. Classify every node in the chain with exactly one of these three labels:
   - VERIFIED: traced to an explicit, authenticated/trusted tool or API
     response, or a direct, attributable statement from a person.
   - INFERRED: the agent derived or summarized this itself from other
     memory/context, with no fresh external confirmation at that step.
   - UNTRUSTED: traced to an unauthenticated scrape, third-party/web content,
     or input I've told you is unverified.
   Never mark something VERIFIED just because it reads confidently — only
   because an actual trusted source is logged for it.

6. Assemble the full chain in chronological order, root cause first, flagged
   action last, with timestamp, session ID, what happened, and source
   classification at every link.

7. For every place the chain hit UNKNOWN PROVENANCE, say exactly what kind of
   log or instrumentation gap caused it (no session boundary logged, no
   tool-call log retained, no transcript provided for that session).

8. Before giving me the final answer, check yourself: can you point to a
   specific line in what I gave you for every single node in the chain? If
   not, delete that node or relabel it UNKNOWN PROVENANCE instead of asserting
   it.

Give me the result in this exact format:

# Decision-Provenance Trace — <flagged action, one line>

## Flagged action
<what happened, when, which session/run>

## Provenance chain
| Timestamp | Session/run | Event | Source classification | Note |
|---|---|---|---|---|

## Root cause assessment
<1-3 sentences>

## Gaps — unknown provenance
- <node> — chain breaks here because <specific missing log type>

## Recommendations to close the gap next time
- <specific instrumentation change>

Here is my flagged action, memory log, and any transcripts/tool logs:

<PASTE YOUR MATERIALS HERE>
```

## Guardrails to keep in mind

- This is a one-time manual reconstruction from logs you already have — it does not run continuously and cannot retroactively create logs that were never kept. If your logs are too thin, expect (and accept) a thin, honestly-labeled partial chain rather than a confident-sounding fabricated one.
- It never decides who is *allowed* to see a memory — only how a specific past decision actually came to be.
- Treat any node the model can't tie to an actual line in your pasted logs as suspect — ask it to show you where that node came from, and if it can't, discard that part of the chain.
- If you want this to run automatically on every future agent action instead of as a one-off, that's a different, bigger build (an always-on provenance-tagging wrapper around your memory backend) — this prompt is only the forensic, after-the-fact version.
