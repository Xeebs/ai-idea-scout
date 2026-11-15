# Scenario 1: Support ticket urgency classifier (should recommend FINE-TUNE)

## Input

**Task description**: "Given the subject line and first message of a support ticket, output one of three urgency labels: `URGENT`, `NORMAL`, or `LOW`. URGENT means the customer reports data loss, an outage, or a billing error charging them twice. NORMAL means a feature question or a bug that has a workaround. LOW means a feature request or general feedback with no immediate impact."

**Examples (42 rows, representative sample shown)**:
```
input: "Subject: Can't log in at all, losing customers right now | Body: Our whole team has been locked out since 9am, we're missing a live sales demo." -> output: URGENT
input: "Subject: Charged twice this month | Body: I see two charges of $49 on my card for November, please refund one." -> output: URGENT
input: "Subject: All our data is gone | Body: I opened the dashboard and every report from the last 6 months is missing." -> output: URGENT
input: "Subject: Export button greyed out | Body: The CSV export is disabled on the reports page, but I can still get the data via the API." -> output: NORMAL
input: "Subject: Confused about date filter" | Body: "Not sure how the custom date range picker works, docs don't explain it." -> output: NORMAL
input: "Subject: Slack integration keeps dropping" | Body: "Messages stop posting to our channel after a few hours, have to reconnect manually." -> output: NORMAL
input: "Subject: Would love dark mode" | Body: "Just a nice-to-have, staring at the white dashboard all day is rough." -> output: LOW
input: "Subject: Feature idea - bulk tagging" | Body: "Could we select multiple records and tag them at once?" -> output: LOW
input: "Subject: Loving the new report builder" | Body: "Just wanted to say the new drag-and-drop report builder is great, no complaints." -> output: LOW
... (33 more rows, roughly 15 URGENT, 15 NORMAL, 12 LOW, no contradictions, consistent single-label format)
```

**Already tried few-shot prompting?**: "Yes — I put 10 of these in-context as few-shot examples against Qwen2.5-1.5B and it got 33/42 (79%) right on the rest, but it keeps calling double-billing NORMAL instead of URGENT and occasionally mislabels outage reports as NORMAL when the wording is informal."

## Pass criteria

- [ ] Gate 0 (contradictions): correctly finds no meaningful contradictions, proceeds.
- [ ] Gate 1 (prompt ceiling): correctly recognizes few-shot prompting was already tried and measured (79%), proceeds instead of stopping with "try prompting first."
- [ ] Gate 2 (knowledge vs behavior): correctly identifies this as a behavior/format consistency gap (not a knowledge gap) — the model knows what double-billing and outages are, it just won't apply the label rule consistently — proceeds.
- [ ] Gate 3 (sufficiency): classifies as classification task with 3 distinct labels, computes examples-per-pattern (~14 per label from 42 total / 3 labels), correctly finds this is >= 2 per pattern, proceeds.
- [ ] Final recommendation is **FINE-TUNE**.
- [ ] Synthetic set target computed as `max(300, 40 x 3) = 300` and shown with the math.
- [ ] Base model tier recommended is the 0.5B-1.5B tier (short inputs, <=10 labels, classification) with named example models (Qwen2.5-0.5B/1.5B or SmolLM2-1.7B).
- [ ] Confidence stated as high or medium with a stated reason (examples-per-pattern ~14, existing 79% baseline measured).
- [ ] Output follows the exact `## Vibe-Tune Advisory` structure from SKILL.md/README.md.
- [ ] Does not claim to have run any training, synthetic generation, or evaluation — advisory only.

## Fail if

- Recommends STICK WITH PROMPTING despite an already-measured, imperfect few-shot baseline.
- Misclassifies this as a knowledge gap (it is clearly a format/rule-consistency gap).
- Omits the synthetic-size math or the base-model tier reasoning.
- Produces a recommendation without noting confidence level.
