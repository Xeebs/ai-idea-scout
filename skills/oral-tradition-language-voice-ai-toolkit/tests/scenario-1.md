# Scenario 1 — Hausa (standardized orthography, likely partial-to-narrow voice coverage)

## Context

A program officer at a West Africa-focused language-tech grantmaker is deciding whether to fund a new ASR/TTS data-collection effort for Hausa, or whether existing coverage already makes that redundant. They run the skill before writing the funding memo.

## Input the user supplies

- Language name: Hausa
- ISO 639-3 code: hau
- Region/country: Northern Nigeria, Niger, and diaspora communities across West Africa
- Approximate speaker population: ~80 million (first + second language speakers combined, rough figure from memory)
- Orthography status: standardized script (Boko/Latin-based orthography, in official use)
- Known existing resources the user is aware of: "I know Mozilla Common Voice has a Hausa dataset, and I've seen Hausa listed on Google's voice products somewhere, but I don't know the real extent."

## Expected skill behavior

1. Confirms the language record back exactly as given (name, ISO code, region, ~80 million, standardized orthography) — no invented or "corrected" population figure.
2. Runs through the named ASR catalog list (AfroLID, AfriSpeech, Masakhane/AfriQA, AI4Bharat, Sunbird, Mozilla Common Voice, Google FLEURS, VoxPopuli) plus a general search for "Hausa automatic speech recognition" / "Hausa ASR corpus," and reports which named sources returned hits vs. nothing.
3. Does the same for TTS, including the commercial-provider list (Google Cloud TTS, Azure Speech, Amazon Polly, ElevenLabs) plus general search.
4. Assigns an ASR tier and a TTS tier independently (plausible real-world outcome: ASR around Tier 2 given Common Voice + FLEURS coverage, TTS possibly Tier 1-2 given more limited commercial/production TTS for Hausa specifically) — the exact tier is less important than that each tier is named, justified in 1-3 sentences, and cites a specific source.
5. Because orthography is "standardized," the skill does **not** raise the no-written-form / audio-first structural warning — it should not fabricate an orthography problem that doesn't exist here.
6. Computes overall readiness as the lower (bottleneck) of the two modality tiers, explicitly stating which modality is the limiting factor.
7. Produces exactly one recommended first step sized to the found tier (e.g., if TTS lands at Tier 1-2, the recommendation should target closing the TTS gap specifically — licensing/reuse inquiry or a scoped data-collection step — not a full production-model build).
8. Outputs all seven required sections in the specified order, with a "Sources Checked" section marking hits vs. misses and the date the audit was run.

## Pass/fail checklist

- [ ] Output contains all 7 sections in order: Language Record, ASR Readiness, TTS Readiness, Overall Voice-Readiness, Gaps Identified, Recommended First Step, Sources Checked.
- [ ] Language Record restates exactly the inputs given (name, ISO code, region, ~80 million, standardized script) with no silently "corrected" or invented numbers.
- [ ] Both ASR Readiness and TTS Readiness cite at least one specific, named, checkable source (project/dataset name + a year or version where findable) for whatever tier is assigned — "Tier 2, no source given" is a FAIL.
- [ ] Overall Voice-Readiness equals the lower of the two individual tiers, and the report states in one sentence which modality is the bottleneck.
- [ ] No audio-first / no-written-form warning is raised (since orthography is standardized) — raising one anyway is a FAIL (false-positive guardrail trigger).
- [ ] Exactly one recommended first step is given, and it is a data-collection/licensing-scoping action, not a "build a full production model" plan.
- [ ] Sources Checked section lists every catalog/search explicitly as hit or miss, plus the date the audit was run, with a note that results will go stale.
- [ ] Nothing in the output presents an invented coverage percentage, dialect count, or WER figure that wasn't actually found in a cited source.
