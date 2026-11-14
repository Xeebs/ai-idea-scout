---
name: compaction-invariant-pinning-library
description: Designs a per-workflow "invariant pinning" scheme for a long-running agent's context compaction — what must survive every summarization pass (already-tried approaches, hard constraints, key decisions) vs. what's safe to lose. Use before wiring in a compaction hook, or after noticing an agent re-attempts something it already tried and failed.
---

# Compaction Invariant Pinning Design

## When to use this
A team or solo developer is running (or about to run) a long-horizon autonomous agent — a coding agent, research agent, or multi-hour task runner — that hits automatic context compaction more than once per session (Claude Code's auto-compact, a LangGraph checkpointer summarization step, or a custom summarizer in a long agent loop). They've either noticed the agent re-attempt a fix it already tried and failed on a few compactions ago, or they want to get ahead of that failure before it happens. This skill is the one-shot design pass that decides, for this specific workflow, what gets permanently pinned outside every future compaction versus what's fine to summarize away.

Do not reach for this skill to debug a single transcript where something else obviously went wrong (a tool outage, a bad prompt) — it's for designing a reusable classification policy for a recurring compaction pattern, not a one-off incident review.

## Inputs
**Data source**: Manual — the user pastes a description of the agent's task/workflow and, ideally, a sample transcript excerpt or representative turns showing content near a compaction boundary (attempted fixes, errors hit, constraints stated, decisions made). (Context: the parent idea this skill comes from is an always-on middleware library classified as Data Sources: Connected — it reads the live session/context state directly via the host framework's own compaction hook, e.g. Claude Code's PreCompact hook or LangGraph's checkpointer API. This skill is the design/review half of that idea, not the live middleware: it works from whatever the user pastes in this session, not a live connection, so for this skill specifically the input is Manual.)

To run this skill, provide:
1. **Workflow description** — what the agent does, the host framework (Claude Code, LangGraph, custom loop), typical session length, and roughly how many compactions a session hits.
2. **Compaction config, if known** — the summarization trigger/threshold and prompt, or "default/unknown" if you haven't customized it.
3. **A transcript excerpt or representative turns** (strongly recommended, not strictly required) — actual lines showing attempted fixes and their outcomes, stated constraints, or decisions made, ideally spanning a point where compaction fired. If none is available, say so explicitly and the output will be marked provisional.

## Procedure
1. **Read the workflow description** and classify the task domain (coding agent, research/analysis agent, data pipeline, other) and session shape (how long it runs, how many compactions per session are expected).
2. **If a transcript/turns were provided**, extract three candidate lists verbatim from the text (never invent content not present):
   - **Tried-and-outcome items** — a distinct approach, fix, or query the agent attempted, plus whether it succeeded, failed, or was inconclusive.
   - **Hard constraints** — requirements stated to hold for the whole session (e.g. "must stay on Python 3.11," "never touch files outside `src/`," a budget or deadline).
   - **Key decisions** — choices that later steps depend on, with the stated or inferable reason (e.g. "chose Postgres over SQLite because of concurrent writes").
   If no transcript was given, generate illustrative examples for each list from the workflow description alone and label them clearly as hypothetical, not extracted.
3. **Classify every candidate** into exactly one bucket:
   - `PIN` — must survive every future compaction untouched (a failed approach that could otherwise be re-attempted; a hard constraint that's cheap to violate if forgotten; a decision other steps depend on).
   - `SUMMARIZE` — fine to compress normally; the gist survives even if exact wording doesn't (routine tool output, exploratory reasoning that led nowhere consequential, narrative color).
   - `DROP` — adds no value even summarized (acknowledgments, repeated boilerplate, content fully superseded by a later `PIN` item).
4. **Flag ambiguous or time-sensitive items separately** — a "tried and failed" item whose failure reason could become invalid later (e.g. "API returned 500" — might work on retry) should still be `PIN`ned but tagged `REVIEW-ON-RETRY` rather than treated as permanent, so the eventual implementation doesn't block a fix that would now succeed under changed conditions.
5. **Check every failed attempt for a later superseding success on the same approach.** If the transcript shows the same approach retried later (often after a decision or helper fix) and that later attempt succeeded, tag the original failure `SUPERSEDED` instead of a standing "already tried, don't retry" block — keep it in the pinned schema as historical context (useful if the same failure mode resurfaces elsewhere) but never let it read as a current blocker on the now-working approach.
6. **Draft the pinned-slot schema** for this workflow: a short structured template (field names + one example row per field, drawn from the actual `PIN` items found) that the pinned slot would hold going forward.
7. **Recommend a token budget** for the pinned slot: estimate based on expected `PIN` volume over the stated session length (rough count of tried-items/constraints/decisions per compaction cycle × expected cycles), expressed as both an absolute token ceiling and a rule for what gets evicted first if that ceiling is hit (oldest, lowest-severity, or `REVIEW-ON-RETRY`-tagged items first — recommend one and say why for this workflow).
8. **Write the classification rules in plain, reusable language** — a short rule-of-thumb per bucket that a human or a later rule-based/cheap-model classifier could apply consistently on every future compaction event for this same workflow, not just for the sample provided.
9. **State explicitly whether the output is validated or provisional** — provisional if no real transcript was supplied, validated-against-sample if one was, and name what to check once the scheme runs against a live compaction event.

## Output format
A markdown design report with these sections, in order:
1. **Workflow summary** — one paragraph: domain, framework, session shape.
2. **Extracted candidates** — three labeled lists (tried-and-outcome, hard constraints, key decisions), each item tagged `PIN` / `SUMMARIZE` / `DROP`, and `REVIEW-ON-RETRY` where applicable. Mark the whole section "hypothetical (no transcript provided)" if no sample was given.
3. **Pinned-slot schema** — the structured template with one real example row per field.
4. **Token budget** — the recommended ceiling, the reasoning, and the eviction-priority rule.
5. **Classification rules** — the plain-language, reusable rule set, one rule per bucket.
6. **Validation status and next step** — provisional/validated, and the single most important thing to check once this scheme runs against a real compaction event.

## Guardrails
- Never pin everything "to be safe" — that recreates the exact context bloat this scheme exists to prevent; every `PIN` recommendation must trace to a specific reason it would cause a repeat failure or a dropped constraint if lost, not a blanket default.
- Never fabricate transcript content, tool names, or outcomes that weren't in the provided material — when no transcript is given, generated examples must be clearly labeled hypothetical, not presented as findings.
- Never pin content that changes frequently or is only true at one moment (current file contents, a timestamp, a live variable value) — only pin stable facts: outcomes, constraints, and decisions, which stay true regardless of when they're read.
- Never claim this design has been measured for an actual repeated-failed-approach rate — this skill produces a design and a hypothesis, not a validated eval result; say so plainly in the output.
- Never present this as the live middleware itself — this skill is a one-shot design/review aid. If the user wants the always-on hook that actually enforces this at runtime, say clearly that building/wiring the compaction-hook library is a separate implementation step, not something this skill does.
