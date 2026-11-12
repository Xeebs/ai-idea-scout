---
name: legal-aid-ai-verification-workflow
description: Checks an AI-drafted intake summary, eligibility assessment, or benefits/immigration form against the specific program rules or statute text it should be grounded in, and produces a claim-by-claim verification report flagging anything unsupported as needing attorney review. Use when a non-lawyer or junior pro bono reviewer has a chatbot-drafted output (from Navi, LIA, Open Chat Studio, or any other tool) that needs checking before it's relied on with a client — not for checking case-law citations, which is a different, already-solved problem.
---

# Legal-Aid Intake Verification Workflow

## When to use this
A legal-aid nonprofit, pro bono attorney, or trained non-lawyer reviewer has an AI-drafted document — an intake summary, an eligibility assessment, or a drafted benefits/immigration form — that was produced by a chatbot (any chatbot: Navi, LIA, PoBot/Open Chat Studio, a generic ChatGPT/Claude conversation) and now needs a human-reviewable check against the actual governing rules before anyone relies on it with a client. The reviewer is explicitly assumed to be a non-expert or junior volunteer who cannot independently re-derive the legal analysis from scratch but can confirm whether a specific sentence in the draft is actually backed by a specific sentence in the rule text.

Do not reach for this skill for case-law citation checking (does this case exist, is this citation accurate) — that is a mature, separately-solved problem with dedicated commercial tools (Clearbrief, CiteCheck AI, BriefCatch RealityCheck). This skill is scoped to checking factual/eligibility claims in intake-type drafts against program rules, statutes, or regulation text — a narrower and currently unserved gap.

## Inputs
**Data source**: Manual — the user pastes (a) the full text of the AI-drafted document to verify, and (b) the full text of the specific source rules it should be grounded in (the relevant statute sections, regulation excerpts, or the program's eligibility guide). Nothing is fetched automatically; this skill never uses its own general legal knowledge as a substitute for source text the user didn't provide.

Required:
1. **The draft** — the AI-drafted intake summary, eligibility assessment, or form content, pasted in full (or the specific section to verify, clearly marked).
2. **The source text** — the statute, regulation, or program eligibility-guide excerpts the draft's claims should trace back to. This must be the actual text, not a citation or a link — if the user only has a citation, ask them to paste the text before proceeding.

Optional:
3. A note on which claims matter most (e.g., "focus on the income and residency claims, not the narrative background") if the draft is long and the reviewer has limited time.

If either required input is missing, do not proceed and do not guess — ask for it. Producing a "verification" against law pulled from training knowledge instead of the text actually governing this case is the single most dangerous failure mode this skill exists to prevent.

## Procedure
1. **Extract claims.** Read the draft and break it into discrete, atomic factual or eligibility claims — each one a single checkable assertion (e.g., "Household income of $2,100/month qualifies under the 125% FPL threshold for a household of 3," "Client meets the continuous-residence requirement," "Client is exempt from the work-registration requirement due to disability"). Number each claim. Skip pure narrative/background statements that assert nothing checkable (e.g., "Client reported feeling anxious about the hearing date") — note in the output that these were excluded as non-checkable, don't just drop them silently.
2. **Search the source text per claim.** For each numbered claim, search only the pasted source text (never outside training knowledge) for the passage that would support or contradict it.
3. **Classify each claim:**
   - **SUPPORTED** — a source passage directly backs the specific claim as stated (same numbers, same conditions, same category). Quote the exact matching passage.
   - **PARTIALLY SUPPORTED** — a relevant passage exists but doesn't fully back the claim as stated: a number doesn't match, a condition in the source was dropped or altered in the draft, or the passage covers a related-but-not-identical scenario. Quote the passage and state exactly what doesn't line up.
   - **UNSUPPORTED — NO MATCH FOUND** — no passage in the pasted source text addresses this claim at all.
   - **CONTRADICTED** — a source passage exists and directly contradicts the claim as stated. This is the highest-priority flag; quote the contradicting passage.
4. **Bias toward caution on ambiguous matches.** If it's genuinely unclear whether a passage fully supports a claim, classify it PARTIALLY SUPPORTED, never SUPPORTED — a missed error (false negative) is worse than an over-flagged correct claim, per the project's own stated priority metric.
5. **Flag hard-eligibility claims for priority review.** Within the UNSUPPORTED, PARTIALLY SUPPORTED, and CONTRADICTED groups, separate claims about hard eligibility criteria (income/asset thresholds, residency/citizenship status, statutory deadlines, categorical exclusions) from softer narrative-adjacent claims — hard-criteria flags go first in the output, since getting one of those wrong is what actually puts a client's case at risk.
6. **Never silently pass a claim through.** Every single extracted claim appears in the output with a classification — there is no "looks fine, omitted" category.

## Output format
```
# Verification Report — <draft identifier/date>

Claims extracted: <n> (<k> excluded as non-checkable narrative — listed below)

## Needs Attorney Review (sorted: hard-eligibility criteria first)
1. [CONTRADICTED] Claim: "<claim text>"
   Source says: "<quoted passage>"
   Why flagged: <one line>
2. [UNSUPPORTED — NO MATCH FOUND] Claim: "<claim text>"
   Why flagged: no passage in the provided source text addresses this.
3. [PARTIALLY SUPPORTED] Claim: "<claim text>"
   Source says: "<quoted passage>"
   Gap: <what doesn't line up>

## Supported Claims
1. Claim: "<claim text>" — Source: "<quoted passage>"
...

## Excluded as Non-Checkable
- "<narrative statement>" — no factual/eligibility assertion to verify.

## Summary
<n> supported · <n> partially supported · <n> unsupported · <n> contradicted
<n> of the flagged items are hard-eligibility criteria — review these first.

## Scope Disclaimer
This report only checks the draft against the source text pasted into this conversation. It does not confirm that the pasted text is the current, complete, or correctly-jurisdiction-matched version of the rule — the reviewer must confirm that separately. This is not a substitute for attorney legal judgment and does not make an eligibility determination. It does not check case-law citations.
```

## Guardrails
- Never classify a claim as SUPPORTED using general/training-data legal knowledge — only the source text pasted in this conversation counts as support. If the pasted source doesn't cover a claim, that is UNSUPPORTED even if the claim happens to be legally correct.
- Never proceed without both the draft and the source text; never substitute a citation, a URL, or a paraphrase for the actual source text.
- Never produce a final eligibility conclusion ("this client is eligible/ineligible") — this skill verifies whether claims are grounded, not whether the client ultimately qualifies. That call belongs to the attorney.
- Never silently drop a claim from the report, and never mark an ambiguous match as SUPPORTED — when in doubt, flag it as PARTIALLY SUPPORTED so a human looks at it.
- Never treat this as a citation-checker for case law (is this case real, does it say what's claimed) — that's explicitly out of scope; redirect the user to a dedicated citation-checking tool for that task.
- Always include the scope disclaimer in every output — omitting it is how a reviewer ends up trusting a check that only ever covered what was pasted in, not the full current law.
