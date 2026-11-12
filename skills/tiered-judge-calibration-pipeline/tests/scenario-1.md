# Scenario 1 — Pairwise CI-gating judge at a chatbot startup

## Input (what the user hands to the skill)

**Judge prompt/rubric** (verbatim):
```
You are comparing two chatbot responses to the same user message. Response A is from the candidate model (the one being tested in this PR). Response B is from the current production model. Decide which response is better overall and output only "A" or "B".

User message: {input}
Response A: {output_a}
Response B: {output_b}
```

**How it's used**: Pairwise comparative judging. Every PR that changes the chatbot's prompt or fine-tune triggers this judge on a fixed set of 200 held-out conversations; if the candidate model wins fewer than 55% of comparisons, the PR is blocked from merging. The judge model is the same vendor's largest model (same family as both the candidate and production models being compared). Runs roughly 200 evals per PR, a few PRs per week.

**Example judged items** (6 provided):
1. Same pair judged in default order (A=candidate, B=production): verdict "A". Same pair re-run with order swapped (A=production, B=candidate): verdict "A" again — i.e., it picked whichever response was placed first both times, not the same response both times.
2-3. Two more pairs, not re-run in swapped order, verdicts "B" and "A" respectively, no reasoning given (prompt doesn't ask for any).
4-6. Three more single-direction examples. Response A text visibly ~3x longer than Response B in 2 of 3 cases, and the judge picked the longer one both of those times.

**Gold-labeled examples**: none yet.

## Expected output characteristics (pass/fail checklist)

- [ ] Bias-Risk Audit table marks **position bias as CONFIRMED (not just exposed)** for item 1, citing that the swapped-order re-run flipped which letter won while the verdict stayed tied to position, not content — this is the one case in this scenario with enough evidence to go beyond "structural."
- [ ] Marks **self-preference bias as exposed**, explicitly noting the judge model is the same family as both compared models.
- [ ] Marks **length bias as suggestive, not confirmed**, correctly citing only 3 examples with a length disparity (too few to call it confirmed) while still flagging it as a real risk given the pattern direction.
- [ ] Marks **missing reasoning-before-score as exposed** — prompt asks for only "A" or "B", no rationale.
- [ ] Does NOT claim a specific agreement percentage or bias magnitude for this team's judge — only cites counts of what was actually observed (e.g., "1 of 1 swap-tested pairs flipped," "2 of 3 length-disparate examples favored the longer response").
- [ ] Tier 1 plan correctly identifies that almost nothing in this rubric is deterministically rule-checkable (it's a single holistic "which is better" ask with no named criteria) — should say Tier 1 coverage is low/near-zero for this specific setup rather than inventing a percentage, and suggest what adding named criteria would enable.
- [ ] Tier 2 rewrite explicitly adds: an order-swap-and-aggregate instruction (run both orders, require agreement or flag disagreement), a reasoning-before-verdict step, and a length-invariance instruction — all tied back to the specific gaps found above.
- [ ] Tier 3 recommends a gold-set size appropriate to a binary (A/B) judge — around the 30 minimum stated in the procedure, not scaled up to 50-100 (that's only for multi-class/multi-criterion judges) — and a refresh cadence sized to "a few PRs per week at 200 evals each," not a generic default.
- [ ] "What this doesn't tell you" section notes the self-preference finding can't be fully confirmed without more targeted testing (e.g., swapping which vendor's model judges) and that 0 gold-labeled examples means there is currently no way to know if either order's pick is actually the better response.
- [ ] Report does not recommend removing the human/gold-labeling step; frames it as the next required action, not optional polish.
