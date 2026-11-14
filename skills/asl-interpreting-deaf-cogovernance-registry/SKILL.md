---
name: asl-interpreting-deaf-cogovernance-registry
description: Scores a specific AI ASL interpreting vendor's published governance claims against a concrete Deaf co-governance bar (majority-Deaf authority, published decision power, responsiveness track record, reviewer compensation, data representation) and cites the exact evidence or gap for each. Use when a procurement reviewer (school district, hospital, court) is evaluating one named AI ASL interpreting vendor and needs a defensible pass/fail before signing a contract.
---

# AI ASL Interpreting Vendor Co-Governance Checklist

## When to use this
A procurement reviewer — a school district accessibility lead, hospital interpreter-services manager, court administrator — is actively evaluating one specific AI ASL interpreting vendor (e.g. Nagish, Sorenson, Silence Speaks, Signapse, or a newer entrant) and has that vendor's public materials and sales-call notes in hand. They need to know, before signing, whether the vendor's "Deaf-led" or "advisory committee" language reflects real decision-making authority or is self-reported marketing. This is a one-shot, per-vendor evaluation — it does not track a vendor over time or replace the standing public registry the parent idea describes; it's the fast checklist version a single buyer runs for a single procurement decision.

## Inputs
**Data source**: Manual — the reviewer pastes or links the vendor's published product pages, any governance/advisory-board disclosure pages, press releases naming an advisory committee, and their own notes from a sales call or RFP response. No API or connector exists for "a company's internal governance structure" — this stays Manual by design; a live feed could never verify whether a committee's stated authority is real.

Required for any run:
1. The vendor's name.
2. At least one piece of the vendor's own published material about governance, an advisory board, or Deaf involvement (a URL's text, a press release, an RFP answer, or a direct quote) — pasted, not just described.

Optional but strengthens the result:
3. The reviewer's notes from a sales call or vendor Q&A (direct quotes work best).
4. Any third-party evidence: Deaf community commentary (e.g. r/ASLinterpreters, NAD/RID statements), the EUD 15-principle ethical framework, or the Cambridge/Minderoo procurement report, if the reviewer has access to any of these and wants them weighed in.

If only the vendor's own marketing copy is provided with no specifics (no names, no structure, no process described), say so explicitly and score every criterion "claims but no evidence" rather than inferring detail that wasn't given.

## Procedure
1. **Confirm inputs.** If no vendor material was actually pasted — only a general impression ("they say they work with Deaf people") — ask for the literal text or a link before scoring anything. Every score must trace to quoted or clearly summarized source text, never to a paraphrase of what the reviewer assumes it says.
2. **Extract governance claims.** From the pasted material, pull out every distinct claim about Deaf involvement: named individuals, named committees/boards, described processes, any stated authority or veto power, any compensation mention, any dataset/signer-representation claim.
3. **Score each of the five criteria** as PASS / PARTIAL / CLAIMS-ONLY / NO-EVIDENCE, each with the specific quote or absence that justifies it:
   - **Majority-Deaf authority**: Is the governing or advisory body majority-Deaf by stated membership, not just "includes Deaf members"? PASS requires a stated count or ratio; PARTIAL if Deaf involvement is named but majority status is unclear; CLAIMS-ONLY if "Deaf-led" is asserted with no roster or ratio; NO-EVIDENCE if nothing is said.
   - **Published decision-making power**: Does the material state the body can block, veto, or require changes to a product decision — not merely "provide input" or "be consulted"? PASS requires explicit veto/approval language; CLAIMS-ONLY if "advisory" is used without any stated power; NO-EVIDENCE if governance isn't mentioned at all.
   - **Responsiveness track record**: Is there a cited, dated example of the vendor changing something because of Deaf-reviewer feedback (a changelog entry, a quote, a cited incident)? PASS requires a specific instance; CLAIMS-ONLY if "we listen to feedback" is asserted with no instance; NO-EVIDENCE if absent.
   - **Reviewer compensation/sustainability**: Does the material state whether Deaf advisors/reviewers are paid, and on what basis (stipend, salary, per-review fee)? Flag silence here explicitly — per the De Meulder et al. co-creation research, uncompensated "co-creation" risks tokenism even when well-intentioned. PASS requires a stated compensation structure; NO-EVIDENCE is the default absent any mention.
   - **Data/signer representation**: Does the vendor state anything about dataset diversity across signers, regional dialects, or who the training/evaluation data represents? PASS requires a specific claim with a concrete scope AND a stated breakdown (e.g. "40% of signers from the Southeast, published in our data card"); PARTIAL if specific but self-admittedly incomplete (names a concrete scope — a count of regions, a number of signers — but states no further breakdown is published); CLAIMS-ONLY for vague "diverse data" language with no scope at all; NO-EVIDENCE if unaddressed.
