# TriageBench Builder: A Reusable Cross-Region Clinical-Safety Benchmark Toolkit for Low-Resource LLM Deployment

A Kenyan evaluation across 16 primary care facilities found that 7.8% of an LLM's AI-generated management recommendations were "actively harmful" — and that number only exists because someone ran a dedicated academic study to find it. In Rwanda, a separate team built a 5,609-question Kinyarwanda benchmark from 101 community health workers and then flagged, in their own paper, that scoring multi-step reasoning was still unaddressed. In Nigeria, the team behind IyàwóBench opens their preprint by stating flatly: "no validated benchmark exists" for scoring LLM triage reasoning in West African primary care. Three regions, three teams, three papers — and the same realization each time, built from scratch, with nothing left behind for the next region to reuse.

## The Gap

The pattern across all three efforts is consistent: a region deploys or considers deploying an LLM-based triage or advisory tool, discovers there's no way to validate whether its recommendations are safe for the local clinical and linguistic context, and responds by commissioning a bespoke academic benchmark — scenario authoring, clinician review, scoring rubric, peer review, publication. That is the only path that currently exists. IyàwóBench's own framing of its gap is also the strongest evidence for this project: the authors built one narrow benchmark precisely because nothing generalized existed, and despite three independent teams converging on nearly the same methodology, none of it has turned into a standard any new region or organization can simply run. There's no GitHub tooling that implements this pattern, just three single-region research artifacts that happen to rhyme.

## The Project

This isn't another regional benchmark — it's the toolkit that makes building one not require a research paper. The core deliverable is a standardized protocol for eliciting local clinicians' case scenarios and management judgments, paired with a scenario-authoring and scoring-rubric template synthesized from the three published methodologies (IyàwóBench, Rwanda, Kenya's Alama Health QA), plus a harness that runs any candidate LLM against the resulting region-specific benchmark and reports harmful-vs-acceptable rates. The reframe is the whole point: instead of "write an academic paper to validate your region's LLM deployment," a team runs a toolkit with their local clinical partner. The methodology has already been proven three times over in three different regions — what's missing is packaging, not validation.

## Tangible Impact

**Population**: Health-tech organizations and research teams deploying LLM-based triage/advisory tools in low-resource primary-care settings with no existing region-specific benchmark — concretely any org deploying outside Nigeria, Rwanda, or Kenya (where IyàwóBench, the Rwanda benchmark, and Alama Health QA already exist), and the 16 primary-care facilities in Kenya's own evaluation that discovered their 7.8% harmful-recommendation rate only after deployment, not before.
**Mechanism**: Today, validating an LLM tool's safety for a new region/language requires months of bespoke benchmark authoring culminating in a publication, as all three cited efforts show. A reusable construction toolkit collapses that months-long academic cycle into a run-it-yourself process, letting a new deploying org find its region's harmful-recommendation rate before going live instead of after an incident forces a retrospective study.
**Measure**: (1) time from "start building a local benchmark" to "first validated scored benchmark," compared to the 6-12+ month cycle implied by the three published efforts' timelines; (2) harmful-recommendation catch rate when an existing deployed tool is run against a toolkit-built benchmark, using Kenya's 7.8% finding as the comparison baseline; (3) number of distinct regions/languages adopting the shared toolkit within a year.

## Try It

A companion Claude Code skill exists at `skills/cross-region-clinical-safety-benchmark-builder/`: "Generates a region-specific protocol for building a clinical-safety benchmark (scenario-elicitation script, harm-scoring rubric, sample-size target) before deploying an LLM-based triage or advisory tool in a new low-resource region or language. Use when a team says it needs a local safety benchmark before going live and has no existing region-specific one to reuse."

It is a design-protocol generator, not an automated data source — it needs a human to hand it the region, language, clinical scope, intended end-user (CHW, clinician, patient), and local clinician reviewer access. Two ways to use it:

- **Any AI chat tool**: paste the contents of `skills/cross-region-clinical-safety-benchmark-builder/README.md` into the chat, then answer the questions it asks about your target region and scope.
- **Claude Code**: drop the `skills/cross-region-clinical-safety-benchmark-builder/` folder into `~/.claude/skills/`, and Claude will reach for it automatically when a team says something like "we need a local safety benchmark before we deploy."

Note that the skill refuses to fabricate reviewer access — if you have no local clinician reviewers lined up yet, it will say so rather than hand you a protocol that pretends the recruitment bottleneck doesn't exist. That's deliberate: the biggest open risk on this idea isn't the software, it's that qualified local clinician reviewers are genuinely scarce, and no toolkit changes that.

Worth flagging before you build on this: it's possible one of the three source teams (IyàwóBench or the Rwanda group) already has an unpublished generalized version of this in progress, and direct outreach to them is worth doing before investing further.

---

Surfaced from `research/2026-11-19-applied-ai-for-underserved-domains.md`, pattern `P2`.
