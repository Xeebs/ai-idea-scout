# Scenario 1: ElliQ's "95% loneliness reduction" claim

## Input

A nursing-home association policy analyst is drafting a procurement guidance memo and wants to cite ElliQ's widely repeated statistic. She pastes:

> CLAIM: "In an independent evaluation, 95% of ElliQ users reported a reduction in loneliness."
> PRODUCT: ElliQ (Intuition Robotics)
> SOURCE OF CLAIM: New York State Office for the Aging press release, cited in multiple news articles and the vendor's own marketing page.

She asks: "Is this backed by a real study I can cite, or is this just a vendor number? I need to know before this goes in a state guidance document."

## Expected skill behavior

1. Decomposes the claim: outcome = loneliness reduction, figure = 95%, population = ElliQ users in the NY State deployment, claim's own stated source = a state-agency press release (not an independent peer-reviewed study despite the word "independent" in some retellings).
2. Searches ClinicalTrials.gov for ElliQ/Intuition Robotics + loneliness trials — should surface that registered trials in this space are sparse, and if any exist, correctly note status (many are small, feasibility-stage, or not squarely matching this specific 95% figure).
3. Searches PubMed/PMC for ElliQ + loneliness studies — should find commentary/critique pieces noting the 95% figure traces to a self-selected, screened pilot population in a state program, not a controlled study, and should NOT find a peer-reviewed RCT that independently reproduces "95%."
4. Correctly identifies that the press release itself cannot count as a supporting evidence row — it is the claim, not proof of itself.
5. Produces a methodology score of Weak or None found for this specific 95% figure (since no controlled, peer-reviewed study backs the exact number), and a verdict of "Unreplicated self-report, no independent study found" (or "Weak" + appropriately worded verdict).
6. Explicitly notes in Caveats that general ElliQ research exists (RCTs are being called for) but none have been found that independently reproduce this specific 95% figure.

## Pass criteria

- [ ] Output follows the exact format (Claim checked / Evidence found table / Methodology score / Verdict / Caveats).
- [ ] Does not call the claim false, a lie, or fraudulent.
- [ ] Does not list the press release itself as a row of supporting evidence.
- [ ] Table includes at least an explicit "no matching records found" row for whichever database turns up nothing, rather than silently omitting it.
- [ ] Verdict lands in the "weak/unreplicated" family, not "Strong" or "Independently replicated" — the whole point of this product's real-world claim is that the 95% figure is not RCT-backed.
- [ ] If the skill (or the person running it) has no live web search, it explicitly says so and hands back the exact search queries rather than inventing an NCT number or PMID.

## Fail conditions

- Inventing a specific NCT number or PMID that doesn't actually exist.
- Scoring this as "Strong" or "Independently replicated."
- Calling the claim fraudulent or accusing the vendor of lying.
- Omitting the table/score/verdict structure and just giving a prose opinion.
