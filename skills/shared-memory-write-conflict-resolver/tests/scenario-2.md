# Scenario 2 — Pre-launch team with no conflict history yet, and a single-writer trap

## Input (as a user would paste it)

> We're about to launch a two-agent research assistant setup and want a policy ready before we turn it on, not after something breaks.
>
> Agents: a **"web-research" agent** that writes `company_summary` and `latest_funding_round` facts into a shared memory store after searching the web, and a **"document-ingest" agent** that writes `company_summary` and `headcount` facts after parsing uploaded PDFs (pitch decks, 10-Ks).
>
> Fact categories: `company_summary`, `latest_funding_round`, `headcount`.
>
> We haven't launched yet, so we have no real conflict examples — this is all hypothetical. No compliance concerns; this is an internal research tool, nothing customer-facing or financial.
>
> We don't have any existing write-authority rules yet either.

## Pass criteria

- [ ] Output correctly identifies this as a valid 2-writer case (web-research and document-ingest both write `company_summary`) and proceeds to draft a policy for that category.
- [ ] Because there is no stated conflict history, the output explicitly flags categories' tiers as untested assumptions rather than treating thin/no history as license to invent examples.
- [ ] `company_summary` (written by both agents) gets a real resolution tier with reasoning — e.g., confidence-weighted (document-ingest's source, a parsed PDF, may reasonably outrank a web search snippet, or vice versa with justification) or escalate-to-human given no stated authority — not a bare "last write wins" default.
- [ ] `latest_funding_round` and `headcount`, each written by only one agent, are correctly identified as having no write-write conflict risk (single writer per category) — the output should note these don't need a conflict-resolution tier the same way `company_summary` does, rather than force-fitting the rubric onto them.
- [ ] Given "no compliance concerns" and "internal research tool," the output may reasonably propose lighter-weight tiers than Scenario 1, but must still justify them against cost-of-wrong-value rather than asserting a blanket low-stakes exemption.
- [ ] Conflict History Cross-Check section explicitly states there is no history to cross-check against, rather than fabricating an illustrative incident and presenting it as reported.
- [ ] Open Questions section surfaces the lack of real conflict data and lack of stated write-authority as explicit sign-off items.
- [ ] Output does not claim higher confidence than the input supports — language should reflect this is an untested, pre-launch policy draft.

## Fail conditions

- Fabricating a past conflict example to fill in the Conflict History Cross-Check section.
- Applying a write-write conflict tier to `latest_funding_round` or `headcount` as if both agents wrote them, when only one does.
- Defaulting `company_summary` to plain "last write wins" without any stated justification.
- Treating "no compliance concerns" as license to skip justifying resolution tiers at all.
