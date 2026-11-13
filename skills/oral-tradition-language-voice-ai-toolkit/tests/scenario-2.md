# Scenario 2 — Krahn (no standardized written form, strong oral tradition, likely near-zero voice coverage)

## Context

A community-based language-preservation organization working with Krahn speakers (an oral-tradition Kru language spoken across Liberia and Ivory Coast) wants to know whether any voice-AI tooling already exists before they apply for a small grant to start their own audio-recording effort. They have no technical background and supply only what they personally know.

## Input the user supplies

- Language name: Krahn
- ISO 639-3 code: "unknown — not sure which code applies, there may be more than one Krahn variety"
- Region/country: Eastern Liberia and western Ivory Coast
- Approximate speaker population: "not provided — I don't have a reliable number"
- Orthography status: no standard written form — strong oral tradition (occasional informal Latin-letter spellings used inconsistently, not standardized)
- Known existing resources: "none known — we haven't found anything built for this language"

## Expected skill behavior

1. Confirms the record back including the explicit "not provided" population and the ISO-code uncertainty — never guesses a number or picks a code on the user's behalf without flagging the ambiguity.
2. Runs the full named ASR catalog check (AfroLID, AfriSpeech, Masakhane/AfriQA, AI4Bharat, Sunbird, Common Voice, FLEURS, VoxPopuli) plus general search for "Krahn automatic speech recognition" / "Krahn ASR corpus" — realistically, most or all of these return nothing, which must be reported as Tier 0, not hedged.
3. Same for TTS, including commercial-provider lists — realistically also Tier 0.
4. Because orthography status is "no standard written form / strong oral tradition," the skill must explicitly flag that text-based ASR training pipelines are a poor fit and that any next step must be audio-first.
5. Overall readiness is computed as the bottleneck tier (Tier 0 if both ASR and TTS are Tier 0), with the limiting modality named (or both, if both are zero).
6. The recommended first step must be audio-first and scoped appropriately for Tier 0 + no orthography — e.g., a native-speaker-recorded set of common phrases with documented community consent — and must explicitly NOT be a text-transcript-based collection plan or a full model-build plan.
7. Gaps Identified section states plainly that no ASR or TTS resource of any kind was found, rather than implying partial coverage exists.
8. Sources Checked lists every catalog/search run as a miss (or hit, if the skill's live search genuinely turns up something unexpected — in which case it must be named and sourced, not assumed), plus the audit date and a staleness note.

## Pass/fail checklist

- [ ] Output contains all 7 sections in order: Language Record, ASR Readiness, TTS Readiness, Overall Voice-Readiness, Gaps Identified, Recommended First Step, Sources Checked.
- [ ] Language Record shows "not provided" for speaker population and flags the ISO-code ambiguity rather than inventing or silently picking a code/number.
- [ ] If no source is found for a modality, the tier is explicitly Tier 0 with the report stating "no model, dataset, or published attempt found" — not a vague "limited information available" dodge, and not an unsupported upgrade to Tier 1+.
- [ ] The report explicitly states that text-based ASR training is a poor fit for this language because of its oral-tradition/no-written-form status (guardrail must fire here, unlike Scenario 1).
- [ ] The Recommended First Step is audio-first (e.g., native-speaker phrase recording with documented consent) and explicitly is not a text-corpus-based step and not a full production-model build.
- [ ] Overall Voice-Readiness correctly reflects the bottleneck logic (Tier 0 overall if either modality is Tier 0).
- [ ] No invented speaker-population figure, dialect count, or coverage percentage appears anywhere in the output.
- [ ] Sources Checked explicitly lists each catalog/search as hit or miss plus the run date, and notes the snapshot will go stale.
