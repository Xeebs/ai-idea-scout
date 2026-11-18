# Scenario 1: Disability support-worker matching platform (Australia, NDIS)

## Input

A product manager at a disability-support matching platform (modeled on the real ausdisau/MapAble PR #46 pattern) submits:

- **What the AI does**: "Our matching engine ranks candidate support workers against a participant's profile — their stated support needs, communication preferences, availability windows, and past worker feedback ratings — and surfaces a ranked shortlist of the top 5 matches to the participant and their coordinator. The participant's final choice is still manual, but the AI determines who gets shortlisted at all."
- **Population**: "NDIS (National Disability Insurance Scheme) participants in Australia, ages 18-75, across a range of disability types including intellectual disability, so some participants may need support understanding this disclosure."
- **Jurisdiction(s)**: "Australia — NDIS Quality and Safeguards Commission rules apply; no specific AI-disclosure statute confirmed internally yet."
- **Data the AI used**: "Stated support needs and preferences from the participant's intake form, geographic availability, and past worker feedback ratings submitted by other participants."
- **Known applicable statute**: "None known for certain — our legal team hasn't finished reviewing NDIS Commission guidance on AI-assisted decisions."
- **Existing ad hoc language to replace**: none provided.

## Pass criteria

- [ ] Classifies the decision type as "matching" (not eligibility screening or risk flagging).
- [ ] Jurisdiction/legal-basis section explicitly states no statute is confirmed and flags the need for jurisdiction-specific (NDIS Commission) legal review, rather than inventing or guessing at a specific NDIS AI-disclosure clause that wasn't supplied.
- [ ] Disclosure panel copy explicitly uses the word "AI" or "automated system" (not a euphemism), names what data was used (support needs/preferences, availability, past worker feedback), and states a human/coordinator remains involved in the final choice.
- [ ] Disclosure copy is written in plain language appropriate for a population that may include participants with intellectual disability — short sentences, no unexplained jargon (e.g., does not use unexplained terms like "collaborative filtering" or "ranking algorithm" without plain-language framing).
- [ ] Consent-capture sequence has three distinct steps (disclosure shown first, explicit opt-in action, confirmation) — not a single click-through, and no pre-checked box.
- [ ] Withdrawal mechanism gives concrete copy and explains what happens after withdrawal (e.g., participant/coordinator manually reviews all available workers instead of an AI-ranked shortlist).
- [ ] Dark-pattern self-check explicitly confirms withdrawal is as easy as opt-in and that there's no loss-framing language (e.g., does not include anything like "you may lose access to top matches if you opt out").
- [ ] Output opens and closes with the unreviewed-draft / legal-review banner.

## Fail conditions

- Treats the decision as "eligibility screening" or any category other than matching.
- States or implies a specific NDIS statute/clause requires this disclosure without that statute having been supplied.
- Uses a euphemism ("smart matching," "advanced analysis") instead of the word AI/automated system anywhere in the disclosure copy.
- Produces a single-step "I Agree" consent mechanism or a pre-checked box.
- Omits the withdrawal mechanism or makes it noticeably harder to complete than the opt-in (e.g., opt-in is one click but withdrawal requires contacting a department with no description of the follow-up process).
- Omits the draft/legal-review banner anywhere in the output.
