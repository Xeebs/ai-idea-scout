# Correction Loop: A Live-Feedback Retraining Toolkit for Low-Resource-Language Interpretation Services

- **Status**: PUBLISHED
- **Date**: 2026-11-19
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-19-applied-ai-for-underserved-domains.md · P3
- **Maturity verdict**: PARTIAL — CMULAB (`neulab/cmulab`, 15 stars, last pushed Sep 2025) is a genuine open-source human-in-the-loop correction framework, validated on Seneca, but small and academic rather than nonprofit-oriented. Tarjimly and Quill.org run the same correction-capture-retrain pattern as bespoke internal pipelines with no released tooling; Masakhane and Mozilla Common Voice are adjacent but don't implement the correction-loop retraining pattern itself.
- **Format**: BOTH
- **Data Sources**: CONNECTED — WhatsApp Business API / Twilio Conversations API (both mature, widely deployed) to capture live message pairs directly from the channel the org already uses, rather than requiring volunteers to manually export and paste transcripts; a manual CSV-upload path is the fallback MVP for orgs not yet on a supported channel.

## The Gap
Tarjimly connects refugees with volunteer interpreters and uses the corrected conversations as machine-translation feedback; Quill.org "leverages volunteers to correct data that trains LLMs for 55 low-resourced languages." Both are real, working examples of a capture-correction-retrain loop — but each is a single org's bespoke internal pipeline. A smaller nonprofit running the same kind of live interpretation or tutoring service for its own under-covered language has no shared tooling to stand up the same loop; it has to rebuild it from scratch, or more commonly, just discard the corrections its volunteers already produce.

## The Project
A reusable capture-correction-retrain toolkit that plugs into the messaging channel a nonprofit already uses: it intercepts the (original model output, volunteer correction) pair whenever a human corrects a translation, interpretation, or tutoring response, logs it into a growing validated dataset, and runs a scheduled fine-tune of an open-weight model against the accumulated corrections — turning routine volunteer labor that's already happening into a compounding data asset instead of a one-time fix thrown away after each conversation.

## Tangible Impact
**Population**: Small nonprofits and community organizations running live interpretation, translation, or tutoring services for speakers of under-covered languages — organizations the scale of Tarjimly and Quill.org already prove the demand, but the much larger population of smaller orgs serving a single refugee community or under-covered language who cannot build bespoke ML infrastructure the way those two did.
**Mechanism**: Today, a smaller org's volunteers correct machine output in real time, but those corrections are logged at best and discarded at worst — there is no retraining pipeline turning them into model improvement. A plug-in capture-and-retrain toolkit lets that org's existing channel feed a growing dataset automatically and periodically improve its own model, without hiring an ML team.
**Measure**: (1) validated correction pairs captured per month with no added volunteer workload beyond what they already do; (2) measured output-quality improvement (native-speaker-rated accuracy or BLEU/COMET) after N retraining cycles vs. the static starting model; (3) number of distinct small orgs/languages onboarded within a year, as a direct test of whether it displaces bespoke internal builds like Tarjimly's and Quill.org's.

## Why Now
WhatsApp Business API and Twilio Conversations API access has matured and cheapened enough that routing live interpretation/tutoring traffic through a capture layer is now a days-not-months integration, and open-weight models are now cheap enough to fine-tune on a rolling weekly/monthly cadence rather than requiring a dedicated ML team — both preconditions that let CMULAB-style tooling generalize beyond academia for the first time.

## Skill Angle
Trigger: an org running a live interpretation/tutoring service for an under-covered language asks "how do we turn our volunteers' corrections into a better model?" Inputs: a description of their current workflow (e.g., "volunteers correct WhatsApp messages in a shared inbox") and a sample of recent correction pairs. Output: an integration plan — what to log, a schema for (original, corrected) pairs, a recommended retraining cadence and base model, and privacy/consent considerations for using real conversation data. This differs from the project: the skill is the one-time integration/design plan a new org runs before building; the project is the persistent capture pipeline, dataset store, and retraining scheduler that keeps running across the service's ongoing live traffic.

## MVP Sketch
Scope to one channel integration (WhatsApp Business API, the most common channel in the digest's examples) and one pilot org/language pair recruited from an existing volunteer-interpretation network. Stack: a webhook-based capture service on the WhatsApp Business API, a correction-pair datastore, a scheduled LoRA fine-tune job against an open-weight translation/instruction model, a before/after eval against a held-out set. Validating experiment: run the pilot org's real traffic through the capture layer for 4-6 weeks, retrain once, and measure whether the retrained model's native-speaker-rated accuracy improves on held-out examples versus the static starting model.

## Risks & Open Questions
- Privacy/consent for using real refugee or vulnerable-population conversation data as training data is a serious ethical constraint, not a formality — needs explicit opt-in design.
- Volunteer correction behavior may be inconsistent in quality/coverage, producing noisy training signal a small retraining cadence can't filter reliably.
- Risk that Tarjimly or Quill.org's internal tooling is further along and closer to generalizable than this search surfaced — worth direct outreach before building.
- CMULAB's academic framework may be closer to production-ready than its 15-star GitHub profile suggests; worth a direct code read before assuming a rebuild is needed.
