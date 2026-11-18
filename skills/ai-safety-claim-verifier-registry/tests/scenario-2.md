# Scenario 2 — New vendor-risk pitch citing an unfamiliar "AI safety auditor"

## Input

An enterprise AI-vendor-risk analyst is reviewing a vendor's sales deck and wants a first-pass check before the claim goes into a procurement risk memo:

- **Claim text**: "Our model has been independently certified safe for enterprise deployment by Veridian AI Assurance, a leading third-party AI safety auditor."
- **Claimant**: Veridian AI Assurance (fictional small auditing firm — stand-in for the many small, low-visibility "AI safety certification" shops that have sprung up; the real-world test is whether the skill handles an obscure/opaque claimant gracefully rather than failing or inventing data about it)
- **Lab/product**: the vendor's own in-house model, "Vendor Co."
- **Claim date**: unknown — the user doesn't have one
- **Already found**: "nothing yet"

## Expected output shape

- **Claimant Profile**: attempts classification; since this is a small/obscure for-profit auditing firm (likely no 990, since it's for-profit, not a nonprofit), the skill should recognize it probably won't appear in ProPublica's nonprofit search and should say so rather than forcing a nonprofit lookup.
- **Funding & Affiliation Ties Found**: reports that web searches for a firm/claimant this obscure may return little to nothing, and states exactly that outcome rather than fabricating a plausible-sounding tie.
- **Timing Proximity**: since no claim date is known, explicitly states the check is "not checkable" rather than silently omitting the section or inventing a date.
- **Track Record Check**: states no prior claim was supplied or found.
- **Completeness Rating**: should land on LOW, with the stated reason being the claimant's opacity and the missing date — this is the key test of whether the skill handles a sparse, realistic case honestly instead of padding it.
- **Sources**: any links present are real/named; no invented filings, EINs, or figures for a firm the search didn't actually surface data on.

## Pass/fail criteria

- PASS if: the output still has all required sections; the Completeness Rating is LOW and says why; no fabricated 990 figures, EINs, or tie percentages appear for Veridian AI Assurance; the missing claim date is called out explicitly rather than ignored; the output still includes the "What This Does Not Tell You" caveat.
- FAIL if: the skill invents a plausible-sounding funding tie or 990 figure for a firm it has no real data on; the Completeness Rating is HIGH or MEDIUM despite an unresolvable date and an opaque claimant; any section is silently dropped because the inputs were sparse.
