---
name: ai-safety-claim-verifier-registry
description: First-pass conflict-of-interest and calibration check on an AI-safety claim or "independent" evaluator endorsement — surfaces funding/affiliation ties to the lab being evaluated and timing proximity to that lab's corporate events, sourced-only, no verdict. Use before citing, amplifying, or acting on a safety claim about a frontier AI lab.
---

# AI Safety Claim Verifier

## When to use this

Use this the moment you encounter a public AI-safety claim or "independent" evaluator endorsement you're about to cite, quote, amplify, or rely on — a press release, a quoted expert in a news article, an HN/X post, a vendor's safety-compliance pitch — and want a sourced first-pass read on whether the claim's author has an undisclosed financial or structural tie to the lab being evaluated, before you repeat it as if it came from a neutral party.

This is a first-pass triage tool, not a finished investigation. It tells you whether a deeper look is warranted and hands you the starting sources for one; it does not adjudicate whether the underlying safety claim is true.

## Inputs

**Data source**: Manual — the user pastes (1) the claim text itself, (2) the name of the organization or individual making the claim, (3) the name of the lab or product the claim is about, and (4) any funding/partnership language the user has already turned up on their own. The skill then performs its own targeted web and public-filing lookups on top of that — it does not require the user to have already done the research, only to name who said what about whom.

If the user has none of items 3-4 beyond the claim and claimant name, proceed anyway — flag the gaps explicitly in the output rather than refusing.

## Procedure

1. **Parse the inputs.** Identify: the claimant (org or individual), the claim's substance in one sentence, and the lab/product being evaluated. If the claimant is an individual, also identify their primary organizational affiliation (employer, board seat, founder role) — ties attach to organizations more often than people.

2. **Classify the claimant.** Determine whether it is: a registered US nonprofit, a for-profit company, a government body (e.g., UK AISI, US CAISI), an academic lab, or an unaffiliated individual. This determines which lookups apply.

3. **Pull the funding/affiliation picture.**
   - If a US nonprofit: search ProPublica's Nonprofit Explorer (`https://projects.propublica.org/nonprofits/search?q=<org name>`) for its EIN and most recent Form 990 — note total revenue, largest listed grants/contributions, and any officers/board members shared with the lab being evaluated or with that lab's known funders.
   - For any claimant type: web-search `"<claimant>" "<lab>" (grant OR partnership OR funding OR "board member" OR "co-founder" OR consulting)` and separately `"<claimant>" conflict of interest policy` to find any self-disclosed COI statement.
   - Note explicitly which of these searches returned nothing — absence of a found tie is not the same as a confirmed absence of one.

4. **Check timing proximity.** Search for the evaluated lab's corporate events (funding round, IPO filing, major model launch, regulatory filing) within roughly 30 days before or after the claim's publication date. If one exists, note it as a timing-proximity flag — explicitly labeled as correlation only, never framed as motive or causation.

5. **Check track record, if the user supplied or the skill finds a prior claim by the same claimant.** Search the AI Incident Database (`https://incidentdatabase.org`) and general news for any incident involving the evaluated lab that occurred after this claimant previously cleared or downplayed a risk from that lab. Only include this section if a genuinely matching prior claim exists; otherwise state "no prior claim found to check."

6. **Rate completeness**, not truth: HIGH (990 found, COI policy found or absence confirmed, timing checked), MEDIUM (one or two of those missing), LOW (claimant is opaque — foreign entity, private company, or individual with no public filings — most lookups came back empty).

7. **Write the dossier** in the Output format below. Every factual line must carry an inline source link or citation; any line without one is removed or rewritten as an explicit "not found."

## Output format

```
## Claim Under Review
<one-sentence restatement of the claim> — claimed by <claimant>, about <lab>, dated <date if known>

## Claimant Profile
<Entity type, and primary affiliation if an individual>

## Funding & Affiliation Ties Found
- <tie 1, with source link/citation>
- <tie 2, with source link/citation>
(or: "No ties found in a 990 search + web search for grants/partnerships/board overlap between <claimant> and <lab>, as of <date checked>.")

## Timing Proximity
<Corporate event at <lab> on <date>, claim published <date>, gap of <N> days — flagged as correlation only, not causation.>
(or: "No corporate event at <lab> found within 30 days of this claim.")

## Track Record Check
<Prior claim, what it said, what the Incident Database or news shows since — with links>
(or: "No prior claim by this claimant found to check.")

## Completeness Rating
HIGH | MEDIUM | LOW — <one line on which lookups returned results vs. came up empty>

## Sources
<every link cited above, deduplicated>

## What This Does Not Tell You
<one line reiterating that a found tie is disclosure, not disqualification, and that an absence of a found tie means the search came up empty, not that no tie exists>
```

## Guardrails

- **Never issue a verdict.** Never say a claim is "compromised," "biased," or "untrustworthy" — report only what was found and let the reader judge. This mirrors the project's sourced-only, no-adjudication editorial policy; violating it turns a defensibility tool into a liability.
- **Never fabricate a tie, filing figure, or date.** If a 990 can't be located or a search returns nothing, say so explicitly — do not infer, estimate, or round from memory.
- **Never present timing proximity as motive.** A claim published near a funding round is a flagged correlation, nothing more — state this constraint in the output every time the section is non-empty.
- **Never skip the "what came up empty" disclosure.** A clean-looking dossier with no ties found must say which specific searches were run and returned nothing, not just "no ties found" — an empty search and a confirmed absence look identical to a careless reader otherwise.
- **Never treat an individual's affiliation as the whole picture.** Always also check their primary organization, since ties (grants, board seats) usually attach there even when the claim is attributed to a named person.
- **Never skip the Completeness Rating.** An opaque claimant (private company, foreign entity, unaffiliated individual) should come back LOW, not silently omitted — a missing rating is itself a false signal of thoroughness.
