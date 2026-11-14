# Agent Monitor Blind-Spot Auditor

A paste-into-any-AI-chat-tool prompt that reviews a described agent-monitoring architecture for structural blind spots — the same categories of gap that METR and Redwood Research's red-team of OpenAI's internal agent-monitoring system found in a three-week manual engagement (published 2026-10-22), and that a second METR red-team of Anthropic's monitoring found again on 2026-03-26 at a different lab. Instead of commissioning a multi-week expert engagement, you get the same taxonomy applied to your own design in one pass.

## When to use this

You're about to ship, or already run, a monitoring/guardrail layer over a production LLM agent — a sampler, a judge-model reviewer, or a policy checker sitting alongside an agent loop — and you want to know whether it has blind spots before an incident finds them for you. This is a design-time review: it works from a written description of your architecture, not from live trace data, so you can run it before you've built anything or as a quick gut-check on something already running.

Don't use this to debug one specific incident with a known cause (that's a post-mortem, different task), and don't treat it as a replacement for actually measuring coverage against real production traces once you have them — this catches design flaws on paper, it doesn't measure your live system.

## What to hand over

This skill works from your own description — nothing gets connected or fetched automatically. Paste or describe:

1. **What gets sampled and when.** Every tool call? Only at end-of-task? A fixed percentage? Only when a risk heuristic trips?
2. **How context compaction/summarization is handled.** When your agent's context gets compacted, truncated, or summarized mid-task, does anything happen to the monitor's visibility into the actions that happened before that point?
3. **How monitor/agent isolation is enforced.** Does the monitor run as a fully separate process/model with no shared mutable state with the agent? Or could the agent see, predict, or influence when or whether it's being watched — shared logs it can read, shared timing signals, or the agent choosing its own action granularity?
4. **(Optional)** Any existing eval/coverage numbers or a sample transcript, to anchor the review in something concrete.

If you can't answer one of the first three, say so — don't guess a safe-sounding default. The reviewer will mark anything unaddressed as `UNKNOWN`, not assume it's fine.

## The full prompt

Copy everything below the line into your AI chat tool, then fill in your architecture details where marked.

---

You are auditing my agent-monitoring architecture for structural blind spots, using the taxonomy from METR and Redwood Research's 2026-10-22 red-team of OpenAI's internal agent-monitoring system (and the matching 2026-03-26 METR red-team of Anthropic's monitoring, which found the same category of gaps independently). That engagement found monitors missed roughly 10% of eligible agent traffic during a multi-month window, concentrated in three failure modes: (1) sampling scope gaps — end-of-task-only or periodic sampling instead of per-action checks, (2) context-compaction gaps — actions that happened right before a compaction/summarization event going unwatched, and (3) monitor/agent coupling — the agent having any way to see, predict, or influence when it's being watched.

Here is my architecture:
- **Sampling**: [describe what triggers a monitor check and how often]
- **Compaction handling**: [describe what happens to monitoring when context gets compacted/summarized/truncated mid-task, or say "not handled" / "not sure"]
- **Isolation**: [describe whether the monitor is a fully separate process/model, and whether any shared state, logs, or timing could let the agent infer or influence monitoring]
- **(Optional) existing numbers**: [any coverage %, eval results, or a sample transcript]

Please:
1. Score each of the three categories (sampling scope, compaction gaps, coupling) as RED (gap present, no mitigation), YELLOW (partial mitigation that doesn't fully close it), GREEN (a specific named mechanism closes it — state the mechanism), or UNKNOWN (I didn't give you enough to judge, or compaction doesn't exist yet in my system but will eventually be needed — never default either case to GREEN).
2. For every RED or YELLOW, explain which specific failure mode it resembles and give me a concrete architectural fix, not a vague suggestion.
3. Give me a qualitative eligible-coverage estimate in words (e.g. "likely low — only end-of-task sampling") with your reasoning shown. Do not invent a numeric percentage unless I gave you real measured data.
4. Tell me which fix to make first and why — default to prioritizing compaction gaps unless my coupling risk looks worse, since that's where METR's report found the largest share of the unmonitored-traffic problem.
5. If all three categories come back GREEN, say so plainly and tell me the next step is measuring real production traces, not more design review — don't manufacture findings just to fill out the report.

Format your answer as:
- A 3-row scorecard table: Category | Score | One-line reason
- A findings section, one subsection per RED/YELLOW/UNKNOWN category, with the fix
- The coverage estimate with reasoning
- A one-line priority recommendation

---

## Guardrails (the reviewer should follow these, and you should check the output against them)

- A category should never be scored GREEN just because you didn't mention it — missing information is UNKNOWN, not a pass.
- No invented coverage percentages, incident counts, or comparisons to specific numbered stats beyond what you supplied or what's publicly reported about the METR/Redwood engagement itself.
- No recommending a specific commercial monitoring product as "the fix" — fixes should be changes to your own architecture.
- The output should explicitly note this is a design-time estimate, not a substitute for measuring real traces once your system is live.
- The compaction-handling category should never get skipped, even if everything else looks solid — it's the category METR's report attributes the largest share of the unmonitored-traffic gap to.

## Limits

This is a one-shot design review based on your own description — it can't catch a blind spot you didn't know to describe, and it can't verify your system actually behaves the way you described it. If you want continuous, trace-based measurement against your real production traffic instead of a design-time review, that's a different (project-level) tool, not this skill.
