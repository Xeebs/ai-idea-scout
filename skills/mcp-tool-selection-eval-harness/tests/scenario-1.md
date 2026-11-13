# Scenario 1 — Brand sentiment vs. generic analytics tool (the originating Reddit incident)

## Input (what the user pastes)

> **User request:** "What's the overall brand sentiment for our product across last week's mentions?"
>
> **Tool that got called:** `analyze_metrics`
> Description: "Analyzes numerical and categorical data trends over a given time window. Use for reporting on usage stats, counts, and performance metrics across a dataset."
>
> **Other tools available:**
> - `brand_sentiment_tracker` — "Tracks and scores sentiment (positive/negative/neutral) from social mentions, reviews, and support tickets for a brand or product over a time range."
> - `export_report` — "Generates a PDF/CSV export of any previously run analysis."
>
> **Correct tool:** `brand_sentiment_tracker` (confirmed by the user)
>
> **System prompt:** none provided.

## Pass criteria

- [ ] Incident Summary line correctly states: request asked for brand sentiment, `analyze_metrics` was called, `brand_sentiment_tracker` should have been called.
- [ ] Root Cause section quotes the actual overlapping language — specifically that both descriptions mention "trends/scores... over a time range/window" and neither explicitly excludes the other's domain (sentiment vs. generic metrics).
- [ ] Missing boundary is named explicitly: `analyze_metrics`'s description never excludes sentiment/opinion data, so "brand sentiment" plausibly reads as a "trend ... over a time window."
- [ ] System Prompt Interference section is omitted or explicitly states "none provided" (no system prompt was given — must not invent one).
- [ ] Suggested rewrite for `analyze_metrics` adds an explicit exclusion (e.g., "...Does NOT handle sentiment, opinion, or subjective scoring — use brand_sentiment_tracker for those.") and stays short enough to be a real schema description (1-3 sentences).
- [ ] At least 2 regression scenarios are produced in intent -> expected_tool form; at least one is a near-miss distractor (e.g., "show me engagement trends for last week" -> analyze_metrics, to confirm the rewrite doesn't break legitimate metrics requests) rather than a repeat of the exact original phrase.
- [ ] Confidence & Limits section is present and does not overclaim — acknowledges this is one incident's evidence, not a guarantee the rewrite eliminates all future misroutes.
- [ ] No tool name, description, or behavior is invented beyond what was pasted in.

## Fail conditions

- Treats the fix as "just delete analyze_metrics" or any architecture change instead of a description rewrite.
- Produces only one regression scenario, or two scenarios that are both near-exact restatements of the original failing request.
- States the root cause as absolute certainty with no acknowledgment that model-specific behavior could also be a factor.
