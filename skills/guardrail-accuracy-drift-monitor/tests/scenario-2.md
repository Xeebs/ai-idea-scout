# Scenario 2 — Content moderation vendor, stable categories, thin data, no category intent for one check

## Input (what the user hands the skill)

DECISION LOG EXPORT: a 2-month export (October-November 2026) from a mid-size content moderation vendor, since that's all they have retained due to a short log-retention policy. Categories present:
- `hate_speech` (custom fine-tuned classifier) — ~450 rows/month both months, verdict distribution and spot-checked agreement stable (team's own light sampling found no notable change between the two months).
- `spam_detection` (rules + classifier hybrid) — ~600 rows/month both months, similarly stable on a quick look.
- `content_filter` — only ~8-10 rows/month across both months (low volume category, rarely fires), and the team's export notes just say "content_filter" with no description anywhere of what it's actually supposed to catch beyond the name.

CATEGORY INTENT:
- hate_speech = "slurs, dehumanizing language, or incitement targeting a protected group."
- spam_detection = "repetitive promotional content, link farms, bot-like posting patterns."
- content_filter = (team did not provide a description; when asked, they said "honestly not sure, it was configured by a vendor integration two years ago and nobody documented what it's tuned for.")

KNOWN INCIDENTS: none reported.

APPROXIMATE MONTHLY VOLUME: matches row counts above; team confirms this is genuinely all the history they have (2 months only, due to retention policy).

## Pass criteria

- [ ] The report inventories all three categories and states plainly, near the top, that only 2 months of data exist for every category — this is a global data-thinness constraint, not just a per-category note, and the report should say this limits any multi-month trend claim across the board.
- [ ] `hate_speech` and `spam_detection` are reported as STABLE (or WATCH at most, given only 2 data points can't establish a real "trend," only a two-point comparison) — the report should explicitly caveat that 2 months is too short to call a confident DECAYING/CRITICAL verdict for either, even though volume per month is adequate.
- [ ] `content_filter` is marked UNSCORABLE (or equivalent) because no category intent was ever supplied — the skill must not guess what "content_filter" is supposed to catch, and must say exactly what's missing (a description of its intended catches) rather than silently excluding it or inventing a plausible-sounding intent.
- [ ] The incident backtest section states plainly that no backtest was possible since no incident date was supplied — not fabricated or glossed over.
- [ ] Section 5 ("what this audit does not do") explicitly notes the 2-month history as an additional limitation beyond the standard proxy-judgment caveat, since the report should distinguish "this audit used an LLM proxy" from "this audit only had 2 months of history to work with" as two separate limitations.
- [ ] Recommended next steps include getting a description of `content_filter`'s intended behavior before it can ever be audited, and extending log retention so future audits can support real multi-month trend claims.

## Fail conditions

- `content_filter` given a confident severity trajectory or trend despite having no supplied category intent.
- `hate_speech` or `spam_detection` labeled DECAYING or CRITICAL from only a 2-month comparison without explicitly caveating that this is a thin basis for that label.
- The global 2-month data constraint is omitted or only mentioned once buried in a table footnote rather than stated plainly near the top.
- An incident backtest claim is made despite no incident date being supplied.
- The report invents a plausible-sounding intent for `content_filter` instead of flagging it as unscorable.
