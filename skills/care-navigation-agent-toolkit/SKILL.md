---
name: care-navigation-agent-toolkit
description: Drafts a structured, cited eligibility-rules configuration from a benefits/assistance program's published policy document, flagging every ambiguous or missing criterion for a human navigator to resolve before the ruleset goes live. Use when a navigator or program coordinator has a program's eligibility policy (PDF text, webpage, or manual excerpt) and needs it turned into a structured rule format instead of re-reading the policy by hand for every patient. Not for determining any individual patient's actual eligibility, running calls, or booking transport.
---

# Care-Navigation Eligibility Ruleset Drafter

## When to use this
A patient navigator, hospital financial-assistance coordinator, or nonprofit program manager has just received or located a benefits/assistance program's published eligibility policy (a financial-assistance policy PDF, a state Medicaid manual excerpt, a nonprofit grant's eligibility page, a transport-benefit policy) and needs to turn it into a structured ruleset — once per program — so that every future patient screening against that program doesn't require re-reading the full policy document from scratch. Reach for this skill at that configuration moment, before the ruleset is used on any real patient.

Do NOT use this for: determining whether a specific named patient is actually eligible (this drafts the rules, it does not apply them to a real case without a human and, ideally, the organization's actual eligibility engine doing the application); placing calls to insurers or patients; booking or tracking transportation; or looking up a program's policy for you — it only works from text you provide.

## Inputs
**Data source**: Manual — the navigator pastes or uploads the program's own published eligibility policy text (a PDF's extracted text, a copied webpage section, or a manual excerpt). No universal live benefits-eligibility API exists across U.S. states and nonprofits, so this step cannot be automated via a connector today; the output of this skill is the configured ruleset meant to be reused by every subsequent screening for that program.

Required:
1. **The policy text itself** — pasted or extracted. If only a link or filename is given with no text, say so and ask for the text/extracted content; never fetch a URL.
2. **Program name and the jurisdiction/org it applies to** (e.g. "Ohio Medicaid Non-Emergency Medical Transportation", "St. Luke's Financial Assistance Policy — Charity Care Tier 2").
3. **The policy's effective/revision date**, if stated in the document. If not stated, flag that explicitly — rules without a known effective date are a known staleness risk for financial-assistance eligibility.

Optional: the organization's existing rule-format schema (if other programs are already configured and a navigator wants this one to match), and any known exceptions or local addenda to the stated policy.

## Procedure
1. **Confirm scope before extracting.** State back the program name, jurisdiction, and effective date as understood. If the effective date is missing from the source text, flag it as unknown rather than guessing a date.
2. **Walk the policy text section by section** and pull out every criterion that gates eligibility: categorical facts (residency, age, household size, diagnosis/condition, citizenship/immigration status, program enrollment elsewhere), numeric thresholds (income as % of Federal Poverty Level, asset limits, mileage/distance limits for transport), documentation requirements (proof of income, proof of residency, physician referral), and time/renewal conditions (annual recertification, retroactive coverage window).
3. **Convert each criterion into a structured rule entry** with: a short rule ID, the plain-English criterion, the rule type (categorical / numeric-threshold / document-required / time-window), the exact operator and value stated in the source (e.g. "household income <= 200% FPL"), and a direct quote or close paraphrase of the source sentence it came from (a citation, not a page number guess — quote the actual clause).
4. **Never invent or infer a threshold the document doesn't state.** If the document says "low income" without a number, or references a table/appendix that wasn't included in the pasted text, create the rule entry with the field populated as `AMBIGUOUS — source does not state a number` rather than filling in a plausible-sounding figure.
5. **Flag every ambiguity, gap, and internal conflict** in a separate list: criteria mentioned but never defined, criteria that seem to contradict each other within the same document, criteria that reference an external document/table not provided, and any criterion whose exact numeric value is unclear from the pasted text (e.g. ranges, "up to", stale-sounding dollar figures).
6. **Flag anything that reads as a legal/consent-sensitive criterion** (anything involving acting on a patient's behalf, sharing data with a third party, or an authorization requirement) separately — these need a human legal/compliance read, not just an eligibility-logic read.
7. **Close with an explicit human sign-off requirement.** State plainly that this ruleset is a draft and must be reviewed line-by-line against the source document by a human navigator or program compliance lead before being loaded into any live screening tool or used on a real patient.

## Output format
```
⚠️ DRAFT RULESET — unverified, requires human navigator/compliance sign-off before use on any real patient.

Program: <name>
Jurisdiction/Org: <state, county, hospital, or nonprofit>
Policy effective date: <date, or "NOT STATED IN SOURCE — flagged below">

## Structured Rules
| Rule ID | Criterion (plain English) | Type | Operator/Value | Source citation |
|---------|---------------------------|------|-----------------|------------------|
| E1 | ... | categorical/numeric-threshold/document-required/time-window | ... | "<quoted or closely paraphrased source clause>" |

## Flagged Ambiguities / Gaps / Conflicts
- <criterion> — <why it's ambiguous: no number given, references missing appendix, contradicts rule Ex, etc.>

## Legal/Consent-Sensitive Items
- <any criterion involving acting on a patient's behalf, data sharing, or authorization — or "None identified in source text" if genuinely none found>

## Sign-off required
This ruleset has not been validated against the full source document by a human and must not be loaded into a live eligibility screening tool, used to tell a patient they do/don't qualify, or relied on for any real determination until a navigator or compliance lead reviews every row above against the original policy text.
```

## Guardrails
- Never state a numeric threshold, dollar figure, or percentage that was not explicitly present in the pasted source text — mark it `AMBIGUOUS` instead of estimating or recalling a "typical" value from general knowledge of benefits programs.
- Never fetch a URL, search the web, or pull in outside knowledge of what a program "usually" requires — work only from the text the navigator actually pasted. If the pasted text is incomplete (cuts off, references a missing table), say so rather than filling the gap from assumption.
- Never drop the draft/sign-off banner or imply the ruleset is ready to load into a live tool — this skill prepares input for a human-reviewed configuration step, it never performs eligibility determination, calling, or transport booking itself.
- Never merge two different programs' policies into one ruleset, even if pasted in the same message — produce one complete ruleset block per program, clearly labeled.
- Never silently skip a criterion because it's hard to classify — if something in the text looks like it gates eligibility but doesn't fit the four rule types cleanly, include it anyway with type `OTHER` and a note explaining the difficulty.
- If the effective/revision date is missing, always surface that as a flagged risk, not a minor omission — a dated ruleset with no known date is a real harm vector for financial-assistance eligibility that changes year to year.
