# Device Fit: A Quantization and Compatibility Toolchain for Clinical LLMs on Sub-Spec Rural Phones

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-19-applied-ai-for-underserved-domains.md · P1
- **Maturity verdict**: PARTIAL — WebSearch found multiple independent pilots/proofs-of-concept (Crane AI's EaseHealth in Uganda — 268 health workers, 5-day field test; PRANAM/ApnaVaidya MLX-Swift iPhone PoC; AfyaPack; Breno Alves's Gemma-4 rapid-test-reader PoC; MAM-AI Zanzibar; AMEGA on-device benchmark study) but every one is a narrow, single-org pilot or unvetted preprint/blog, and each independently flags phone RAM/device compatibility as the unsolved blocker. No GitHub repo or product found offering a reusable toolchain for packaging/quantizing clinical models to fit sub-spec rural phones.
- **Format**: BOTH
- **Data Sources**: CONNECTED — Firebase Test Lab API (Google, mature, existing today) to run automated compatibility tests against real device profiles, including low-end Android hardware; the clinical model checkpoint itself is uploaded once by the developer, not continuously read from an external source.

## The Gap
Crane AI Labs' EaseHealth deployment of offline MedGemma to rural Ugandan health workers names "the device gap" — most health workers' phones lacking enough RAM — as the primary barrier to scaling, and five-plus other independent pilots (PRANAM, AfyaPack, MAM-AI, Breno Alves's rapid-test-reader, the AMEGA benchmark study) each separately rediscover the same wall. No one has built a reusable toolchain that packages and quantizes a clinical model to fit a specific low-end device before deployment, instead of finding out it doesn't fit after a field team is already standing in a clinic.

## The Project
A quantization-and-packaging toolchain purpose-built for clinical SLMs (MedGemma-class models to start) targeting real low-RAM Android devices. It inspects a candidate model checkpoint, recommends a quantization level (int4/int8/mixed) against a catalog of real device profiles common in CHW programs, runs the packaged model through automated on-device testing to verify it actually hits a usable latency/memory bar, and emits a packaged, versioned build plus a compatibility matrix the deploying org can trust before a field pilot — not after one fails.

Core components: a device-profile catalog (sourced from field reports like EaseHealth's), a quantization-recipe recommender, an automated device-farm test runner, and a published pass/fail compatibility matrix per model-device pair.

## Tangible Impact
**Population**: Community health workers whose field phones fall below the RAM threshold current clinical SLMs assume — concretely the 268 health workers in EaseHealth's Uganda field test and the comparable device-constrained cohorts in PRANAM, AfyaPack, and MAM-AI's pilots, situated within the broader ~2-4 million CHWs globally relying on smartphone-based tools in low/no-connectivity regions (WHO/ITU connectivity estimates).
**Mechanism**: Today, each org building a CHW-facing clinical model discovers the RAM wall independently, late, usually during or after a field test. A reusable toolchain with a verified device-compatibility matrix lets an org check and fix model fit before committing field time, turning a late deployment failure into an early, cheap engineering decision.
**Measure**: (1) percentage of a catalogued low-end device list (sourced from real CHW program hardware) that passes a defined memory/latency bar after toolchain-recommended quantization; (2) reduction in field pilots blocked or restarted due to device incompatibility, compared to the status quo EaseHealth and peers describe; (3) number of independent orgs adopting the toolchain's packaged output in a real deployment.

## Why Now
MedGemma-class clinical SLMs and quantization paths (MediaPipe LLM Inference API, llama.cpp int4/int8) are mature enough to generalize, and multiple independent orgs hit the identical device wall within the same 30-day window — the capability exists, only the packaging/verification layer is missing.

## Skill Angle
Trigger: a developer says "I have this clinical model checkpoint and need it to run on [a specific low-end Android device/RAM spec]." Inputs: the model checkpoint's architecture/size and the target device's RAM/chipset. Output: a recommended quantization strategy and a pass/fail/borderline compatibility verdict with a memory-budget breakdown. This differs from the project: the skill is a one-shot advisory check; the project is the maintained, device-farm-integrated benchmark suite and packaging pipeline that stays current as new devices and models ship.

## MVP Sketch
Scope to one model family (MedGemma 2B/4B quantized variants) and a fixed catalog of 5-8 real low-end Android device profiles common in East African CHW programs, sourced from EaseHealth's and peers' field reports. Stack: llama.cpp/MediaPipe LLM Inference API for on-device inference, Firebase Test Lab for automated multi-device testing, a CLI that takes a checkpoint and emits a per-device pass/fail plus recommended quantization level. Validating experiment: run the same MedGemma checkpoint through the toolchain against EaseHealth's named device list and check whether the recommended recipe clears a defined latency/memory bar on the devices EaseHealth's own report flagged as borderline.

## Risks & Open Questions
- Device fragmentation across regions may be too wide for one compatibility matrix to stay useful without constant upkeep.
- Clinical accuracy can degrade non-uniformly under aggressive quantization in ways a generic latency/memory benchmark won't catch — needs a clinical-accuracy regression check alongside the hardware benchmark.
- Risk this is already solved in-house, unpublished, by Google's Health AI Developer Foundations team (who ran the EaseHealth pilot) — worth direct outreach before building.
- Firebase Test Lab's device catalog may not include the specific ultra-low-RAM phones rural CHWs actually carry, requiring physical device procurement instead.
