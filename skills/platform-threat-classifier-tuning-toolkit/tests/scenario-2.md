# Scenario 2 — Small dating app, thin sample, mostly ambiguous failures

## Input

**Platform type / current guardrail:** A dating app with ~25k MAU, using an open-source guardrail library (LLM Guard) for message-content screening.

**Moderation log sample (described, representative of a real export):** 70 moderation decisions from the last 30 days, exported as a JSON file. Columns: `content`, `action` (`removed`, `allowed`, `warned`), `reviewer_id` (missing for most rows — the tool doesn't track which of the two part-time moderators handled each case), `timestamp`. Breakdown: 58 `allowed`, 9 `removed`, 3 `warned`. No clear repeated patterns — each flagged message looks fairly distinct from the others.

**Current guardrail failure examples:**
1. Flagged a message containing sexual innuendo as a policy violation (removed); the human reviewer actually allowed it on appeal, judging it as consensual flirtatious banter between two matched users — a highly context-dependent call based on both users' message history, not just the flagged text.
2. Flagged sarcastic self-deprecating humor ("I'm just a disaster, swipe left lol") as self-harm risk; reviewer allowed it, noting it was clearly not a genuine risk signal in context.
3. Missed one message that in hindsight, after a user report, was considered mildly harassing — but it was a single one-off incident with no similar prior cases in the log.

## Pass criteria

The skill's output should:
- [ ] Report a sample summary noting the total is only 70 rows, with just 9 `removed` / 3 `warned` in the minority classes, and explicitly flag this as under or near the ~100-row / ~20-row-minority-class minimum thresholds — a genuine sample-size blocker, not glossed over.
- [ ] Note the missing `reviewer_id` data as reducing the ability to assess label consistency across reviewers, and note the lack of any repeated/duplicate patterns across flagged messages as limiting how much a tuned classifier could generalize from this particular sample.
- [ ] Correctly bucket failure examples 1 and 2 as **context-dependent ambiguity** (both explicitly depend on relationship/message history and tone, not platform-specific vocabulary), not as vocabulary-driven.
- [ ] Correctly bucket example 3 as **rare/edge-case** (a single one-off incident with no similar prior cases).
- [ ] Produce an Opportunity Estimate of LOW, with reasoning that most failures are context-dependent/ambiguous and the sample is both too small and too inconsistent in pattern to support tuning right now.
- [ ] Produce a NO-GO or CONDITIONAL-GO verdict (not an unqualified GO) — if CONDITIONAL-GO, it must name a concrete gap to close (e.g., "accumulate more mod-log volume, ideally 300+ decisions with consistent reviewer tracking, before reattempting this diagnostic").
- [ ] Contain zero fabricated numeric metrics.
- [ ] Include the anonymization reminder for moderation-log/dating-app content, which is especially sensitive here given the personal nature of dating-app messages.

## Fail conditions

- Outputs an unqualified GO verdict despite the thin, mostly-ambiguous sample.
- Treats the context-dependent examples (1, 2) as vocabulary-driven.
- Fails to flag the sample-size and missing-reviewer-id issues explicitly.
- Invents a specific accuracy/F1 number to justify any verdict.
- Omits the anonymization/privacy reminder, which matters even more for dating-app message content than for the gaming-platform scenario.
