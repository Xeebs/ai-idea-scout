# Cross-Framework Trace Correlator

Paste this whole prompt into any AI chat tool, then attach or paste your trace export files when asked. No installation, no connectors, no access to this repo required.

## What this is for

Your multi-agent request crossed a framework boundary — maybe a LangGraph orchestrator called into a CrewAI crew, or a CrewAI agent handed off to a raw tool-use loop — and something went wrong. You pulled a trace export from each framework involved (from Phoenix, Langfuse, LangSmith, Helicone, or a raw OpenTelemetry/debug log dump), but they're separate files with no shared trace ID, because nobody had live trace-propagation wired up between these two frameworks. You need to reconstruct what actually happened across the full chain, from the evidence you already have, without re-running the request.

This is a one-time diagnostic exercise, not a fix. If this keeps happening on the same pair of frameworks, the real fix is installing a context-propagation shim so future traces come out already stitched — this prompt just gets you through the incident in front of you.

## What you need before you start

1. **Two or more trace export files** (or pasted JSON/log excerpts) — one per framework involved in the request. Each one must be clearly labeled with which framework produced it (e.g. "LangGraph export" / "CrewAI export").
2. **A one-line description** of what the request was supposed to do and where you think it broke (e.g. "the orchestrator calls a research crew and the response came back empty").
3. **Optional, but helps a lot**: the approximate wall-clock time the request happened, and which timezone/epoch each export's timestamps use, if it isn't obvious from the file.

Data source note: this is entirely manual — you paste or upload the files yourself. There is no automatic connector to any observability backend here; the whole premise is that these traces were captured separately and were never linked at the source.

## The prompt

```
You are reconstructing a single correlated timeline from multiple separately-exported
agent-framework trace files that cover the same failing multi-framework request. I will
give you one trace export per framework, each labeled with its source framework, plus a
one-line description of what the request was supposed to do and where it broke.

Follow this procedure exactly:

1. Parse each file independently. For every span, extract: the framework label, the
   span/operation name, start and end timestamps (or duration), parent-span id if present,
   and any available input/output payload, tool arguments, tool results, or error text.

2. Normalize the clock. Convert all timestamps to the same timezone/epoch. If the files
   use different epochs, or no epoch is stated, ask me rather than silently assuming UTC.
   If the normalized timestamps look implausible across files (e.g. clear sign of clock
   skew), flag it explicitly and say ordering across that boundary is unreliable.

3. Find candidate handoff points between frameworks, in this priority order:
   a. Payload match (HIGH confidence) — one span's output/return value appears, verbatim
      or near-verbatim, as another span's input/argument. Quote the matched text.
   b. Timestamp adjacency (MEDIUM confidence) — one span ends right around when a span in
      the other framework begins, with no payload match found.
   c. Pure temporal overlap with no content link (LOW confidence) — spans merely occur in
      the same rough window with nothing else connecting them.

4. Assemble a single merged, chronological timeline across all the files, with each row
   tagged by framework and each cross-framework link tagged with its confidence level.

5. Identify the hop(s) in that timeline nearest to where I said the request broke, and
   explain why, using evidence from the timeline itself — not a guess made independently
   of it.

6. List every inferred (non-payload-matched) link explicitly as a caveat, and list every
   span you could not place in the merged timeline at all ("orphan spans").

Produce your answer as a single markdown report with exactly these sections, in order:

1. Request summary — one line restating what I said the request should do and where it broke.
2. Merged timeline — a table: Time | Framework | Span/Operation | Duration | Link to
   previous hop (confidence).
3. Handoff points — for each cross-framework boundary found, 1-3 sentences naming the two
   spans, the confidence level, and the evidence (quote matched payload text if that's
   what grounded it).
4. Likely fault point — the hop(s) closest to where I said things broke, with reasoning
   tied to the timeline.
5. Caveats and unresolved spans — every inferred link, every orphan span, and any
   clock-skew warning.
6. Next step — one line noting that if this framework pair keeps producing incidents like
   this, installing live trace-context propagation for that pair would remove the need to
   do this reconstruction by hand each time.

Rules you must follow:
- Never state a handoff is certain when it's only timestamp-adjacency or overlap-based —
  always carry the confidence label through to the final report.
- Never invent a payload match — only cite one if the matched text is actually present
  (and quoted) in both files.
- Never silently assume a timezone/epoch when the files don't state one or disagree with
  each other — ask me, or clearly flag the assumption and its risk.
- Never drop an orphan span from the report — list it as unresolved instead.
- Don't present this reconstruction as equivalent to a real propagated trace ID; it's an
  inference from after-the-fact evidence, and the report must say so.
- If I give you only one framework's trace file, tell me you need at least two
  framework-tagged files to do cross-framework correlation — don't analyze one file as if
  it were multi-framework.

Here is what was supposed to happen and where it broke:
<one-line description>

Here are the trace export files, each labeled with its framework:

<paste or attach trace file 1, labeled>

<paste or attach trace file 2, labeled>

<paste or attach additional trace files if more than two frameworks were involved>
```

## What you'll get back

A markdown report with six sections: a one-line request summary, a merged timeline table spanning every framework, a list of the handoff points found (with confidence levels and quoted evidence), the most likely fault point tied to what you said broke, an explicit caveats list of every inferred link and unresolved span, and a one-line suggestion about whether it's time to stop doing this by hand.

## Limits to know going in

- This cannot create certainty that doesn't exist in your data. If your exports don't carry payload content, most links will land at medium or low confidence — that's a correct, honest answer, not a failure of the prompt.
- If your trace files don't share a clear, stated timezone or epoch, expect to be asked a clarifying question before the timeline comes back.
- This only reconstructs what's recoverable from the files you provide. It cannot recover spans that were never exported in the first place.
