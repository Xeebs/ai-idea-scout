# Guideline Gate: A Grounded-Claim Verification Middleware for General Medical LLMs in Low-Resource Deployment

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-19-applied-ai-for-underserved-domains.md · P6
- **Maturity verdict**: PARTIAL — several research-stage tools exist (VerifAI, an open-source biomedical RAG + post-hoc claim verification pipeline; OpenGATE, whose own docs state its claim-extraction gate is "currently failing"; GroundCheck, a demo not a library; DIASENTINEL, a diabetes-specific multi-agent grounding system with unconfirmed code availability) but none is a general, bolt-on grounded-claim layer built for low-resource/non-specialist frontline deployment on top of permissively-licensed public medical models.
- **Format**: BOTH
- **Data Sources**: MANUAL — the deploying org uploads/pastes the clinical guideline documents relevant to its region (e.g., WHO IMCI protocol excerpts, local Ministry of Health guidance) once, which the middleware then reuses as its grounding corpus; no mature cross-region API serves "the locally-applicable clinical guideline" uniformly, so this cannot be made CONNECTED beyond that one-time upload.

## The Gap
A solo developer's field report, "Building Medical AI for the Other 90%," describes building a shared routing/citation layer with "a check that flags grounded versus ungrounded claims" specifically because permissively-licensed public medical AI models are, in the author's words, "not deployment-ready" for frontline use as-is — the report-orchestration layer is finished but other modules are still pending validation, unshipped and untested by anyone else. Research-stage grounding tools exist in the general medical-AI space, but each is incomplete, demo-stage, or narrow to one condition, and none targets the specific low-resource/non-specialist deployment context.

## The Project
A bolt-on middleware that sits between a general-purpose medical LLM and the frontline worker who sees its output: it extracts the distinct clinical claims in a response, retrieves the relevant passage from a locally-uploaded clinical-guideline corpus, and flags each claim grounded (with its supporting citation) or ungrounded (flagged for review) before the response reaches the worker. The centerpiece is making this check a reusable, drop-in layer any org can wrap around whatever permissively-licensed public medical model it's already using, instead of a bespoke in-progress project only one developer has built.

## Tangible Impact
**Population**: Frontline non-specialist health workers and small health-tech orgs in low-resource settings who deploy general-purpose, permissively-licensed public medical LLMs because that's what's affordable and available to them — the same population the "Other 90%" field report targets, broader than triage/referral-decision users alone: anyone using a general medical LLM for patient education, documentation, or Q&A.
**Mechanism**: A general medical LLM will readily state a claim that sounds authoritative but is not grounded in any actual clinical guideline, and a non-specialist worker has no way to tell the difference. A middleware that flags each claim grounded or ungrounded against a locally-relevant guideline corpus gives that worker a visible, per-claim trust signal, instead of an all-or-nothing choice between blind trust and not using the tool at all.
**Measure**: (1) precision/recall of the grounded/ungrounded flag against a clinician-labeled validation set of model outputs; (2) reduction in frontline-worker-reported "acted on an ungrounded claim" incidents in a pilot deployment vs. an unguarded baseline; (3) latency overhead the grounding check adds per response, since it must remain usable in a live, low-bandwidth deployment.

## Why Now
Open-weight medical LLMs (MedGemma and similar) are now good and cheap enough to deploy in low-resource settings that the deployment question has shifted from "can we run a medical model at all" to "can we trust what it says" — exactly the gap the solo developer's field report and the research-stage grounding tools are all independently circling without anyone shipping a general, deployment-ready version.

## Skill Angle
Trigger: a developer building a medical LLM tool for low-resource deployment pastes a draft model response and asks "is this grounded in our clinical guidelines?" Inputs: the model's draft response and the relevant guideline document excerpt (or a reference to an already-uploaded guideline corpus). Output: a claim-by-claim breakdown — each distinct clinical claim marked grounded (with supporting citation) or ungrounded (flagged), plus an overall grounding score. This differs from the project: the skill is a one-shot development-time/QA check a builder runs while iterating; the project is the always-on inline middleware performing this check on every live response in production, which must stay running and fast.

## MVP Sketch
Scope to one clinical domain and one guideline source (e.g., WHO IMCI protocols) and wrap an open claim-extraction approach (similar to VerifAI's post-hoc verification step) around one target open-weight medical model's outputs. Stack: an LLM-based claim-extraction step, a retrieval step against the uploaded guideline corpus, a grounded/ungrounded classifier, exposed as a lightweight API middleware. Validating experiment: run a held-out set of model outputs with clinician-labeled grounded/ungrounded ground truth through the middleware and measure precision/recall against a naive "flag everything as needs-review" baseline.

## Risks & Open Questions
- OpenGATE's own docs state its claim-extraction gate is "currently failing," suggesting this exact sub-step is harder than it looks — worth a direct technical read of OpenGATE's failure mode before assuming it's quickly solvable.
- A grounding check too slow for the low-bandwidth, near-real-time usability this population needs defeats the purpose — latency budget must be a first-class design constraint.
- A false "grounded" flag is arguably worse than no flag at all, since it actively mis-signals trustworthiness — the validation bar needs to be genuinely high before any pilot deployment.
- Risk this duplicates an in-progress, unpublished continuation of the solo developer's own "Other 90%" project — worth direct outreach to that report's author before building a parallel effort.
