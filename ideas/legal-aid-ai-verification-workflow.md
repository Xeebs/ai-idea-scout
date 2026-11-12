# VerifyAid: A Structured Verification Workflow for Non-Expert Legal-Aid Reviewers

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P4
- **Maturity verdict**: PARTIAL — mature citation-verification products exist (Beyond Assured/Benchly, CiteSentinel, Clearbrief, BriefCatch RealityCheck, CiteCheck AI/LawDroid) but every one targets law-firm/court case-law citation checking; none is adapted for non-expert legal-aid-nonprofit reviewers verifying plain-language intake and form-drafting output, where the verification step today is manual, ad hoc, line-by-line attorney review.
- **Format**: BOTH

## The Gap
Across every example in the digest — Lone Star Legal Aid's "Navi," NC Legal Aid's "LIA," PoBot (built by Linklaters Asia pro bono attorneys for Migrasia) — the AI chatbot generates intake guidance or draft forms, and a pro bono attorney manually re-checks it line by line before it's relied on. A Linklaters pro bono partner is quoted saying "much of the project's time... [is] dedicated to verifying the AI's findings." That manual bottleneck is the actual constraint on how many cases these programs can serve, not the chatbot's drafting quality.

## The Project
A verification-workflow tool purpose-built for the legal-aid reviewer persona: a non-lawyer or junior pro bono volunteer who needs to check an AI-drafted intake summary, eligibility assessment, or form against the underlying statute/regulation/program rules without doing a full independent legal analysis. The tool takes the AI's draft output plus the source documents it should be grounded in (the specific benefit program's eligibility rules, the specific visa category's requirements), highlights each factual/eligibility claim in the draft, shows the reviewer the exact source passage that should support it side by side, and flags claims with no supporting passage found as "unverified — needs attorney review" rather than silently passing them through. It is explicitly scoped to intake/eligibility/form-drafting verification, not case-law citation-checking (the commoditized, already-solved adjacent problem).

## Tangible Impact
**Population**: Legal-aid nonprofits and their pro bono attorney networks serving low-income clients in immigration, public-benefits, and domestic-worker cases — the Legal Services Corporation (LSC), which funded both Navi and LIA via Technology Initiative Grants, estimates roughly 92% of low-income Americans' civil legal needs go unmet or under-met annually, and the specific bottleneck this targets is the attorney-hours constraint limiting how many of those cases an AI-assisted intake program can actually process.
**Mechanism**: Today, every AI-drafted intake output requires a full manual attorney re-check because there's no structured way to see which claims are grounded and which aren't — this consumes the same scarce attorney hours the AI tool was meant to free up. A side-by-side claim-to-source verification view lets a reviewer confirm grounded claims in seconds and focus full attention only on the flagged unverified ones, cutting the review time per case.
**Measure**: (1) median minutes per case spent on manual verification before vs. after adoption, measured with a partner legal-aid org; (2) percentage of AI-drafted claims the tool correctly flags as unverified against a human-attorney-labeled gold set (false-negative rate on missed errors is the critical metric — a tool that misses an ungrounded claim is worse than no tool); (3) number of additional cases a given attorney-hour budget can process per month post-adoption.

## Why Now
LSC's continued Technology Initiative Grant funding for exactly this category of tool (Navi, LIA) and the explicit, named pain point from the PoBot/Linklaters case both landed in the last 30 days of community signal — legal-aid orgs are actively building the chatbot half of this and visibly struggling with the verification half, which is the precise moment to offer the missing piece rather than another chatbot.

## Skill Angle
A Claude Code skill version: given an AI-drafted intake summary or form, plus the source eligibility rules/statute text it should be grounded in, the skill extracts each factual or eligibility claim from the draft, searches the source text for a supporting passage, and returns a claim-by-claim verification report (supported/unsupported/partially-supported, with the matched source passage or an explicit "no match found"). This is the one-shot analysis task a reviewer runs per case — the project is the persistent tool that stores source documents, logs verification history across cases for audit purposes, and integrates with whatever chatbot platform (Navi, LIA, Open Chat Studio) the org already runs. The skill proves the verification-matching logic works before anyone commits to building the full audit-trail infrastructure.

## MVP Sketch
Scope to one legal domain (e.g., one state's public-benefits eligibility rules, since those are a bounded, enumerable rule set) and one draft type (eligibility-assessment summaries). Stack: a claim-extraction step (LLM call), a retrieval step against the source rules (simple embedding search over the statute/regulation text), and a side-by-side review UI. The validating experiment: run the pipeline against a set of past Navi- or LIA-style drafts with known attorney-corrected answers, and measure how often the tool correctly flags the claims the attorney actually had to correct.
## Risks & Open Questions
- Legal domains vary wildly in how "enumerable" their source rules are (benefits eligibility rules are fairly bounded; immigration case law is not), so the MVP's domain choice matters a lot for feasibility.
- Risk that a generic commercial citation-checker (Clearbrief, CiteCheck AI) can be configured/prompted to cover this use case well enough that building a dedicated tool is unnecessary — worth a direct trial against a real legal-aid intake draft before building.
- Legal-aid orgs are liability-sensitive; any tool claiming to "verify" legal content needs a clear scope disclaimer and probably legal review of the tool itself before any org adopts it.
- A false sense of security from an imperfect verifier could be worse than the current all-manual process — the false-negative rate on missed errors needs to be the primary gate before any pilot deployment, not an afterthought metric.
