# Scenario 2 — Marketing-copy generator, second run with a prior baseline (regression check)

## Setup

A 3-person team has a Claude-powered tool that generates short product-description blurbs for an e-commerce catalog. They tightened the system prompt's word-count limit to cut costs and want to check it didn't tank quality. They ran a vibe check last week and saved the block; now they're running it again on fresh samples from the tightened prompt.

## Input handed to the skill

Rubric (existing, pasted): "Rubric: Accuracy (does it match the product facts given), Persuasiveness (would this make someone want to buy), Brand Voice (upbeat, concise, no clichés like 'game-changer' or 'must-have')."

Prior run block (pasted, from last week):
```
## Vibe Check — 2026-11-06
Rubric: Accuracy, Persuasiveness, Brand Voice

| Sample | Accuracy | Persuasiveness | Brand Voice | Notes |
|--------|----------|-----------------|-------------|-------|
| 1      | 5        | 4               | 4           | Clear, grounded in specs |
| 2      | 5        | 5               | 3           | Strong pitch, slightly cliché ("must-have") |
| 3      | 4        | 4               | 5           | Good voice, minor spec miss |

Averages: Accuracy: 4.7 · Persuasiveness: 4.3 · Brand Voice: 4.0
```

New samples (3 pairs, from the tightened prompt):

1. **Product**: "Stainless steel insulated water bottle, 32oz, keeps drinks cold 24 hours."
   **Response**: "32oz stainless bottle, cold for a full day. Simple, solid, does the job."

2. **Product**: "Organic cotton throw blanket, 50x60in, machine washable."
   **Response**: "Soft organic cotton blanket you'll want on every couch. Machine washable, zero fuss."

3. **Product**: "Wireless earbuds, 8-hour battery, water resistant IPX4."
   **Response**: "Great earbuds for the price. Long battery, resistant to water. A must-have for anyone who works out."

## Pass criteria

- [ ] Scores all 3 new samples against the same 3 rubric dimensions (does not invent new dimensions).
- [ ] Computes new per-dimension averages.
- [ ] Produces a diff section comparing new averages to the prior run's (Accuracy: 4.7, Persuasiveness: 4.3, Brand Voice: 4.0), correctly labeling each as REGRESSION / IMPROVEMENT / stable based on the ≥0.5 threshold.
- [ ] Flags Brand Voice as a likely concern or at least notes the recurrence of "must-have" in sample 3 — same cliché flagged in the prior run's sample 2 — as specific, response-grounded evidence (not a generic restatement).
- [ ] Justifications quote actual phrases ("does the job," "zero fuss," "must-have for anyone who works out").
- [ ] Ends with the review-needed line.

## Fail conditions

- Treating this as a first run (ignoring the supplied prior block) or skipping the diff.
- Diff math that doesn't roughly match straightforward averaging of the given scores.
- A justification for the Brand Voice dimension that fails to mention the repeated cliché pattern as evidence.
