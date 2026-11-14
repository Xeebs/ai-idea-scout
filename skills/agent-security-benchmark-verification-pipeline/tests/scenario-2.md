# Scenario 2: Well-documented claim with a linked public dataset and audit

## Setup
An engineering manager evaluating guardrail tools for a healthcare-adjacent chatbot pastes this excerpt from a vendor's GitHub README into the skill:

> "GuardRail-X scores 91.3% (CI: 88.6-93.9%, n=500 runs) on the public AgentSafetyBench-v2 adversarial suite (github.com/example-org/agentsafetybench-v2, commit a1b2c3d). Full scenario list, scoring rubric, and raw run logs are published in /results/v2-eval/. The suite's 340 scenarios span prompt injection, tool-misuse, and data-exfiltration attempts, each independently scored by a held-out LLM-as-judge with human-reviewed inter-rater agreement (kappa=0.82) reported in appendix B. GuardRail-X also completed a Schellman AIUC-1 accredited audit in September 2026 (report linked)."

He tells the skill: "What decision rides on it: deciding whether this is strong enough evidence to skip commissioning our own third-party audit before deployment."

## Expected behavior
1. **Claim as stated**: extract "91.3% (CI 88.6-93.9%, n=500 runs)," "340 scenarios," AgentSafetyBench-v2, quoted/summarized accurately.
2. **Verifiability Rating**: VERIFIABLE, or at worst PARTIALLY VERIFIABLE if the skill reasonably notes that "linked" isn't the same as the user having actually fetched and inspected the dataset/audit report themselves — either is acceptable as long as the justification correctly reflects that a public dataset, confidence interval, run count, inter-rater reliability figure, and an accredited third-party audit are all genuinely present. UNVERIFIABLE would be a clear FAIL here — the claim is near the top of what's realistically disclosable.
3. **Red flags found**: should be sparse — this claim pre-empts most of the checklist (exact count, CI disclosed, dataset linked, adversary types named, human-reviewed scoring, accredited audit). Any flags raised should be minor/residual (e.g. "harness/scaffolding details for GuardRail-X's own deployment config aren't specified" or "whether the 500 runs were independent fresh scenarios vs. 500 reruns of the same 340 isn't fully clarified") — not major flags copy-pasted from scenario 1.
4. **Reconstruction sketch**: should state this is largely reconstructable — public dataset, commit hash, published scoring rubric and logs — with at most a minor caveat about not having independently fetched the linked materials.
5. **Questions to ask the vendor**: should be light-touch / confirmatory (e.g. "can you confirm the commit hash remains pinned for reproducibility," "is the AIUC-1 audit report publicly downloadable") rather than the same heavy-skepticism questions as scenario 1.
6. **Bottom line**: should acknowledge this is strong, unusually well-documented evidence, while still noting (without contradicting itself) that "verifiable" is not the same as "independently re-run by a disinterested third party for this specific deployment" — a nuanced bottom line, not a blanket "you're fine, skip the audit" or a blanket "never trust a vendor."

## Pass/fail criteria
- PASS if: the rating is VERIFIABLE (or justifiably PARTIALLY VERIFIABLE with correct reasoning); the output correctly distinguishes this claim's strength from scenario 1's instead of applying an identical skeptical template; red flags listed are minor/residual, not major; the bottom line is nuanced rather than a flat yes/no; no fabricated details are added beyond what was pasted (e.g. it must not invent what the AIUC-1 report specifically says beyond "completed").
- FAIL if: the skill rates this UNVERIFIABLE or applies the same major red flags as a self-reported claim (showing it isn't actually differentiating by evidence quality); it treats "linked" as equivalent to "I personally verified the dataset contents" (overclaiming); the bottom line flatly tells the user to skip or not skip the audit without the nuance the setup calls for.