4. **Never infer a PASS from silence.** If a criterion isn't addressed anywhere in what was pasted, the score is NO-EVIDENCE, not an assumed failure or an assumed pass — distinguish "the vendor said nothing" from "the vendor said no."
5. **Weigh sales-call notes and third-party evidence, if given, as corroboration or contradiction — never as a substitute for the vendor's own published material.** A verbal assurance from a sales rep with no document or timeline behind it never moves a score up (e.g. "we're working on it" stays at whatever the written material alone supports). Third-party evidence (community commentary, a former-employee claim, an independent framework) that contradicts or qualifies a criterion the vendor scored PASS or PARTIAL on must be surfaced as an explicit caveat next to that score or in the Overall Read — never silently dropped just because the reviewer supplied it separately from the vendor's own material.
6. **Write one gap sentence per criterion scored below PASS**, naming exactly what additional document, statistic, or named individual would move it to PASS (e.g. "would need a stated roster showing >50% Deaf membership on the advisory body").
7. **Roll up an overall read**: count PASS / PARTIAL / CLAIMS-ONLY / NO-EVIDENCE across the five criteria and state plainly whether the vendor's public claims, as given, support a "co-governance" characterization or amount mostly to self-reported marketing language — without rendering a verdict on whether to sign the contract, which is the reviewer's call, not this checklist's.
8. **Always close with a Limits section** (see Output format) — every run, regardless of score.

## Output format
```
## Vendor: <name>

| Criterion | Score | Evidence or gap |
|---|---|---|
| Majority-Deaf authority | PASS/PARTIAL/CLAIMS-ONLY/NO-EVIDENCE | <quote or "not addressed in material provided"> |
| Published decision power | ... | ... |
| Responsiveness track record | ... | ... |
| Reviewer compensation | ... | ... |
| Data/signer representation | ... | ... |

## What Would Move Each Gap to PASS
1. [Criterion] — <specific document/statistic/named detail needed>
(one per criterion scored below PASS)

## Overall Read
<2-4 sentences: tally of scores, and whether the claims as given support "co-governance" or read as self-reported marketing. No sign/don't-sign recommendation.>

## Limits
- This reads only the material you pasted — a vendor may have governance detail published elsewhere that wasn't included, and a NO-EVIDENCE score here means "not found in what was given," not "does not exist."
- This is not an audit. Nothing here independently verifies that a stated committee roster, veto power, or compensation structure is real — it only checks whether the vendor's own published material makes the claim and how specifically.
- This is a one-shot, single-vendor, point-in-time check. It does not track whether a vendor's claims change over time, and it does not replace a standing, independently-reviewed public registry maintained by Deaf reviewers (the kind the parent project describes) — treat a PASS here as "the claim is specific," not "the claim is Deaf-verified."
- Never treat this checklist's overall read as a procurement decision — that's the reviewer's and their institution's call, weighing cost, timeline, and risk tolerance alongside this.
```

## Guardrails
- Never score a criterion PASS based on the vendor's reputation, name recognition, or general goodwill — only on specific, cited claims in the material actually provided.
- Never collapse "advisory committee" language into "co-governance" — advisory and decision-making authority are different claims, and conflating them is the exact failure mode this checklist exists to catch.
- Never fabricate a quote, statistic, or named individual not present in the pasted material.
- Never render a sign/don't-sign recommendation — this checklist scores specificity of claims, not contract risk overall; that judgment belongs to the reviewer and their institution.
- Never let a NO-EVIDENCE score silently read as a failure in the output — state explicitly that it means absence of information, not a confirmed negative.
- If the reviewer supplies only vague marketing copy, say so and score every criterion accordingly rather than filling in plausible-sounding detail.
