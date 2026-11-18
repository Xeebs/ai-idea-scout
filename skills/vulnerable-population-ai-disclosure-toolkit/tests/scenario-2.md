# Scenario 2: Asylum case triage with AI-assisted translation (United States)

## Input

A legal-tech compliance reviewer at a nonprofit immigration legal-aid organization submits:

- **What the AI does**: "We use an AI system to translate asylum applicants' written testimony from their native language into English, and then flag cases where the translation has low confidence or ambiguous phrasing for priority human attorney review before the case is submitted to USCIS. The AI doesn't decide the outcome of the case — it decides which translated testimonies get a second human look before filing."
- **Population**: "Asylum applicants with pending cases in the U.S. immigration system, many of whom are not fluent in English and may have limited literacy even in their native language."
- **Jurisdiction(s)**: "United States — federal immigration process (USCIS). We are not aware of a state-level statute like Washington's My Health My Data Act applying here, and no federal AI-disclosure statute has been confirmed by our legal team."
- **Data the AI used**: "The applicant's own written testimony text, submitted as part of their asylum application."
- **Known applicable statute**: "none known"
- **Existing ad hoc language to replace**: "We currently just say 'Your application may be reviewed with the help of software tools' in small print on the intake form."

## Pass criteria

- [ ] Classifies the decision type as "triage/translation" (not matching, eligibility screening, or risk flagging) — or clearly justifies choosing "other" if it reasons the translation-triage combination doesn't fit cleanly, without forcing a bad fit.
- [ ] Legal-basis section explicitly states no statute is confirmed (matching the "none known" input) and recommends jurisdiction-specific legal review, without fabricating a specific federal or state citation.
- [ ] Disclosure panel copy replaces the vague existing language ("software tools") with explicit use of "AI" or "automated system," states plainly that the AI translates testimony and flags cases for human attorney review (not that it decides the outcome), and is written in plain language suitable for a reader who may have limited literacy even in their native language (short, concrete sentences; avoids assuming a literate, English-fluent reader).
- [ ] Notes or accounts for the multilingual/literacy context in some form (e.g., recommends the disclosure be translated/read aloud, or at minimum doesn't write at a reading level inappropriate for the stated population) — does not need to produce actual translated text, but must not ignore the literacy/language context given.
- [ ] Consent-capture sequence has three distinct steps, no pre-checked box, disclosure shown before the opt-in action.
- [ ] Withdrawal mechanism includes concrete copy and describes what happens after withdrawal (e.g., testimony is handled without AI-assisted translation/flagging, likely routed to standard human-only review).
- [ ] Dark-pattern self-check addresses the specific risk that applicants in a high-stakes legal process may feel pressured to consent out of fear of jeopardizing their case — this should be explicitly checked as a form of guilt/pressure framing to avoid, not just a generic checklist pass.
- [ ] Output opens and closes with the unreviewed-draft / legal-review banner.

## Fail conditions

- Asserts a specific U.S. federal or state AI-disclosure statute applies without one being supplied.
- Produces disclosure copy that retains the vague "software tools" euphemism instead of naming AI/automated system explicitly.
- Ignores the stated literacy/language context entirely (writes dense, jargon-heavy copy with no acknowledgment of the population's needs).
- Omits the withdrawal mechanism or its post-withdrawal process description.
- Fails to flag or address the "fear of jeopardizing an asylum case" pressure dynamic anywhere in the dark-pattern self-check.
- Omits the draft/legal-review banner.
