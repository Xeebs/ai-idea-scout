# AI Safety Claim Verifier

A paste-in prompt for any AI chat tool with web search (ChatGPT with browsing, Claude with web search, Perplexity, Gemini, etc.). It does a sourced, first-pass conflict-of-interest and timing check on an AI-safety claim or "independent" evaluator endorsement before you cite, quote, or amplify it — surfacing financial/structural ties to the lab being evaluated and whether the claim landed suspiciously close to that lab's own corporate events. It never tells you whether the underlying safety claim is true, and it never issues a verdict on the claimant — only what it found, sourced, with gaps named explicitly.

## When to use this

Use it the moment you're about to cite, quote, repost, or act on a public AI-safety claim — a press release, a quoted "independent" expert, an HN/X post, a vendor's safety-compliance pitch — and you want to know first whether its source has an undisclosed tie to the lab it's evaluating, or whether it showed up suspiciously close to that lab's IPO, funding round, or product launch.

This is a triage tool. It tells you whether the claim is worth a deeper investigative look and hands you the starting sources for one. It does not replace that deeper look, and it does not adjudicate whether the safety claim itself is correct.

## What to hand it

Paste this prompt, then fill in:

1. **The claim text** — the actual sentence or paragraph being evaluated.
2. **Who made it** — the organization or individual's name.
3. **Which lab/product it's about** — e.g., Anthropic, OpenAI, a specific model.
4. **Anything you've already found** — any funding, partnership, or affiliation language you've personally turned up (optional — if you have nothing, say "nothing yet" and the tool will do its own search from scratch).

If you don't know the claim's publication date, say so — the timing-proximity check becomes "not checkable" rather than being skipped silently.

## The prompt

```
You are doing a first-pass conflict-of-interest and timing check on an AI-safety claim. This is triage, not a finished investigation — report only what you find, with sources, and never issue a verdict on whether the claimant is biased or the claim is true.

INPUTS:
- Claim text: <paste here>
- Claimant (org or individual): <name>
- Lab/product the claim is about: <name>
- Claim date (if known): <date or "unknown">
- Anything already found about ties or funding: <paste or "nothing yet">

Do the following, using web search:

1. Classify the claimant: US nonprofit, for-profit company, government body, academic lab, or unaffiliated individual. If an individual, also identify their primary organizational affiliation (employer, board seat, founder role).

2. Search for funding and affiliation ties between the claimant and the evaluated lab:
   - If a US nonprofit, look up its IRS Form 990 via ProPublica's Nonprofit Explorer (projects.propublica.org/nonprofits) — note total revenue, largest grants/contributions, and any officers or board members shared with the lab or the lab's known funders.
   - Web-search for: "<claimant>" "<lab>" grant OR partnership OR funding OR "board member" OR co-founder OR consulting
   - Web-search separately for: "<claimant>" conflict of interest policy
   - State explicitly which of these searches came back empty — an empty search is not the same as a confirmed absence of a tie, and you must say so.

3. Check timing proximity: search for the evaluated lab's corporate events (funding round, IPO filing, major product launch, regulatory filing) within roughly 30 days of the claim's date. If one exists, flag it as a timing correlation only — never state or imply it as motive or causation.

4. Check track record: if there's a prior claim by the same claimant about the same lab, search the AI Incident Database (incidentdatabase.org) and general news for any incident at that lab since the prior claim. If no prior claim exists to check, say so plainly.

5. Rate completeness (not truth): HIGH if the 990/COI-policy search and the timing check both returned usable results, MEDIUM if one came back empty, LOW if the claimant is opaque (private company, foreign entity, or individual with no public filings) and most searches returned nothing.

6. Output in exactly this structure:

## Claim Under Review
<one-sentence restatement> — claimed by <claimant>, about <lab>, dated <date or "unknown">

## Claimant Profile
<entity type, and primary affiliation if an individual>

## Funding & Affiliation Ties Found
- <tie with source link>
(or: "No ties found in a 990 search + web search for grants/partnerships/board overlap, as of today.")

## Timing Proximity
<event, date, gap in days — labeled correlation only>
(or: "No corporate event found within 30 days of this claim.")

## Track Record Check
<prior claim, what it said, what's happened since, with links>
(or: "No prior claim found to check.")

## Completeness Rating
HIGH | MEDIUM | LOW — <one line explaining which searches returned results>

## Sources
<every link cited above>

## What This Does Not Tell You
A found tie is disclosure, not disqualification. An absence of a found tie means the search came up empty, not that no tie exists. This does not evaluate whether the underlying safety claim is correct.

Never skip a section — if a lookup found nothing, say so in that section rather than omitting it.
```

## Guardrails (read before you trust the output)

- The tool never tells you a claim is biased, compromised, or false — only what ties and timing it found, sourced. Treat any output that issues a verdict as a sign the prompt wasn't followed correctly.
- A clean "no ties found" result means the specific searches run came up empty, not that no tie exists anywhere. Check the Completeness Rating before treating a clean result as reassuring.
- Timing proximity to a funding round or IPO is a flag for your own further scrutiny, never evidence of motive by itself.
- This tool is weakest on opaque claimants — private companies, foreign entities, or individuals with no public nonprofit filings. A LOW completeness rating there is expected, not a bug; don't push the model to "fill in the gaps" with speculation.
- This checks the claimant's ties and timing, not the scientific/technical merits of the safety claim itself — those require separate domain expertise.
