# TriageBench Builder: A Reusable Cross-Region Clinical-Safety Benchmark Toolkit for Low-Resource LLM Deployment

- **Status**: EXPLORING
- **Date**: 2026-11-19
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-19-applied-ai-for-underserved-domains.md · P2
- **Maturity verdict**: PARTIAL — three independent region-specific efforts exist (Rwanda CHW benchmark, 5,609 Kinyarwanda questions from 101 CHWs, Nature Health Feb 2026; Kenya's "Alama Health QA" RAG-grounded methodology; IyàwóBench's Nigeria febrile-triage arXiv preprint), each a real implementation but single-region, preprint-stage or newly-peer-reviewed, with no generalized cross-region standard and no GitHub tooling found.
- **Format**: BOTH
- **Data Sources**: MANUAL — local clinical advisory partners paste/upload authored case scenarios (a symptom vignette plus the locally-correct management decision) via a structured intake template; no API or connector exists for "regionally-valid clinical ground truth," so this cannot be made CONNECTED — the human clinical judgment is the thing being captured, not fetched.

## The Gap
IyàwóBench's preprint states plainly that "no validated benchmark exists" for scoring LLM triage reasoning in West African primary care, and cites a Kenyan evaluation across 16 facilities where 7.8% of AI-generated management recommendations were "actively harmful." A separate Rwanda CHW benchmark (101 CHWs, 5,609 Kinyarwanda questions) explicitly flags multi-step reasoning evaluation as unaddressed future work. Three regions independently built nearly the same thing from scratch, as an academic paper each time, with no shared methodology any new region or org can reuse.

## The Project
A benchmark-construction toolkit, not a single benchmark: a standardized protocol for eliciting local clinicians' case scenarios and management judgments, a scenario-authoring and scoring-rubric template adapted from the three published methodologies (IyàwóBench, Rwanda, Kenya), and a harness that runs any candidate LLM against the resulting region-specific benchmark and reports harmful/acceptable rates. The centerpiece is turning "write an academic paper to validate your region's LLM deployment" into "run a toolkit with your local clinical partner" — the methodology is proven three times over, just never packaged for reuse.

## Tangible Impact
**Population**: Health-tech organizations and research teams deploying LLM-based triage/advisory tools in low-resource primary-care settings with no existing region-specific benchmark — concretely any org deploying outside Nigeria, Rwanda, or Kenya (where IyàwóBench, the Rwanda benchmark, and Alama Health QA already exist), and the 16 primary-care facilities in Kenya's own evaluation that discovered their 7.8% harmful-recommendation rate only after deployment, not before.
**Mechanism**: Today, validating an LLM tool's safety for a new region/language requires months of bespoke benchmark authoring culminating in a publication, as all three cited efforts show. A reusable construction toolkit collapses that months-long academic cycle into a run-it-yourself process, letting a new deploying org find its region's harmful-recommendation rate before going live instead of after an incident forces a retrospective study.
**Measure**: (1) time from "start building a local benchmark" to "first validated scored benchmark," compared to the 6-12+ month cycle implied by the three published efforts' timelines; (2) harmful-recommendation catch rate when an existing deployed tool is run against a toolkit-built benchmark, using Kenya's 7.8% finding as the comparison baseline; (3) number of distinct regions/languages adopting the shared toolkit within a year.

## Why Now
Three independent region-specific teams converged on building nearly the same benchmark-construction methodology within the same recent window, and LLM-based clinical tools are now capable enough that "is this specific regional deployment safe" is the live, urgent question rather than a hypothetical — the methodology is de-risked three times over; packaging is the only missing step.

## Skill Angle
Trigger: a team planning an LLM-based clinical tool for a new region/language says "we need a local safety benchmark before we deploy." Inputs: the target region/language, the clinical scope (e.g., febrile illness triage, maternal health), and access to local clinician reviewers. Output: a tailored benchmark-construction protocol — a scenario-elicitation question set, a scoring rubric adapted from the three published methodologies, and a sample-size recommendation. This differs from the project: the skill is the one-time protocol design a team runs at kickoff; the project is the persistent scored-benchmark dataset and harness that keeps running as the deployment and candidate models evolve.

## MVP Sketch
Scope to one clinical domain (febrile-illness/respiratory triage, where IyàwóBench and Kenya's work already overlap), port IyàwóBench's published methodology into a reusable protocol template, and pilot it with one new region not yet covered via one willing clinical partner. Stack: a scenario-authoring web form for clinician reviewers, a scoring rubric derived from the three published papers, a harness to run any candidate LLM's output against the scenarios and compute harmful/acceptable rates. Validating experiment: build one new regional benchmark with the toolkit and measure whether it catches the same class of harmful recommendations the Kenya study found manually, in a fraction of the time.

## Risks & Open Questions
- Recruiting qualified local clinician reviewers is the actual bottleneck, not software — the same recruitment risk every language/region-dependent idea in this digest hits.
- Over-generalizing the protocol risks losing exactly the regional/cultural specificity (local disease prevalence, local treatment norms) that makes the source benchmarks valid in the first place.
- Risk that the IyàwóBench or Rwanda team already has an unpublished generalized version in progress — worth direct outreach before building.
- Ethical-review and liability requirements for benchmarks built on real clinical judgment data vary by country/institution, adding setup time beyond the pure engineering effort.
