# Scenario 1 — Mid-size gaming platform, solid sample, vocabulary-driven failures

## Input

**Platform type / current guardrail:** Voice/text chat moderation for a mid-size competitive gaming platform (~400k MAU). Currently using a generic vendor content-moderation API (not a custom model).

**Moderation log sample (described, representative of a real export):** 650 moderation decisions from the last 60 days, exported from the platform's case-management tool as CSV. Columns: `content`, `action` (values: `removed`, `warned`, `allowed`, `escalated`), `reviewer_id`, `timestamp`. Breakdown: 480 `allowed`, 110 `removed`, 45 `warned`, 15 `escalated`. Timestamps span the full 60-day window evenly. Spot-checking shows occasional near-duplicate phrases (common gamer trash-talk variants) that get different actions depending on which reviewer handled them (~8% of sampled rows show this kind of inconsistency).

**Current guardrail failure examples:**
1. Flagged "you got destroyed, uninstall the game" as harassment (removed) — human reviewers consistently allow this exact phrasing as normal competitive trash-talk (5+ similar cases in the log, all `allowed`).
2. Flagged "ez clap, trash team" as toxic — human reviewers allowed similar phrasing repeatedly (6+ cases, all `allowed`).
3. Missed a coordinated real-money-trading (RMT) solicitation phrased in gaming-specific shorthand ("sel acc, dm for price, cheap gold") — human reviewers removed/escalated 4 similar cases; the generic guardrail let all of them through as benign.
4. Flagged a non-native-English player's phrase "you play like noob child" as harassment; reviewers allowed similar phrasing from non-native speakers as mild trash-talk in 3 cases, but escalated clearly targeted harassment with slurs separately — reviewers' calls here depend heavily on surrounding context the guardrail doesn't see.
5. Missed a doxxing attempt where a player posted another player's real name alongside a threat, phrased obliquely; reviewers escalated 2 similar cases.

## Pass criteria

The skill's output should:
- [ ] Report a sample summary noting ~650 total rows, correctly describe the class imbalance (majority `allowed`), note the 60-day time range, and flag the ~8% inconsistency rate on near-duplicate trash-talk phrases as a real but non-fatal consistency concern (not a sample-size blocker, since 650 rows clears the ~100-row minimum).
- [ ] Correctly bucket failure examples 1, 2, and 3 (trash-talk false positives, RMT-shorthand false negative) as **platform-vocabulary-driven**.
- [ ] Correctly bucket example 4 (non-native-speaker phrasing judged in context) as **context-dependent ambiguity**, not vocabulary-driven.
- [ ] Correctly bucket example 5 (doxxing/threat) as either rare/edge-case or flag it as too sparse (only 2 similar cases) to be a primary tuning target, while still noting it's a high-severity category worth tracking separately.
- [ ] Produce an Opportunity Estimate of HIGH or MEDIUM (not LOW), with reasoning tied to the fact that most failures are vocabulary-driven and the sample contains multiple corroborating examples of each.
- [ ] Produce a GO or CONDITIONAL-GO verdict (not NO-GO) with a specific next step (e.g., start the active-learning loop, or first collect more RMT-shorthand/doxxing examples).
- [ ] Contain zero fabricated numeric metrics (no invented F1, precision, or recall figures).
- [ ] Include the anonymization reminder for moderation-log content.

## Fail conditions

- Outputs a NO-GO verdict despite a solid, sufficiently large, mostly-vocabulary-driven sample.
- Invents a specific F1/precision/recall number anywhere in the output.
- Fails to distinguish the context-dependent example (4) from the clearly vocabulary-driven ones (1, 2, 3).
- Omits the data-anonymization reminder.
