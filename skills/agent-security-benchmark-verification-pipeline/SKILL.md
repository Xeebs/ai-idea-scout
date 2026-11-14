---
name: agent-security-benchmark-verification-pipeline
description: One-shot due-diligence check on a single self-reported agent-security/guardrail benchmark claim (e.g. "100% unsafe-action prevention across 22 scenarios") — flags methodology red flags and rates how verifiable the claim actually is, before a buyer relies on it in a purchase decision.
---

# Agent-Security Benchmark Claim Due-Diligence Check

## When to use this
Use this the moment someone is evaluating an AI agent-security, guardrail, or "agentic safety" product/tool and has a specific published benchmark claim in front of them — a vendor blog post, a README metrics table, a one-pager, or a paper excerpt — and wants to know before a purchase or adoption decision: "is this claim trustworthy," "can I believe this number," or "what should I ask the vendor before I rely on this." This is a one-shot reasoning check on one claim at a time, not a monitoring service and not an actual re-execution of the vendor's tool — it does not run code, does not stand up a sandbox, and does not produce a measured delta against the vendor's number. If the user wants the claim actually re-run against reconstructed scenarios in an isolated environment, that is a separate, heavier engineering effort this skill cannot perform; say so explicitly rather than implying the check is a substitute for it.

## Inputs
**Data source**: Manual — the user pastes or links the specific vendor claim (a URL, a copied paragraph, a README table row, a paper excerpt) they want checked. This skill never crawls vendor sites, GitHub, or arXiv on its own and never fabricates a claim's wording from memory — if the user names a vendor/tool without pasting the actual claim text, ask them to paste or link the exact passage before proceeding.

Required from the user:
1. **The claim text itself** — pasted verbatim or as a working link the user has already fetched the content of. Do not proceed on a paraphrase ("they say they're basically 100% safe") — ask for the exact wording.
2. **What decision rides on it** — e.g. "deciding whether to buy this over a competitor," "deciding whether to deploy without additional review." This calibrates how hard the output pushes back.

Optional, if available:
3. A competing or baseline claim to compare methodology against.
4. Any vendor documentation link beyond the claim itself (methodology appendix, dataset link, audit report).

## Procedure
1. **Extract the claim's structure** from the pasted text: the headline metric (e.g. "100% unsafe-action prevention," "0.00% violation rate"), the stated scenario/test count, the named benchmark or dataset (if any), and any stated methodology detail (who ran it, how scenarios were generated, what counts as a "pass").
2. **Check for a traceable source**, using only what the user supplied (do not browse unless the user has provided a link and asked you to fetch it): does the claim link to a public dataset, a named third-party benchmark suite, an accredited-auditor report (e.g. AIUC-1/Schellman-style), or is it entirely self-measured and self-reported with no external check named at all? Self-measured + self-reported with zero external reference is the single strongest red flag.
3. **Run the claim against this red-flag checklist**, marking each present/absent/unclear:
   - **Vague or rounded scenario count** (e.g. "dozens of scenarios," "a comprehensive test suite") instead of an exact, enumerable number.
   - **No linked dataset or scenario list** — the claim names a count but nothing a third party could inspect or reproduce.
   - **Suspiciously perfect metric** (100%, 0.00%, or a round number with implausible precision) with no stated confidence interval or run-to-run variance.
   - **Harness/scaffolding conflation** — the claim attributes the result to "the model" or "the agent" when a wrapper, retry logic, or best-of-N sampling likely did the work, and this isn't disclosed.
   - **Metric choice obscures consistency** — reporting a single pass/success rate with no mention of how many independent runs or attempts produced it.
   - **No stated adversary/threat model** — "unsafe action" or "violation" isn't defined, so it's unclear what the tool was actually tested against.
   - **No disclosed exclusions** — scenarios dropped, retried, or excluded from the denominator aren't mentioned one way or the other.
   - **Benchmark-to-deployment mismatch** — the test scenarios look generic/public rather than resembling the buyer's actual use case.
4. **Attempt a lightweight reconstruction sketch**: based only on what's disclosed, state in 2-3 sentences whether a third party could faithfully reproduce this test today (full/partial/not reconstructable), and name exactly what's missing (e.g. "no scenario list, no adversary definition, no run count — reconstruction would require generating a new scenario set from scratch, which is not the same test").
5. **Assign a Verifiability Rating**: `VERIFIABLE` (public dataset or accredited third-party audit named and linkable), `PARTIALLY VERIFIABLE` (some methodology disclosed but key details missing), or `UNVERIFIABLE` (self-reported, no external reference, insufficient detail to reconstruct). Tie between partial and unverifiable resolves to UNVERIFIABLE — the rating should err toward skepticism, mirroring the buyer-protective purpose of this check.
6. **Draft 3-5 specific follow-up questions** the buyer should ask the vendor directly, each tied to a specific red flag found in step 3 (e.g. "Can you share the exact list of the 22 scenarios and how each was scored?" not a generic "please be more transparent").

## Output format
A single due-diligence note, in this order:
1. **Claim as stated** — the extracted headline metric and scenario count, quoted.
2. **Verifiability Rating** — VERIFIABLE / PARTIALLY VERIFIABLE / UNVERIFIABLE, one-line justification.
3. **Red flags found** — bullet list from step 3, each flagged item with a one-sentence explanation of why it matters for this specific claim; omit flags that don't apply rather than listing them as "N/A."
4. **Reconstruction sketch** — the 2-3 sentence assessment from step 4.
5. **Questions to ask the vendor** — the 3-5 questions from step 6, numbered.
6. **Bottom line** — one sentence stating plainly whether this claim alone is sufficient grounds for the stated decision (step 2's "what decision rides on it"), or whether it should be treated as marketing until independently verified.

## Guardrails
- Never state or imply that this skill has independently re-run, reproduced, or tested the vendor's tool — it has only assessed whether the *claim as written* is checkable. That re-run is a separate, infrastructure-heavy effort (sandboxed agent execution), not something this one-shot text check can do.
- Never invent methodology details, scenario contents, or dataset names that aren't present in the pasted claim or user-supplied links — if something is unknown, say "not disclosed," never fill the gap with a plausible-sounding guess.
- Never soften an UNVERIFIABLE rating to make the output feel more useful — the entire value of this skill is that it's willing to say "there isn't enough here to trust this," even for a well-known vendor.
- Never treat a vendor's reputation, funding, or market position as evidence for a claim's methodology quality — assess only what's in the claim text itself.
- If the user pastes a paraphrase instead of the claim's exact wording, do not proceed with the full checklist — ask for the verbatim text or link first, since red-flag detection on a paraphrase is unreliable and could clear or condemn a claim unfairly.
