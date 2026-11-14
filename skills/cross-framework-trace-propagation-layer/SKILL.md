---
name: cross-framework-trace-propagation-layer
description: Reconstructs a single correlated timeline from two or more separately-exported agent-framework trace files (e.g. one LangGraph export, one CrewAI export) covering the same failing multi-framework request, so you can see the likely call order and handoff points without live trace-ID propagation installed.
---

# Cross-Framework Trace Correlator

## When to use this
A multi-agent request crossed a framework boundary (e.g. a LangGraph node called into a CrewAI crew, or a CrewAI agent dropped into a raw tool-use loop) and something went wrong — a timeout, a wrong answer, a dropped tool call. You have one export file per framework (from Phoenix, Langfuse, LangSmith, Helicone, a raw OTel collector dump, or a framework's own debug log), each covering only its own side of the request, and no shared trace ID links them because live propagation middleware was never installed. You need to understand what actually happened across the full chain without re-running the request.

This is a one-off, after-the-fact diagnostic task. It is not a substitute for installing live cross-framework trace propagation — if this keeps happening on the same framework pair, that's the signal to build the always-on middleware instead of re-running this skill every incident.

## Inputs
**Data source**: Manual — the user pastes or uploads the separate trace export files (JSON/OTel exports from Phoenix, Langfuse, LangSmith, Helicone, or a raw framework debug log), each one explicitly tagged with which framework and which run/request it came from. Nothing is fetched automatically; there is no connector for this because the whole point is these traces were never linked at capture time.

Required from the user:
1. Two or more trace export files (or pasted JSON/log excerpts), each labeled with its source framework (e.g. "LangGraph export", "CrewAI export").
2. A one-line description of what the request was supposed to do and roughly where it went wrong (e.g. "orchestrator calls a CrewAI research crew, response came back empty").
3. Optional but valuable: approximate wall-clock time of the request and the timezone/epoch each export uses, if not obvious from the file.

If any export is missing span-level timestamps entirely, say so before proceeding — correlation without timestamps degrades to pure ordering-by-content-match, which must be flagged as low confidence throughout.

## Procedure
1. **Parse each file independently.** For every span found, extract: framework label (from the file tag), span/operation name, start timestamp, end timestamp (or duration), parent-span id if present, and any input/output payload or attribute text available (prompts, tool args, tool results, error messages).
2. **Normalize the clock.** Convert all timestamps to the same timezone/epoch. If the files use different epochs or no epoch is stated, ask the user rather than silently assuming UTC. If normalized timestamps across files look implausible (e.g. one framework's whole trace falls fully *inside* a single span of another with no plausible call relationship), explicitly flag likely clock skew and note that ordering is unreliable for that boundary.
3. **Find candidate handoff points**, in this priority order:
   a. **Payload match (high confidence)** — the output/return value/final text of a span in framework A appears (verbatim or near-verbatim) as the input/argument of a span in framework B. This is the strongest evidence of an actual call boundary.
   b. **Timestamp adjacency (medium confidence)** — framework A's span ends at roughly the moment framework B's span begins (within a plausible scheduling gap, e.g. under a few hundred ms to a few seconds depending on what's typical in the data), with no payload match found.
   c. **Pure temporal overlap with no content link (low confidence)** — spans merely occur in the same rough window with nothing else connecting them. Report these as possible but unconfirmed.
4. **Assemble the merged timeline** — a single chronological sequence across all files, each row tagged with its framework, with handoff points marked and their confidence level stated.
5. **Identify the likely fault point** relative to the user's one-line description of what went wrong — which hop in the merged timeline is nearest to where things diverged from expected behavior (e.g. the handoff where a payload went missing or an error first appears).
6. **Write the caveats explicitly** — list every inference that rests on timestamp adjacency or temporal overlap rather than a payload match, and list any span that could not be placed in the merged timeline at all (orphan spans).

## Output format
A single markdown report with these sections, in order:

1. **Request summary** — one line restating what the user said the request was supposed to do and where it broke.
2. **Merged timeline** — a table: `Time | Framework | Span/Operation | Duration | Link to previous hop (confidence)`.
3. **Handoff points** — for each cross-framework boundary found, 1-3 sentences naming the two spans involved, the confidence level, and the evidence (quote the matched payload text if that's what grounded it).
4. **Likely fault point** — the hop(s) closest to where the user said things went wrong, with reasoning tied to the timeline, not a guess made independently of it.
5. **Caveats and unresolved spans** — every inferred (non-payload-matched) link, every orphan span, and any clock-skew warning raised in step 2.
6. **Next step** — one line noting that if this framework pair keeps producing cross-boundary incidents, installing live trace-context propagation for that specific pair (shared W3C trace ID carried across the call) would remove the need to run this reconstruction manually each time.

## Guardrails
- Never state a handoff is certain when it's only timestamp-adjacency or overlap-based — always carry the confidence label through to the final report.
- Never invent a payload match — only cite a payload link if the matched text is actually present (and quoted) in both source files.
- Never silently assume a timezone or epoch when the files don't state one or disagree — ask, or clearly flag the assumption made and its risk.
- Never treat an orphan span (one that can't be placed in the merged timeline with any confidence) as absent from the report — list it explicitly as unresolved rather than dropping it.
- Do not present this reconstruction as equivalent to a true propagated trace ID — it is an inference from after-the-fact evidence, not ground truth, and the report must say so.
- If fewer than two distinct framework-tagged trace files are provided, this skill cannot do cross-framework correlation — say so rather than analyzing a single file as if it were multi-framework.
