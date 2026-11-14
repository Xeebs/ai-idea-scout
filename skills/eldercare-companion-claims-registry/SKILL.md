---
name: eldercare-companion-claims-registry
description: Checks a specific marketing claim about an AI elder-care companion product (e.g. "reduces loneliness by 95%") against independent evidence in ClinicalTrials.gov and PubMed/PMC, and returns a sourced, plain-language verdict on how strong the backing actually is. Use when someone is deciding whether to buy, recommend, or cite a companion-device claim and needs to know if it's backed by real research or just a vendor press release.
---

# Companion Claim Verifier

## When to use this

Someone — a nursing-home administrator, a family caregiver, a journalist, a procurement officer, a policy staffer — has a specific claim in hand about an AI companion/social-robot product for older adults (ElliQ, Meela, Pepper, Paro, Intuition Robotics, or similar) and needs to know: is this backed by real independent evidence, or is it an unreplicated vendor number? Trigger phrases: "does this claim hold up", "is there a study behind this", "check this press release stat", "should we buy/recommend this device based on this claim".

This is a one-shot verification of a single claim, not a standing registry. For tracking many products' claims over time with scheduled re-checks, that's the larger registry project this skill is a component of — this skill only answers the question in front of you right now.

## Inputs

**Data source**: CONNECTED — ClinicalTrials.gov's public API and PubMed/PMC's public E-utilities API (both mature, free, no auth required) to pull registered trials and published studies matching the product/condition. MANUAL for the claim itself: the user pastes the exact marketing claim, press release excerpt, or product-page text being checked, since vendor claims aren't available through any structured API — only the independent evidence side is connected.

What you need from the user:
1. The exact claim text (paste it verbatim — don't paraphrase for them).
2. The product name (ElliQ, Meela, Pepper, Paro, etc.) — ask if not already clear from the claim.
3. Where the claim came from, if known (press release, product page, news article, sales deck) — affects how the verdict frames the source.

## Procedure

1. **Decompose the claim.** Extract: the product, the specific outcome claimed (loneliness, depression, anxiety, falls, medication adherence, etc.), the numeric figure if any (e.g. "95% reduction"), the population described (e.g. "older adults living alone"), and the claim's own stated source if it names one.

2. **Search ClinicalTrials.gov.** Query the product name plus the condition/outcome (e.g. "ElliQ loneliness" or "Meela depression nursing home") against ClinicalTrials.gov. Record every matching trial's NCT number, status (Recruiting / Completed / Withdrawn / Terminated / Not yet recruiting), phase if applicable, enrollment size, and sponsor (vendor-funded vs. independent/academic/NIH).

3. **Search PubMed/PMC.** Query the same terms against PubMed/PMC. Record every matching study's PMID, design (RCT, controlled pilot, uncontrolled feasibility study, case series, review/meta-analysis), sample size, funding disclosure if stated, and the actual reported outcome (not the abstract's spin — read far enough to get the effect size and whether it was statistically significant).

4. **Match evidence to the specific claim.** Not every study on the product supports the specific numeric claim being checked — a general "users reported satisfaction" study does not back a specific "95% reduction in loneliness" figure. Only count a study as directly supporting the claim if it measured the same outcome in a comparable way.

5. **Score methodology quality** using this scale, applied to the strongest matching evidence found:
   - **Strong**: peer-reviewed RCT or controlled study, independent (non-vendor) funding or vendor funding disclosed and accounted for, n ≥ 50, findings replicated in a second independent study.
   - **Moderate**: controlled study or peer-reviewed feasibility study, but single-site, small n (<50), unreplicated, or vendor-funded without independent confirmation.
   - **Weak**: uncontrolled pilot, self-reported survey, case series, or a study measuring a related but not matching outcome.
   - **None found**: no matching trial or publication located after a genuine search of both databases.

6. **Write the verdict** as one of: "Independently replicated" / "Small controlled pilot" / "Unreplicated vendor-funded study" / "Unreplicated self-report, no independent study found" / "No evidence found" / "Mixed/contradictory evidence" (use this last one whenever two matching studies disagree — never average them into a false middle score).

7. **If search access is unavailable** (no live web/API access in the current tool), stop and say so explicitly — list the exact search queries the user should run on clinicaltrials.gov and pubmed.ncbi.nlm.nih.gov themselves and paste back the results, rather than guessing or fabricating a study.

## Output format

```
## Claim checked
"<exact claim text>" — <product>, source: <press release / product page / article / unstated>

## Evidence found
| Source | Design | n | Funder | Outcome measured | Matches claim? |
|---|---|---|---|---|---|
| NCT########  (ClinicalTrials.gov) | ... | ... | ... | ... | Yes/Partial/No |
| PMID######## (PubMed) | ... | ... | ... | ... | Yes/Partial/No |
(one row per matching record found; "No matching records found in ClinicalTrials.gov" / "...in PubMed/PMC" if a database returned nothing)

## Methodology score: Strong | Moderate | Weak | None found

## Verdict
<one of the six verdict categories> — <2-3 sentence plain-language explanation citing the specific evidence row(s) that drove the score>

## Caveats
<anything that limits confidence: search access unavailable, conflicting studies, claim too vague to match to a specific outcome, etc.>
```

## Guardrails

- Never state that a claim is "false," "a lie," or "fraudulent" — score and describe the *evidence*, never the vendor's intent. The output is a methodology assessment, not an accusation.
- Never fabricate an NCT number, PMID, sample size, or finding. If you cannot actually search ClinicalTrials.gov/PubMed in this session, say so and hand the user the exact search queries instead of inventing results.
- Never let a vendor's own press release or product-page number count as "evidence" in the table — it is the claim being checked, never a row supporting itself.
- Never average or split the difference between a supporting and a contradicting study — report both and use the "Mixed/contradictory evidence" verdict.
- Always flag vendor funding explicitly in the Funder column; a vendor-funded study is not automatically disqualified but must never be scored as "Strong" without independent confirmation.
- If the claim is too vague to match to one specific, searchable outcome (e.g. "residents love it"), say that plainly instead of forcing a verdict onto a non-claim.
