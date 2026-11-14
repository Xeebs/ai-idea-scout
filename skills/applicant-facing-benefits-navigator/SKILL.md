---
name: applicant-facing-benefits-navigator
description: Explains a confusing SNAP/Medicaid (or similar means-tested benefits) notice in plain language, lists exactly what's required and by when, and drafts a response or appeal letter. Use when someone has received a benefits notice, denial, reduction, or recertification/verification request they don't fully understand and needs to know what to do next.
---

# Notice Explainer & Response Drafter

## When to use this
Someone has just received (or is looking at) a letter, portal message, or PDF from a SNAP, Medicaid, or similar means-tested benefits agency — an approval, denial, reduction, termination, recertification request, or request for verification documents — and either doesn't understand what it's asking of them, is unsure of the deadline, or needs a response/appeal drafted. This is a single-document task: one notice in, one explanation plus (if warranted) one drafted letter out. It does not track multiple pending deadlines over time or pre-fill a full benefits application — those need persistent state this skill doesn't carry.

## Inputs
**Data source**: Manual — the user pastes the full text of the actual notice/letter they received (copy-paste, OCR'd text, or a careful retype) plus a few sentences on their situation. Nothing is fetched from any agency system.

Required:
1. **The notice text, as close to verbatim as possible** — including any reference/case numbers, dates, checked boxes, and cited reasons. Partial or garbled OCR is usable but must be flagged as such.
2. **Program and state** — e.g. "SNAP, California" or "Medicaid, Texas" — rules and deadlines vary by state and program.
3. **A few sentences on their situation** — what changed recently (new job, income change, moved, missed an appointment), and what they want to happen (keep benefits, get the reduction reversed, just understand it).

Optional but improves the draft: household size, approximate income, and whether they've already sent in any of the requested documents.

## Procedure
1. **Parse the notice** for: program name, notice type (approval / denial / reduction / termination / recertification request / verification request), the specific agency action taken or requested, any case/reference numbers, the stated reason or policy citation, and any date given (notice date, response-by date, effective date).
2. **Classify procedural vs. substantive**:
   - *Procedural* — the action hinges on a missing document, unreturned form, or missed appointment, not a judgment about actual eligibility. These are usually the easiest to reverse by simply supplying what's missing.
   - *Substantive* — the agency made an eligibility or benefit-amount determination based on income, household composition, or program rules.
   - If the notice text doesn't clearly support either label, say so explicitly rather than guessing.
3. **Compute the deadline** only from what the notice states: if it gives an explicit date, use it; if it gives "X days from the date of this notice" and the notice date is present, calculate the resulting date and show the arithmetic; if neither is present, output `Deadline: not stated in notice text — confirm with caseworker or agency directly` rather than inventing one.
4. **List exactly what's required**, as a checklist, quoting or closely paraphrasing the notice's own language for each item (document, form, appointment) — never add a requirement the notice didn't state.
5. **Write the plain-language summary** — 2-4 sentences, no jargon, answering: what happened, why (as the notice states it), and what happens if nothing is done by the deadline.
6. **Decide whether a response/appeal letter is warranted.** Draft one when: the user wants to contest a denial/reduction/termination, needs to request more time, or is submitting verification in response to a procedural notice. Skip the letter (and say why) when the notice is a simple approval or informational notice with nothing to contest.
7. **Draft the letter** using the structure in Output format below, written in the applicant's own voice from the situation they gave — stick to the facts they provided, never invent supporting facts (income figures, dates of events) they didn't state.
8. **Flag what to confirm locally** — anything state-specific (fair hearing request process, legal aid contact, exact mailing address/fax) that this skill can't verify from the notice text alone.

## Output format
```
Program: <as stated in notice> · State: <as given>
Notice Type: <approval|denial|reduction|termination|recertification request|verification request|unclear>
Procedural vs. Substantive: <label> — <one-line reason>

Plain-Language Summary:
<2-4 sentences>

What's Required of You:
- <item 1, by when>
- <item 2, by when>
(or "Nothing further required — this is an approval/informational notice.")

Deadline: <computed date + consequence of missing it> | "not stated in notice text — confirm with caseworker"

Draft Response/Appeal Letter:
<full letter text, or "Not applicable — see reason above">

What to Confirm Locally:
- <state-specific procedural items the notice text didn't cover>

Disclaimer: This explains the notice and drafts a response based only on what you provided — it is not legal advice and does not guarantee an outcome. Confirm deadlines and procedure with your caseworker, local legal aid, or a benefits attorney before relying on it, especially for anything with real consequences (loss of benefits, fraud flags).
```

## Guardrails
- Never state or imply a legal eligibility determination ("you should win this appeal," "you qualify") — only explain what the notice says and draft the requested document.
- Never invent a deadline, case fact, income figure, or document requirement that isn't present in the notice text or the user's stated situation — say explicitly what's missing instead.
- Never treat this as a substitute for legal aid on high-stakes outcomes (fraud allegations, loss of housing-linked benefits); always include the disclaimer and recommend local confirmation.
- If the pasted notice text is too garbled/incomplete to parse reliably, say so and ask for a cleaner copy rather than guessing at its content.
- Do not draft an appeal/response letter when the notice is a plain approval with nothing to contest — padding with an unnecessary letter is a failure, not thoroughness.
