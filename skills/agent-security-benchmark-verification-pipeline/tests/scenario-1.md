# Scenario 1: Self-reported "100% prevention" claim, no methodology

## Setup
A security-engineering lead at a mid-size fintech is shortlisting an agent-guardrail vendor ("SentinelAgent") before a Q1 purchase decision. She pulls the following paragraph from the vendor's product page and pastes it into the skill:

> "SentinelAgent achieves a 100% unsafe-action prevention rate across 22 agentic scenarios, demonstrating best-in-class protection for autonomous AI deployments. Our internal red team designed the scenarios to reflect real-world attack patterns."

She also tells the skill: "What decision rides on it: deciding whether to buy SentinelAgent over our other finalist, which only claims 94% but links to a public dataset and an AIUC-1 audit."

## Expected behavior
Running the Procedure in SKILL.md, the output should:
1. **Claim as stated**: correctly extract "100% unsafe-action prevention," "22 agentic scenarios," quoted.
2. **Verifiability Rating**: UNVERIFIABLE — no dataset link, no third-party auditor named, "internal red team" is self-reported with nothing external to check.
3. **Red flags found** should include at minimum: suspiciously perfect metric (100%, no confidence interval), no linked dataset/scenario list, no stated adversary/threat model detail beyond "real-world attack patterns" (too vague to be a definition), vague methodology ("internal red team designed" — no run count, no exclusions disclosed). Should NOT claim harness conflation unless the pasted text actually suggests wrapper/retry behavior (it doesn't here) — flags present must be ones genuinely supported by the pasted text, not padded to hit a quota.
4. **Reconstruction sketch**: should state this is NOT reconstructable today — no scenario list, no adversary definition, internal-only red team — and name specifically what's missing.
5. **Questions to ask the vendor**: should include something like "can you share the 22 scenario descriptions and scoring rubric," "was this measured over multiple independent runs or a single pass," "can an external party review or reproduce this test."
6. **Bottom line**: should explicitly say this claim alone is NOT sufficient grounds for the purchase decision as stated, and should note the comparison context (the 94%-with-AIUC-1-audit competitor) makes the self-reported 100% claim weaker, not stronger, as a decision input.

## Pass/fail criteria
- PASS if: Verifiability Rating is UNVERIFIABLE; at least 3 genuinely-applicable red flags are listed (not padded with inapplicable ones); the reconstruction sketch says "not reconstructable" with specific missing pieces named; at least 3 vendor questions are produced, each tied to a named red flag; the bottom line explicitly declines to treat the claim as sufficient for the purchase decision; no language anywhere implies the skill actually tested or reproduced SentinelAgent's tool.
- FAIL if: the rating is VERIFIABLE or PARTIALLY VERIFIABLE; red flags are generic/templated rather than tied to this claim's actual text; the output implies an independent re-run happened; the bottom line treats "100%" as reassuring without qualification; fewer than 3 vendor questions are produced.
