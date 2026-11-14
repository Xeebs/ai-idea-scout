# No Leak: An Automatic Sensitivity Classifier for Fail-Closed Local/Cloud Routing

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Small & local models
- **Source**: research/2026-11-14-small-and-local-models.md · P1
- **Maturity verdict**: PARTIAL — `shaxzodbek-uzb/llm-localfirst` ("Fail-closed privacy routing + manager-worker delegation, MCP-native") exists on GitHub but has 0 stars and hasn't been pushed since 2026-08-16, a narrow unadopted solo project. The Cactus hybrid router (Gemma4-2B + Gemini fallback) is a different, cost/quality-motivated pattern, not fail-closed. No tool found anywhere automates the sensitivity-classification step itself — every example relies on a caller-declared flag, which is exactly the part the community signal says is unreliable.
- **Format**: BOTH — the always-on router is runtime infrastructure; auditing an existing hybrid-routing setup for silent cloud-fallback leak risk is a separable one-shot review task.
- **Data Sources**: CONNECTED — the router wires directly into the application's existing LLM request pipeline (whatever already calls Ollama/llama.cpp plus a cloud fallback), classifying every outbound request in real time; no third-party API is needed since it operates on the app's own live traffic. It uses a small, locally-run classifier calibrated once from a MANUAL seed set the developer uploads (a few hundred labeled example requests from their own domain — clinical notes, legal intake text, source material). No mature packaged connector/library doing this today; it would need to be built as part of this idea.

## The Gap
A developer write-up cited in this digest describes a local-inference timeout that defaulted to a cloud provider "to ensure high availability" — a trade the author concluded was wrong for a privacy-first system. The one close match, `llm-localfirst`, pins sensitive calls to a local model with no cloud fallback, but it still depends on a caller-declared sensitivity flag rather than classifying requests automatically, and it's an unmaintained 0-star solo project. No implementation anywhere automates the "is this sensitive" decision itself.

## The Project
A routing middleware that sits between an application and its local/cloud model calls. It classifies every outbound request's sensitivity in real time using a small local classifier (not a caller-set flag), and for anything flagged sensitive it hard-pins the request to the local model path — queuing or erroring on local failure rather than ever silently falling back to a cloud call. Policy is per-field/per-domain configurable (clinical, legal, source-protection categories) rather than one global switch, and every routing decision is logged for audit.

## Tangible Impact
**Population**: Solo and small-practice mental-health therapists in the U.S. adopting AI session-note tools — the APA's 2025–2026 Practitioner Pulse Survey found only 44% of psychologists had never used an AI tool in practice, down sharply from 71% the prior year, and a separate industry report found 40% of therapists already use at least one AI tool with note-taking the second most common use (Ensora Health, 2026) — plus the comparable population of small-practice immigration/criminal-defense lawyers and investigative journalists building or adopting similar local-first tools. Transitively, every client/source whose disclosures pass through one of these tools is exposed by the exact failure mode this project closes.
**Mechanism**: These solo practitioners have no IT/security team to catch a "local-first" tool's hybrid router silently defaulting to a cloud model on a timeout. Replacing the caller-declared sensitivity flag with an automatic classifier, and making the sensitive path physically incapable of falling back to the cloud, removes the single point where a developer's or integrator's oversight leaks a client disclosure to a third-party API.
**Measure**: (1) Leak rate on a red-team benchmark — planted sensitive requests injected during simulated local-inference outages; target 0% cloud fallback for sensitive-labeled requests. (2) Classifier precision/recall on a labeled held-out set of clinical/legal/journalistic example requests, benchmarked against the miss rate of a caller-declared-flag baseline. (3) Adoption — integrations/forks by local-first tool builders within 6 months of release.

## Why Now
The Cactus hybrid router benchmark (Gemma4-2B + Gemini fallback matching Gemini 3.1 Flash-Lite quality while routing only 15–55% of tasks to cloud) proves hybrid local/cloud routing is now accurate and cheap enough to run in production — but that pattern optimizes cost/quality, not privacy, leaving the fail-closed case unaddressed exactly as AI-scribe-style tools reach rising real-world adoption among the solo practitioners least equipped to catch a silent leak.

## Skill Angle
Given a pasted description or code snippet of an existing hybrid-routing setup (the fallback logic, timeout handling, and any sensitivity-flag code), Claude reviews it against the known failure mode — timeout-triggered silent cloud fallback — and returns a concrete list of where sensitive data could leak plus a drafted fail-closed policy config to seed the runtime router. This is a pre-deployment audit task, distinct from the always-on classifier/router itself.

## MVP Sketch
2–4 weeks, 1–2 people: a Python/TS middleware wrapper around an Ollama/llama.cpp call plus a cloud fallback call; ships with a lightweight local classifier (a small distilled model or logistic-regression head over embeddings) calibrated from ~300–500 labeled seed examples covering 2–3 sensitivity categories (clinical, legal, PII). The sensitive path hard-codes "no cloud call ever" — local retry/queue instead. Validate against a red-team set of ~100 planted sensitive prompts run under simulated local-inference failure, measuring whether any leak to the cloud path.

## Risks & Open Questions
- A classifier false negative (missed sensitivity) reproduces exactly the failure this project exists to prevent — recall on novel phrasing is the single hardest and most important number to get right.
- Defining "sensitive" is domain-specific; a clinical-tuned classifier may not transfer to legal or journalistic source material without re-calibration.
- A well-resourced local-first tool vendor (or `llm-localfirst` itself, if it gets a maintainer) could ship an equivalent feature and obsolete a standalone project.
- Overly conservative classification could permanently exclude legitimate low-latency queries from ever benefiting from local-first economics, undermining adoption.
