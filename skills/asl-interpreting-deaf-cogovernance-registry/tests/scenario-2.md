# Scenario 2: Specific published claims, sales-call notes, and contradicting third-party evidence

## Input

**Vendor**: ClearHands AI (fictional, representative of a vendor with more developed — but still partial — governance documentation)

**Pasted material** (from the vendor's published "Governance" page):

```
ClearHands AI's Deaf Advisory Board consists of 5 members, 3 of whom are
Deaf (60%), including the Board Chair. The Board reviews all major feature
releases before launch and holds formal sign-off authority on any change to
avatar signing output; a release cannot ship without Board sign-off. In Q2
2026, the Board required us to redesign our regional-dialect handling after
flagging that our Midwest ASL variant was being flattened to a generic
signing style — we delayed launch six weeks to fix this, documented in our
changelog. Board members receive a quarterly stipend for their service.
Our training data currently represents signers primarily from three
metro regions; we have not yet published a breakdown by region or dialect.
```

**Sales call notes** (pasted by the reviewer): "Rep said the Advisory Board is 'very engaged' and that they're 'working on' expanding signer diversity in the data, but couldn't give a timeline when asked directly."

**Third-party evidence** (pasted by the reviewer, from r/ASLinterpreters): "A thread from 3 months ago claims a former ClearHands Board member said the sign-off requirement was 'mostly honored, but marketing once shipped a demo video without Board review.'"

## Expected output characteristics (pass/fail criteria for the evaluator)

- [ ] Produces the five-row table with scores for all five criteria.
- [ ] **Majority-Deaf authority**: scored PASS — the text gives an explicit roster (5 members, 3 Deaf, 60%, Chair is Deaf), meeting the "stated count or ratio" bar.
- [ ] **Published decision-making power**: scored PASS — "cannot ship without Board sign-off" is explicit veto/approval language, not just "input."
- [ ] **Responsiveness track record**: scored PASS — the Q2 2026 regional-dialect example is specific, dated, and documented (changelog cited).
- [ ] **Reviewer compensation**: scored PASS — "quarterly stipend" is a stated compensation structure, even though the exact amount isn't given (amount is not required for PASS per the SKILL.md rubric — only that a structure is stated).
- [ ] **Data/signer representation**: scored PARTIAL or CLAIMS-ONLY, not PASS — the vendor admits data represents only three metro regions and explicitly has not published a full breakdown; this is a partial, self-limiting claim, not a vague one, so PARTIAL is the more defensible score than CLAIMS-ONLY, but either must come with a gap sentence calling out the missing regional breakdown.
- [ ] The third-party Reddit claim (marketing shipping a demo without Board review) is surfaced somewhere in the output — either as a caveat on the Published decision-making power score or in the Overall Read — rather than silently dropped, since the reviewer explicitly supplied it as evidence to weigh in.
- [ ] Overall Read reflects a mixed picture (four PASS, one PARTIAL/CLAIMS-ONLY, plus the third-party caveat) rather than rounding up to "fully verified co-governance" or rounding down to "pure marketing" — must not overstate confidence given the one contradicting data point.
- [ ] Does not treat the sales rep's "working on it" as evidence of a PASS on signer representation — vague verbal assurances without a timeline or document stay NO-EVIDENCE/CLAIMS-ONLY-level, not promoted to PARTIAL on their own.
- [ ] No sign/don't-sign recommendation is given.
- [ ] Limits section is present.
