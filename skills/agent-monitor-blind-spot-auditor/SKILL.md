---
name: agent-monitor-blind-spot-auditor
description: Reviews a described agent-monitoring architecture (what gets sampled, when, and how monitor/agent isolation is enforced) against the METR/Redwood-derived blind-spot taxonomy — compaction gaps, end-of-task-only sampling, monitor/agent coupling — and returns a scored checklist with specific gaps and fixes. Use before shipping or trusting a new or existing agent-monitoring layer, especially one with no prior external red-team.
---

# Agent Monitor Blind-Spot Auditor

## When to use this
A team is about to ship (or already runs) a monitoring/guardrail layer over a production LLM agent — a sampler, judge-model reviewer, or policy checker sitting alongside an agent loop — and wants to know whether that monitor has structural blind spots before an incident surfaces them, the way METR and Redwood Research's red-team of OpenAI's internal agent-monitoring system found in a three-week manual engagement (published 2026-10-22; a second METR red-team of Anthropic's monitoring on 2026-03-26 found the same category of gaps at a different lab). This skill is the one-shot design-review substitute for that engagement: it works from a written description of the architecture, not live trace data, so it's usable before any instrumentation exists or as a quick gut-check on an existing one.

Do not reach for this skill to debug a specific incident with a known root cause (that's a post-mortem, not an architecture review), and do not use it as a substitute for actually measuring coverage against real traces once they exist — this is the design-time check, not the continuous production auditor.

## Inputs
**Data source**: Manual — the user describes their monitoring architecture in prose/diagram/config form (what triggers a monitor check, what counts as a "monitored action," how context-compaction or summarization is handled, and how the monitor's own execution is isolated from the agent it watches). There is no connector: this skill works from a design description, not live telemetry.

To run this skill, provide:
1. **What gets sampled and when** — e.g., every tool call, only end-of-task, a fixed percentage, risk-triggered only.
2. **How context compaction/summarization is handled** — does anything happen to the monitor's visibility when the agent's context gets compacted, truncated, or summarized mid-task?
3. **Monitor/agent isolation** — does the monitor run as a fully separate process/model with no shared mutable state with the agent, or does the agent have any way to see, predict, or influence when/whether it's being watched (shared timing signals, shared logs the agent can read, the agent choosing its own action granularity)?
4. **Optional**: any existing eval/test coverage numbers, or a sample transcript, to anchor the review in something concrete rather than pure description.

If any of the four aren't described, say so explicitly and score that category `UNKNOWN` rather than assuming a safe default.

## Procedure
1. **Classify sampling scope.** From the description, determine what fraction of agent actions are structurally eligible to ever be checked, versus what fraction actually gets a monitor look. Flag explicitly if monitoring is end-of-task-only, periodic/sampled rather than per-action, or risk-triggered on a heuristic the agent itself can influence.
2. **Audit the compaction/summarization path specifically.** This is the single highest-value check: ask whether a context-compaction, truncation, or summarization event ever happens *without* a corresponding monitor checkpoint on the actions that occurred before it. METR's report found this exact pattern caused the bulk of the ~10% unmonitored-eligible-traffic gap. If the user's description doesn't mention compaction handling at all, treat that as a gap, not a clean bill — absence of mention is absence of a plan. If the user explicitly states no compaction mechanism exists yet (e.g., conversations are currently too short to need one), do not score this GREEN — score it `UNKNOWN` and note explicitly that it has no answer in place for the moment compaction becomes necessary; "not needed yet" is not the same as "solved," especially if the user has stated or implied the system will scale toward longer contexts.
3. **Audit monitor/agent coupling.** Check for any channel — shared logs, shared timing, shared state, the agent choosing how finely to chunk its own actions — through which the agent could infer or influence when/whether it's being watched. Any such channel is a coupling risk regardless of how unlikely exploitation seems; the point of the audit is to name the channel, not to judge intent.
4. **Score each of the three taxonomy categories** (sampling scope, compaction gaps, coupling) as:
   - `RED` — the described architecture has the gap pattern with no stated mitigation.
   - `YELLOW` — a partial mitigation exists but doesn't fully close the gap (e.g., compaction is logged but not independently re-checked).
   - `GREEN` — a specific, named mechanism closes the gap (describe it in one clause to justify the score).
   - `UNKNOWN` — the user's description didn't address this category; never default to GREEN on missing information.
5. **Draft a concrete fix for every RED and YELLOW finding**, stated as a specific architectural change (e.g., "emit a monitor checkpoint keyed to pre-compaction state before any summarization call, not just post-compaction state"; "move monitor sampling-rate decisions server-side so the agent's own action-chunking choices can't change how often it's checked").
6. **Estimate an eligible-coverage range** in words, not a fabricated percentage — e.g., "likely low: only end-of-task sampling means most individual tool calls are never eligible for review" — never invent a numeric coverage estimate without the user supplying real measurement data.
7. If the description already matches a GREEN on all three categories, say so plainly and recommend the production trace-based continuous auditor (the project-level tool, not this skill) as the next step to verify the design holds up against real traffic — don't manufacture findings to pad the report.

## Output format
A markdown review with:
1. **Scorecard**: a 3-row table — `Category | Score (RED/YELLOW/GREEN/UNKNOWN) | One-line reason`.
2. **Findings**, one subsection per RED/YELLOW/UNKNOWN category: what's missing or partial, why it matters (tie back to the specific METR-reported failure mode it resembles), and the concrete fix.
3. **Coverage estimate**: the qualitative eligible-coverage statement from step 6, with the reasoning shown, never a bare invented number.
4. **Priority order**: which fix to make first, with one sentence of justification (compaction gaps first by default, since METR's report attributes the largest share of the unmonitored-traffic finding to this category, unless the user's architecture shows worse coupling risk).

## Guardrails
- Never score a category GREEN when the user's description simply didn't mention it — missing information is `UNKNOWN`, not a pass.
- Never invent a numeric coverage percentage, incident count, or stars/adoption figure for a comparison tool — this skill reasons from the architecture description and the publicly reported METR/Redwood taxonomy only, nothing else.
- Never recommend a specific commercial monitoring vendor or product as "the fix" — fixes are architectural changes to the user's own design, not a product pitch.
- Never treat this review as equivalent to measuring real production traces — always state in the output that this is a design-time estimate, not a substitute for trace-based measurement once the system is live.
- Never skip the compaction-handling check even if the user's description seems thorough elsewhere — it's the single most commonly missed category per the source report, and skipping it defeats the point of the audit.
