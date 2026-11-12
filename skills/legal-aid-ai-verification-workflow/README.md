# Legal-Aid Intake Verification Workflow

A paste-in prompt template for checking an AI-drafted legal-aid intake summary, eligibility assessment, or benefits/immigration form against the actual program rules or statute text it's supposed to be based on — before a non-lawyer reviewer or junior pro bono volunteer relies on it with a client.

This is **not** a case-law citation checker (is this case real, does it say what's claimed — that's a separate, already-solved problem with dedicated commercial tools). This is for checking factual and eligibility claims in intake-type drafts against program rules, which today still gets checked by a human reading line by line with nothing structured to help.

## When to use this

You have a draft produced by an AI intake chatbot — any chatbot: a legal-aid org's own tool (like Navi or LIA), a pro bono project's chatbot (like PoBot, built on Open Chat Studio), or just a general-purpose AI conversation — and you need to check whether its factual and eligibility claims are actually backed by the governing rules before anyone acts on it. You are not expected to be a lawyer; you just need to see, side by side, which claims are grounded and which ones need an attorney to look at.

## What you need to paste in

1. **The draft itself** — the full text of the AI-drafted intake summary, eligibility assessment, or form content. If it's long, you can paste just the section you want checked, clearly marked.
2. **The source rules** — the actual text of the statute sections, regulation excerpts, or program eligibility guide the draft's claims should be based on. This has to be the real text, not a citation or a link. If you only have a citation, go get the actual text first — the whole point of this tool is not using an AI's general knowledge as a stand-in for the rule that actually governs this case.

Optional: tell it which claims matter most if the draft is long (e.g., "just check the income and residency parts").

If you don't have both of these ready, the tool should ask you for them rather than guessing — that's intentional, not a bug.

## The prompt

Paste this into any AI chat tool along with your draft and source text:

```
I need you to verify an AI-drafted legal-aid document against specific source rules. I am a non-lawyer / junior reviewer checking this before it's relied on — I need a structured, claim-by-claim check, not a general opinion on whether it looks right.

Here is the AI-drafted document to verify:
[PASTE DRAFT HERE]

Here is the source text (statute/regulation/program eligibility guide) the draft's claims should be grounded in:
[PASTE SOURCE TEXT HERE]

Do the following:
1. Break the draft into discrete, numbered, checkable factual/eligibility claims (skip pure narrative statements that assert nothing checkable, but list those separately as excluded, don't just drop them).
2. For each claim, search ONLY the source text I pasted above — not your own general legal knowledge — for a passage that supports or contradicts it.
3. Classify each claim as:
   - SUPPORTED (quote the exact matching passage)
   - PARTIALLY SUPPORTED (a related passage exists but a number, condition, or category doesn't fully match — quote it and explain the gap)
   - UNSUPPORTED — NO MATCH FOUND (nothing in my pasted source addresses it)
   - CONTRADICTED (a passage directly contradicts the claim — quote it)
4. If a match is ambiguous, classify it PARTIALLY SUPPORTED rather than SUPPORTED — a missed error is worse than an extra flag.
5. Within everything that isn't SUPPORTED, separate hard-eligibility claims (income/asset thresholds, residency/citizenship status, deadlines, categorical exclusions) from softer narrative-adjacent claims, and list the hard-eligibility ones first — those are the ones that put a case at risk if wrong.
6. Never mark a claim SUPPORTED based on what you know generally about this area of law — only based on the text I pasted. If my pasted source doesn't cover a claim, that's UNSUPPORTED even if you happen to know the claim is correct.
7. Never give me a final "this client is eligible/ineligible" conclusion — just tell me which claims are grounded and which aren't. The eligibility call is the attorney's.
8. Don't check case-law citations — that's out of scope.

Output format:
# Verification Report
Claims extracted: [n] ([k] excluded as non-checkable — list them)

## Needs Attorney Review (hard-eligibility claims first)
[numbered list, each with classification, quoted source passage or "no match found", and why it's flagged]

## Supported Claims
[numbered list with quoted source passage for each]

## Excluded as Non-Checkable
[list]

## Summary
[counts by classification; how many of the flagged items are hard-eligibility]

## Scope Disclaimer
This only checks the draft against the source text I pasted — it does not confirm that text is current, complete, or the right jurisdiction. This is not a substitute for attorney judgment and does not decide eligibility. It does not check case-law citations.
```

## What a good result looks like

- Every single claim in the draft shows up with a classification — nothing silently passes through unflagged.
- Every quote attributed to the source text is actually from the text you pasted, not invented or pulled from general knowledge.
- Claims about income thresholds, residency/citizenship status, and deadlines are visibly prioritized at the top of the "needs review" list when they're flagged.
- The report never states a final eligibility conclusion — only claim-by-claim grounding status.
- If you didn't paste source text for some part of the draft, the tool says so instead of filling the gap from its own knowledge.

## What this doesn't do

It doesn't fetch the current statute for you, doesn't know if the text you pasted is out of date, doesn't check citations to actual case law, and doesn't replace an attorney's sign-off. It only tells you whether what's in the draft is actually backed by what you gave it to check against.
