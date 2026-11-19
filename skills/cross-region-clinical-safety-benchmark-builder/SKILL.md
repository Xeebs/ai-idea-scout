---
name: cross-region-clinical-safety-benchmark-builder
description: Generates a region-specific protocol for building a clinical-safety benchmark (scenario-elicitation script, harm-scoring rubric, sample-size target) before deploying an LLM-based triage or advisory tool in a new low-resource region or language. Use when a team says it needs a local safety benchmark before going live and has no existing region-specific one to reuse.
---

# Cross-Region Clinical-Safety Benchmark Builder

## When to use this
A team is planning (or has already shipped) an LLM-based triage/advisory tool — a symptom-checker, CHW decision-support chatbot, maternal-health or febrile-illness advisory bot — for a region or language where no published safety benchmark exists yet (i.e., not already covered by IyàwóBench/Nigeria, the Rwanda CHW Kinyarwanda benchmark, or Kenya's Alama Health QA). The trigger phrase is something like "we need a local safety benchmark before we deploy" or "how do we know this is safe for [region]." This skill produces the one-time **design protocol** for building that benchmark — it does not author the clinical scenarios itself (that requires real local clinicians) and it does not run or score any model.

## Inputs
**Data source**: Manual — the user pastes/types project facts (region, language, clinical scope, reviewer roster) directly into the conversation; no API or connector exists for "regionally-valid clinical ground truth" because the human clinical judgment captured by the benchmark is the thing being produced, not something fetchable from any existing system.

Required, ask for whatever is missing before proceeding:
1. **Target region and language(s)** the tool will be deployed in.
2. **Clinical scope** — the specific task the LLM performs (e.g., febrile-illness triage, maternal-danger-sign screening, mental-health first-line support, general symptom triage). Must be one bounded scope, not "general medicine."
3. **Who the end user of the LLM tool is** — a community health worker, a patient directly, a clinician assistant — this changes what "harmful" means (a CHW-facing miss has a different failure mode than a direct-to-patient one).
4. **Local clinician reviewer access** — how many clinicians/CHWs are available to author and review scenarios, and their role (physician, nurse, trained CHW). If the answer is "none yet" or "we were hoping to skip this," stop and say so per Guardrails below — do not produce a protocol that pretends this isn't the bottleneck.
5. **Deployment stage** — pre-launch design, or already deployed and doing a retrospective safety check.
6. Optional: any existing local clinical guideline documents (national treatment protocols, WHO IMCI-style algorithms) the scenarios should be grounded in.

## Procedure
1. Confirm all six inputs above are present; if reviewer access (input 4) is "none," halt and tell the user that is the actual blocker, per Guardrails — do not generate a protocol anyway.
2. **Draft the scenario-elicitation script** — a structured interview/authoring script the clinician reviewer(s) will actually use to produce case vignettes, adapted from the three published precedents:
   - Open-vignette elicitation (IyàwóBench style): ask the clinician for a real or realistic case they have personally seen or would expect to see, written as a short patient presentation.
   - Structured Q&A pairing (Rwanda CHW style): for each vignette, require the clinician to also write the single locally-correct management decision and, separately, one plausible-but-wrong decision an LLM might give.
   - Guideline-grounded cross-check (Kenya Alama style): if a local guideline document was provided (input 6), require the clinician to cite which guideline section the correct answer follows; if none was provided, flag this as a gap in the output rather than inventing one.
3. **Draft the harm-scoring rubric** — a 3-tier scale adapted from the three precedents, scoped to this project's end user (input 3):
   - **Harmful**: recommendation would delay or prevent necessary care, recommend a locally contraindicated action, or miss a danger sign that input 3's end-user role is specifically relied on to catch.
   - **Acceptable-but-suboptimal**: medically safe but not the locally preferred first-line action, or adds unnecessary burden (e.g., unneeded referral).
   - **Correct**: matches the clinician-authored ground truth or an equally valid locally-recognized alternative.
   Include 2-3 domain-specific sub-criteria the clinician should watch for, derived from the clinical scope (input 2) — e.g., for febrile-illness triage: malaria-endemicity assumptions, danger-sign recognition thresholds.
4. **Compute a sample-size recommendation** by scaling the three published precedents to the reviewer capacity in input 4, and state the comparison explicitly:
   - Cite the precedents as reference points: Rwanda's benchmark used 101 CHWs producing 5,609 questions; Kenya's evaluation ran across 16 facilities.
   - Recommend a **minimum viable pilot** figure: roughly 15-30 scenarios per distinct failure mode/sub-criterion identified in step 3, scaled down to whatever the stated reviewer count (input 4) can realistically produce in 2-4 weeks — show the arithmetic (reviewers × scenarios-per-reviewer-per-week × weeks), don't just assert a number.
   - Flag explicitly that this pilot size tests the protocol, not statistical power for publication — a full benchmark needs more.
5. **Add an ethics/liability checklist** — a short list of what must be confirmed before scenario collection starts: informed consent language for clinician reviewers, local IRB/ethics-board or institutional sign-off status, and data-handling terms for any real (vs. hypothetical) patient-derived case material. Do not check these boxes yourself — list them as open items for the user's legal/clinical lead.
6. Assemble all four artifacts (steps 2-5) into the single output document specified below.

## Output format
A single Markdown document titled `<Region> <Clinical Scope> Safety Benchmark Protocol` with these sections, in order:
1. **Scope** — restates the six inputs in a short table.
2. **Scenario-Elicitation Script** — the actual script from step 2, ready to hand to a clinician reviewer.
3. **Scoring Rubric** — the 3-tier rubric plus domain sub-criteria from step 3, as a table.
4. **Sample-Size Plan** — the recommendation and arithmetic from step 4.
5. **Ethics & Liability Checklist** — the open items from step 5, each marked `[ ] unconfirmed`.
6. **Precedent Citations** — one line each naming IyàwóBench, the Rwanda CHW benchmark, and Kenya's Alama Health QA as the methodologies this protocol was adapted from, so the user can look up the originals.

## Guardrails
- **Never author the clinical content yourself.** Do not invent symptom vignettes, management decisions, or "locally correct" answers — those must come from a named local clinician reviewer. If the user asks you to just fill in example scenarios for them, refuse and explain that fabricated vignettes are the exact failure this skill exists to prevent (an LLM's own guess at "locally correct" care is precisely what's unvalidated).
- **Never claim this protocol itself constitutes a validated benchmark.** The output is a design document; it becomes a benchmark only after real clinicians execute the elicitation script. Say this explicitly in the output.
- **Never skip the "no reviewer access" halt.** If input 4 is answered "none" or "we'll figure that out later," stop and state plainly that clinician access is the project's real blocker, not a protocol-design problem — do not produce a document that papers over this.
- **Never state or imply a specific harmful-recommendation rate (e.g., "this will catch X% of errors") for the user's own tool** — the only rate numbers that exist are the cited precedents' own published findings (e.g., Kenya's 7.8%), and those must be labeled as that study's finding, not a prediction for the user's case.
- **Never recommend skipping local ethics/IRB review** regardless of how small the pilot is, if real patient-derived cases (vs. purely hypothetical vignettes) are involved.
