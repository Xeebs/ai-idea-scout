# TrustedTriage: A Validated, Maintained On-Device Triage Assistant for Community Health Workers

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P1
- **Maturity verdict**: PARTIAL — GitHub/web search found a real cluster (Trij, Sentinel Health, PocketTriage, TriageOS, SHIFA, TriageMate, Google's MedGemma) but every community-built implementation is a solo side-project or hackathon entry, several self-labeled "unvalidated prototype v0.1," with no independent clinical evaluation found anywhere.
- **Format**: PROJECT

## The Gap
A dev.to field report ("Building medical AI for the other 90%") and an HLTH industry piece both describe the same structural problem: every CHW-facing triage tool must run fully offline on a phone CPU or district-clinic laptop, yet "there is no requirement or incentive for developers to test AI tools in rural settings, include rural data in training sets, or design for low-bandwidth environments." The digest surfaced five to six independently-built on-device triage prototypes (Trij, Sentinel Health, SHIFA, PocketTriage, TriageOS) — real evidence of demand — but none has been clinically validated, none is maintained past its hackathon or solo-dev origin, and none publishes an evaluation protocol a health system could trust.

## The Project
A single, maintained, open-source on-device triage assistant for CHWs, built around three things none of the existing prototypes combine: (1) a deterministic safety layer that hard-gates every model output against a clinician-authored decision tree before it reaches the CHW (the model drafts, the tree constrains — never the reverse), (2) a published, versioned evaluation protocol (sensitivity/specificity on a held-out symptom set, reviewed by a clinical advisory partner) run before every release, and (3) a packaging/update pipeline that works over SMS or occasional Wi-Fi sync so a clinic laptop with hours-a-month of connectivity still gets safety-layer patches. The LLM (a quantized Gemma-class model) handles symptom elicitation and documentation; the deterministic layer handles anything that gates a referral decision.

## Tangible Impact
**Population**: Community health workers serving the ~1.4 billion people the WHO estimates live in areas with persistently low or no internet connectivity for health services (WHO/ITU connectivity reports), concentrated in rural sub-Saharan Africa, South Asia, and remote Latin America — roughly 2-4 million CHWs globally rely on manual paper protocols for triage decisions today.
**Mechanism**: Today a CHW without connectivity either guesses, calls a supervisor who may be hours away, or defaults to over-referral (costly transport, overloaded clinics) or under-referral (missed emergencies). A validated on-device tool with a hard safety gate narrows that gap by giving a structured, offline second opinion at the point of contact, with referral-threshold logic clinicians can audit and amend.
**Measure**: (1) sensitivity/specificity of referral recommendations against a clinician-labeled validation set, published per release; (2) reduction in inappropriate referrals vs. a paper-protocol control arm in a pilot district; (3) number of independent clinic deployments still active 6 months post-install (the thing every existing prototype fails on).

## Why Now
Gemma-class and similarly sized open-weight models now run acceptable-latency inference on sub-$150 Android hardware, and the last 30 days show at least five teams independently converging on this exact architecture (model + offline + safety layer) — the technique is de-risked, but no one has paired it with a maintained release process and a real evaluation protocol, which is the actual missing piece per the HLTH critique.

## MVP Sketch
Scope the MVP to one well-bounded triage domain (e.g., wound/skin-lesion or respiratory-symptom triage, where WHO IMCI-style decision trees already exist as a deterministic backbone). Stack: quantized Gemma 2B/4B via llama.cpp or MediaPipe on Android, a hand-coded decision tree from an existing WHO/IMCI protocol as the hard gate, SQLite for offline case logs, SMS-based patch delivery. The single validating experiment: run the tool against 100-200 clinician-labeled historical cases and report sensitivity/specificity before any live deployment — if it can't clear a clinically-set bar on retrospective data, the project stops there rather than shipping to a real clinic.

## Risks & Open Questions
- Medical-device and local health-authority regulatory exposure varies by country; an early partnership with one willing ministry-of-health pilot program is probably a prerequisite, not an add-on.
- Liability: who is accountable if the safety layer's decision tree is wrong? Needs an explicit disclaimer/scope boundary (triage aid, not diagnosis) baked into the UX, not just the terms of service.
- Risk this duplicates an NGO's in-house unpublished tool — worth a direct outreach check to Dimagi, PATH, and Living Goods before building, since large CHW-program operators may have unpublished internal versions.
- Clinical validation requires a real clinical advisor and labeled data, which is the hardest and slowest part of the MVP — if that partnership can't be secured, the project isn't viable regardless of the engineering.
