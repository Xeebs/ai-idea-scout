# Scenario 2 — Legal research assistant, heavy multi-hop, grounding-critical

## Input the user hands the skill

**Use case**: "Research assistant for a small litigation team. It answers questions over a corpus of case filings, depositions, and prior court rulings for one active case. Lawyers rely on its answers to draft motions, so wrong or invented citations are a serious problem."

**Pipeline today**: "We already added a basic query-rewrite step (expands abbreviations, fixes typos) a few months ago. Nothing else — still single-shot retrieval after the rewrite, one combined index over all document types, no verification step."

**Sample queries (7)**:
1. "Did the defendant's deposition on March 3rd contradict anything they stated in their initial filing?"
2. "Summarize the judge's ruling on the motion to compel."
3. "What exhibits were referenced in both the plaintiff's opening brief and the expert witness report?"
4. "Find every instance where opposing counsel cited precedent that was later overturned."
5. "What was the filing date of the amended complaint?"
6. "Compare the damages figures stated in the deposition versus the expert report versus the original complaint."
7. "Is there a conflict between what witness A said in deposition and what witness B said in their affidavit?"

**Constraints**: "No hard latency requirement — lawyers are fine waiting 10-20 seconds for a thorough answer. Grounding is critical: every claim needs to be traceable to a real document, and we've already had one incident where it cited a case holding that didn't exist. We only have one combined index right now, not separate per-document-type sources."

## Pass criteria

- [ ] Classifies the majority of queries (1,3,4,6,7) as multi-hop/compositional (require combining facts across 2+ documents) — this sample should show a high multi-hop proportion, contrasting with Scenario 1.
- [ ] Recognizes query rewrite is already implemented and doesn't recommend it as a fresh ADOPT (should note it's already present, or treat it as already-ADOPT / no action needed rather than redundantly prescribing it as new).
- [ ] Recommends query decomposition AND multi-hop retrieval together as ADOPT NOW (or clearly top priority), reasoning explicitly from the high multi-hop proportion in the sample.
- [ ] Recommends self-check/self-correction as ADOPT NOW given the explicit grounding requirement and the stated prior incident of a fabricated citation — and does NOT water this down given there's no latency pressure (this is the scenario where self-check is clearly the priority, inverse of Scenario 1).
- [ ] Correctly identifies tool/source routing as not applicable or SKIP/ADOPT LATER, since the team stated only one combined index exists (no genuinely separate sources/tools to route between) — should not invent a routing need that isn't supported by the input.
- [ ] Produces a sequenced adoption order placing decomposition/multi-hop and self-check as the top priorities, distinct in ordering rationale from Scenario 1.
- [ ] Flags the retry-cap / cost consideration for self-check as a secondary note only (since latency isn't a stated constraint here), not as a blocking concern.
- [ ] Does not claim a measured accuracy number (e.g., does not say "this will reduce hallucination by X%") since no benchmark data was supplied.

## Fail conditions

- Recommending query rewrite as a new adoption (ignoring it's already built).
- Recommending routing as ADOPT NOW despite the stated single-combined-index constraint.
- Treating this scenario identically to Scenario 1 in verdict/ordering (would indicate the skill isn't actually reasoning from the specific inputs).
- Inventing a specific hallucination-reduction percentage or benchmark figure.
