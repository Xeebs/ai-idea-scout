# Companion Claim Verifier

A paste-anywhere prompt for checking whether a marketing claim about an AI elder-care companion device (ElliQ, Meela, Pepper, Paro, Intuition Robotics, or similar) is actually backed by independent research — or is just an unreplicated vendor number dressed up as proof.

## Who this is for

Nursing-home administrators, family caregivers, journalists, procurement staff, or policy people who have one specific claim in front of them (a press release stat, a product-page line, a sales-deck slide) and need a straight answer: is there real evidence behind this number, or not?

This checks **one claim at a time**. It is not a running registry of every claim ever made about every product — it's the thing you run right before a purchase decision or before quoting a number in a report.

## What you need before you start

1. The exact claim text, pasted verbatim — don't summarize it yourself, paste the actual sentence.
2. The product name it's about (ElliQ, Meela, Pepper, Paro, etc.).
3. Where you got the claim, if you know (press release, product page, news article, sales deck) — this matters for the final write-up.

**Data source note**: this skill is CONNECTED for the evidence side — it depends on an AI tool that can actually search or browse ClinicalTrials.gov and PubMed/PMC (both free, public, no login required). The claim itself is always MANUAL — you paste it, because vendor claims live in press releases and product pages, not in any structured database. If your AI tool cannot browse the web, it should tell you so and hand you the exact search terms to run yourself on clinicaltrials.gov and pubmed.ncbi.nlm.nih.gov, then you paste the results back.

## The prompt

Paste this into any AI tool with web search/browsing enabled, filling in the brackets:

```
I need you to fact-check a specific marketing claim about an AI elder-care companion
product against independent research. Here is the claim:

CLAIM: "[paste the exact claim text here]"
PRODUCT: [product name, e.g. ElliQ]
SOURCE OF CLAIM: [press release / product page / article / sales deck / unknown]

Do the following:

1. Break the claim down into: the specific outcome measured (loneliness, depression,
   falls, medication adherence, etc.), the numeric figure claimed if any, and the
   population described.

2. Search ClinicalTrials.gov for trials matching this product and outcome. For each
   match, note: NCT number, status (Recruiting/Completed/Withdrawn/Terminated),
   enrollment size, and sponsor (is it vendor-funded or independent/academic/NIH?).

3. Search PubMed/PMC for published studies matching this product and outcome. For
   each match, note: PMID, study design (RCT, controlled pilot, uncontrolled
   feasibility study, case series, review), sample size, funding source if disclosed,
   and the actual reported finding (read past the abstract spin to the real effect
   size and whether it was statistically significant).

4. Only count a study as supporting THIS specific claim if it measured the same
   outcome in a comparable way — a general satisfaction survey does not back a
   specific numeric reduction claim.

5. Score the strongest matching evidence as:
   - STRONG: peer-reviewed RCT or controlled study, n>=50, independent funding or
     vendor funding independently confirmed, replicated by a second study.
   - MODERATE: controlled or feasibility study but small, single-site, unreplicated,
     or vendor-funded without independent confirmation.
   - WEAK: uncontrolled pilot, self-report, case series, or a related-but-not-matching
     outcome.
   - NONE FOUND: no matching trial or publication located.

6. If two matching studies disagree, do NOT average them — say so explicitly and
   use a "Mixed/contradictory evidence" verdict instead of a score.

7. If you cannot actually search ClinicalTrials.gov or PubMed (no web access), STOP
   and tell me that directly. Give me the exact search queries to run myself on
   clinicaltrials.gov and pubmed.ncbi.nlm.nih.gov, and I will paste the results back
   to you. Do not invent a study, NCT number, PMID, or finding under any circumstances.

Give me your answer in this exact format:

## Claim checked
"<exact claim>" — <product>, source: <where it came from>

## Evidence found
A table: Source (NCT#/PMID) | Design | n | Funder | Outcome measured | Matches claim? (Yes/Partial/No)
If a database returned nothing, say so as a row: "No matching records found in
ClinicalTrials.gov" (or PubMed/PMC).

## Methodology score: Strong / Moderate / Weak / None found

## Verdict
One of: Independently replicated / Small controlled pilot / Unreplicated vendor-funded
study / Unreplicated self-report, no independent study found / No evidence found /
Mixed or contradictory evidence — plus a 2-3 sentence plain-language explanation
citing the specific evidence row(s) that drove this.

## Caveats
Anything limiting confidence: search access unavailable, conflicting studies, or the
claim being too vague to match to one specific outcome.

Rules you must follow:
- Never call the claim "false," "a lie," or "fraudulent" — you are scoring the
  evidence, not the vendor's honesty.
- Never let the vendor's own press release or product page count as a row of
  supporting evidence in the table — it is the thing being checked, not proof of itself.
- Always flag vendor funding explicitly. Vendor funding alone doesn't disqualify a
  study, but it blocks a "Strong" score without independent confirmation.
- If the claim is too vague to tie to one measurable outcome (e.g. "residents love it"),
  say that plainly instead of forcing a score onto it.
```

## What you get back

A short, sourced report: the claim restated, a table of every matching trial/study found (with NCT numbers and PMIDs you can look up yourself), a one-word-ish methodology score, a plain-language verdict, and any caveats about search limitations or conflicting evidence. You should be able to hand this directly to a purchasing committee or cite it in a report.

## What this will not do

- It will not tell you a product is "good" or "bad" overall — only whether this one claim has real evidence behind it.
- It will not catch every study ever published — search terms matter; if the first pass finds nothing, try the product's generic/academic name (e.g. "Intuition Robotics" instead of "ElliQ") and resubmit.
- It will not maintain history across claims or products — each run is independent. If you're tracking many claims over time, you want the standing registry this skill is a piece of, not repeated one-off runs.
