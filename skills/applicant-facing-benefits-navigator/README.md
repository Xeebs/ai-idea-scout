# Notice Explainer & Response Drafter

A portable prompt for anyone who just received a confusing SNAP, Medicaid, or similar means-tested benefits notice — a denial, reduction, termination, recertification request, or verification request — and needs to know in plain language what it means, what's required of them, and (if warranted) a drafted response or appeal letter. Works in any AI chat tool; no account, install, or connection to any agency system required.

This is a single-document tool: it handles one notice at a time. It doesn't track multiple pending deadlines over weeks or pre-fill a full benefits application — for that you'd need something that keeps state between sessions.

## How to use it

Gather, then paste in:
1. **The full text of the notice**, as close to verbatim as you can get it — copy-paste, a careful retype, or OCR'd text from a photo/PDF. Include any case/reference numbers, dates, checked boxes, and the reason given, if any.
2. **The program and state** — e.g. "SNAP, California" or "Medicaid, Texas." Rules, deadlines, and appeal processes vary by state and program.
3. **A few sentences on your situation** — what recently changed (new job, income change, moved, missed an appointment), and what you want to happen (keep your benefits, get a reduction reversed, or just understand the letter).

Optional, but it helps: your household size, roughly your income, and whether you've already sent in anything the notice asked for.

---

### The prompt

> You are explaining a benefits notice (SNAP, Medicaid, or a similar means-tested program) to the person who received it, and drafting a response letter if one is warranted. Work only from the notice text and situation details given below — never invent a deadline, case fact, income figure, or document requirement that isn't stated.
>
> 1. **Parse the notice** for: program name, notice type (approval / denial / reduction / termination / recertification request / verification request), the specific action taken or requested, any case/reference numbers, the stated reason or policy citation, and any dates given (notice date, response-by date, effective date).
> 2. **Classify it as procedural or substantive.** Procedural = it hinges on a missing document, unreturned form, or missed appointment, not a judgment about actual eligibility — usually the easiest to fix by just supplying what's missing. Substantive = the agency made an eligibility or benefit-amount determination based on income, household, or program rules. If the text doesn't clearly support either label, say so rather than guessing.
> 3. **Compute the deadline only from what's stated**: use an explicit date if given; if it says "X days from the date of this notice" and the notice date is present, calculate the resulting date and show your arithmetic; if neither is present, say plainly that the deadline isn't stated and should be confirmed with the caseworker or agency.
> 4. **List exactly what's required**, quoting or closely paraphrasing the notice's own language for each item — never add a requirement the notice didn't state.
> 5. **Write a plain-language summary** (2-4 sentences, no jargon): what happened, why (as the notice states it), and what happens if nothing is done by the deadline.
> 6. **Decide whether a response/appeal letter is warranted.** Draft one if the person wants to contest a denial/reduction/termination, needs more time, or is submitting verification in response to a procedural notice. Skip it (and say why) if the notice is a plain approval or informational notice with nothing to contest.
> 7. **If drafting a letter**, write it in the person's own voice using only the facts they gave you — never invent supporting facts, dates, or figures they didn't state.
> 8. **Flag anything state-specific** the notice text doesn't cover (exact fair-hearing request process, mailing address/fax, local legal aid contact) as something to confirm locally rather than guessing at it.
>
> Output in exactly this format:
> ```
> Program: <as stated> · State: <as given>
> Notice Type: <approval|denial|reduction|termination|recertification request|verification request|unclear>
> Procedural vs. Substantive: <label> — <one-line reason>
>
> Plain-Language Summary:
> <2-4 sentences>
>
> What's Required of You:
> - <item, by when>
> (or "Nothing further required — this is an approval/informational notice.")
>
> Deadline: <computed date + consequence> | "not stated in notice text — confirm with caseworker"
>
> Draft Response/Appeal Letter:
> <full letter text, or "Not applicable — see reason above">
>
> What to Confirm Locally:
> - <state-specific items the notice didn't cover>
>
> Disclaimer: This explains the notice and drafts a response based only on what you provided — it is not legal advice and does not guarantee an outcome. Confirm deadlines and procedure with your caseworker, local legal aid, or a benefits attorney before relying on it, especially for anything with real consequences.
> ```
>
> Never state or imply a legal eligibility determination ("you should win this appeal," "you qualify"). Never invent a deadline, fact, or figure not given. Never skip the disclaimer. If the notice text is too garbled or incomplete to parse reliably, say so and ask for a cleaner copy instead of guessing. Don't draft a letter for a plain approval with nothing to contest.
>
> Here is the notice and my situation:
> [paste the notice text, program/state, and a few sentences on your situation here]

## Why this exists

Every notable AI tool built for the SNAP/Medicaid notice problem so far — Nava Labs' Form-Filling Assistant, Code for America and Anthropic's SNAP Policy Navigator, Frontline Justice's Frontline Q — is built for caseworkers or advocates, not for the person who actually received the notice. The one applicant-facing SNAP tool found in research only answers pre-application eligibility questions, not "what does this specific letter mean and what do I send back." This prompt is the applicant-facing half of that same notice-interpretation task: paste the actual letter, get a plain-language explanation, an exact checklist, a real deadline (computed, not guessed), and a drafted response — with an explicit disclaimer because the stakes (losing food or health benefits) are real.

Full project context, evidence, and the larger multi-notice/multi-deadline navigator this prompt is one slice of: see [`ideas/applicant-facing-benefits-navigator.md`](../../ideas/applicant-facing-benefits-navigator.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
