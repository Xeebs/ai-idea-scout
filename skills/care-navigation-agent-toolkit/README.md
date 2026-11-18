# Care-Navigation Eligibility Ruleset Drafter

A prompt template for turning a benefits or assistance program's published eligibility policy into a structured, cited ruleset — so a patient navigator (or whatever tool they use to screen patients) doesn't have to re-read the full policy document by hand every single time, while still catching every ambiguous or missing detail before it causes harm.

## Who this is for

Hospital financial-assistance coordinators, nonprofit patient navigators, and small tech teams building a care-navigation tool who have just gotten hold of a program's eligibility policy — a financial-assistance PDF, a Medicaid transport-benefit manual excerpt, a grant program's eligibility webpage — and need it turned into a structured, checkable ruleset. This is a one-time-per-program configuration step; once done, the ruleset is reused for every future screening against that program.

**This is not** an eligibility checker for a specific patient, a calling agent, or a transport booking tool. It only drafts the rules. A human must sign off before the ruleset is used on any real patient, and applying the ruleset to an actual case is a separate step done by a person or a separate tool, not by this prompt.

## Data source

**Manual.** You paste or upload the program's own policy text yourself (extracted PDF text, a copied section of a webpage, or a manual excerpt). There is no universal live API across U.S. states and nonprofits for benefits eligibility rules today, so this cannot be automated by connecting to a data source — you provide the text, and the output (the structured ruleset) is what gets reused afterward.

## How to use it

Paste the following into any AI chat tool (Claude, ChatGPT, Copilot, etc.), then paste your policy text and program details right after it.

---

**Prompt template:**

> You are drafting a structured eligibility ruleset from a benefits/assistance program's published policy text. I will give you: (1) the policy text itself, (2) the program name and the jurisdiction or organization it applies to, and (3) the policy's effective date if stated.
>
> Do this:
> 1. Confirm back the program name, jurisdiction, and effective date as you understood them. If no effective date is stated in the text, say so explicitly — don't guess one.
> 2. Walk through the policy text and extract every criterion that gates eligibility: categorical facts (residency, age, household size, diagnosis, citizenship status, other-program enrollment), numeric thresholds (income as % of Federal Poverty Level, asset limits, mileage/distance limits), documentation requirements (proof of income, proof of residency, physician referral), and time/renewal conditions (recertification period, retroactive coverage window).
> 3. For each criterion, create a rule entry with: a short rule ID, the plain-English criterion, its type (categorical / numeric-threshold / document-required / time-window / other), the exact operator and value as stated in the text, and a direct quote or close paraphrase of the source sentence it came from.
> 4. Never invent or infer a number, threshold, or value that isn't explicitly in the text I gave you. If a number is vague ("low income"), missing, or refers to an appendix/table I didn't paste, mark that rule entry as `AMBIGUOUS — source does not state a number` instead of estimating.
> 5. List separately every ambiguity, gap, missing reference, or internal contradiction you found.
> 6. List separately anything that involves acting on a patient's behalf, sharing their data with a third party, or requiring their authorization — these need a legal/compliance read, not just an eligibility-logic read.
> 7. Never search the web or use outside knowledge of what this type of program "usually" requires — work only from the text I pasted. If my pasted text looks cut off or references something missing, tell me instead of filling the gap yourself.
> 8. End with an explicit statement that this is a draft requiring human sign-off before anyone loads it into a real screening tool or uses it on an actual patient.
>
> Output using this exact structure:
>
> ```
> ⚠️ DRAFT RULESET — unverified, requires human navigator/compliance sign-off before use on any real patient.
>
> Program: <name>
> Jurisdiction/Org: <state, county, hospital, or nonprofit>
> Policy effective date: <date, or "NOT STATED IN SOURCE — flagged below">
>
> ## Structured Rules
> | Rule ID | Criterion (plain English) | Type | Operator/Value | Source citation |
> |---------|---------------------------|------|-----------------|------------------|
> | E1 | ... | ... | ... | "<quoted or closely paraphrased source clause>" |
>
> ## Flagged Ambiguities / Gaps / Conflicts
> - <criterion> — <why it's ambiguous>
>
> ## Legal/Consent-Sensitive Items
> - <item, or "None identified in source text">
>
> ## Sign-off required
> This ruleset has not been validated against the full source document by a human and must not be loaded into a live eligibility screening tool, used to tell a patient they do/don't qualify, or relied on for any real determination until a navigator or compliance lead reviews every row above against the original policy text.
> ```
>
> Here is the policy text, program name, jurisdiction, and effective date:
>
> [PASTE YOUR POLICY TEXT, PROGRAM NAME, JURISDICTION, AND EFFECTIVE DATE HERE]

---

## What you get back

A table of structured eligibility rules, each traceable to an exact quote in the policy you pasted, plus a separate flagged list of anything ambiguous, missing, or contradictory, plus a separate flagged list of anything legally sensitive (acting on someone's behalf, data sharing, authorization requirements). Every output is explicitly marked as a draft that a human must check line-by-line against the source document before it's used on a real patient.

## What this will not do

- It will not look up a program's policy for you — you must have the text already.
- It will not tell you whether a specific patient qualifies — that's a separate step after the ruleset is reviewed and loaded into whatever screening process you use.
- It will not make a phone call, book a ride, or touch any patient's real data.
- It will not fill in a missing number with a "typical" value from general knowledge — if the source document doesn't state it, the output says so.
