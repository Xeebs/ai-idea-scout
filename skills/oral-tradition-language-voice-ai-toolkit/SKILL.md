---
name: oral-tradition-language-voice-ai-toolkit
description: Produces a sourced voice-AI (ASR/TTS) readiness audit for one specific oral-tradition or low-resource language, with a 4-tier score, named evidence, and a recommended first data-collection step. Use when someone needs to decide whether to fund or build voice tooling for a specific language before committing resources.
---

# Oral-Tradition Language Voice-Readiness Audit

## When to use this
A language-community organization, field researcher, grant officer, or anyone evaluating a coalition/funder commitment (e.g. the AI-for-underrepresented-languages effort backed by frontier AI labs, Masakhane, AI4Bharat, Sunbird, and the Gates Foundation) needs a documented answer to: "What is the current state of ASR and TTS support for *this specific language*, and what should happen next?" — before deciding whether to request funding, start a data-collection effort, or flag the language as already covered. This is a per-language, point-in-time audit, not an ongoing tracker.

## Inputs
**Data source**: Manual — the user supplies the language name, any ISO 639-3 code they know, region/country, an approximate speaker-population figure (or states it's unknown), the orthography status (standardized script / emerging script / no standard written form / strong oral tradition), and a description of any resources they personally know exist (audio recordings, text corpora, prior papers, existing apps). The skill then performs its own ad hoc web/catalog research — there is no single maintained API or MCP connector today that unifies ASR/TTS coverage across AfroLID, AfriSpeech, AI4Bharat, Sunbird, Mozilla Common Voice, FLEURS, and commercial voice providers, so this step is live search, not a connector call, and must be repeated fresh each time (results go stale).

## Procedure
1. **Collect the record.** Confirm: language name, ISO code if known, region/country, speaker population (or "not provided" — never invent one), and orthography status as stated by the user.
2. **Search ASR coverage.** Check, by name, each of: AfroLID, AfriSpeech's 92-language catalog, Masakhane/AfriQA, AI4Bharat (Airavata and related Indic efforts), Sunbird AI, Mozilla Common Voice, Google FLEURS, VoxPopuli. Then run a general web/paper search for "<language name> automatic speech recognition" and "<language name> ASR corpus". Record every hit and every catalog that returned nothing.
3. **Search TTS coverage.** Same catalog list plus commercial providers' published language-support lists (Google Cloud TTS, Azure Speech, Amazon Polly, ElevenLabs). General search: "<language name> text-to-speech" / "<language name> TTS model". Record hits and misses.
4. **Score each of ASR and TTS independently on a 4-tier rubric:**
   - **Tier 0 — None**: no model, dataset, or published attempt found after the full catalog + general search.
   - **Tier 1 — Research-grade**: an academic paper, thesis, or small dataset exists (roughly under 10 hours of audio, or a single one-off system) with no deployable model or API.
   - **Tier 2 — Narrow-production**: a usable model or API exists but is limited — single dialect, restricted vocabulary, non-commercial license, or beta/unstable.
   - **Tier 3 — Broad-production**: a maintained, general-purpose model or commercial API covers the language with reasonable dialectal breadth.
   Every tier assignment must cite the specific source (project name + year, paper title, or product page). If nothing is found, the tier is Tier 0 and the output must say so explicitly — never round up out of charity, never leave a tier unsourced.
5. **Flag orthography as a structural risk, not a footnote.** If the user described the language as having no standard written form or a strong oral tradition, state plainly that text-based ASR training pipelines (which need aligned transcripts) are a poor fit, and that any recommended next step must be audio-first (e.g. phrase-list recording with native-speaker audio validation, not text transcription).
6. **Compute an overall readiness as the lower (bottleneck) of the ASR and TTS tiers** — a language with Tier 2 ASR but Tier 0 TTS is overall Tier 0 for "voice support," since the gap this toolkit targets is the ASR+TTS pair, not either alone.
7. **Write one recommended first step**, sized to the found tier and orthography status — e.g., Tier 0 + no orthography → start with a 50-100 phrase native-speaker-recorded audio set with community consent documented, not a text corpus. Tier 1 → identify the existing research dataset's license/holder and ask about reuse before collecting new data. Never recommend building a full production model as a "first step."
8. **Assemble the output** in the format below.

## Output format
A single markdown report with these sections, in this order:
1. **Language Record** — name, ISO code, region, speaker population (or "not provided"), orthography status (as given by the user).
2. **ASR Readiness** — tier (0-3), 1-3 sentence justification, named sources.
3. **TTS Readiness** — tier (0-3), 1-3 sentence justification, named sources.
4. **Overall Voice-Readiness** — the bottleneck tier, one sentence explaining which modality is the limiting factor.
5. **Gaps Identified** — bullet list of what specifically is missing (e.g. "no TTS voice model of any kind," "ASR exists only for a different dialect").
6. **Recommended First Step** — one concrete, resource-appropriate action, noting audio-first vs. text-based approach per orthography status.
7. **Sources Checked** — every catalog/search run, explicitly marking which returned hits and which returned nothing, plus the date the audit was run (results decay — this is a snapshot, not a live feed).

## Guardrails
- Never assign a tier without naming a specific, checkable source; "nothing found" is a valid, explicit Tier 0 result — never silently upgrade a tier to avoid saying "none."
- Never invent a speaker-population figure, dialect count, or coverage percentage the user didn't supply and the search didn't source — write "not provided" or "not found" instead.
- Never recommend a text-corpus-based collection protocol for a language the user described as having no standard written form or strong oral tradition — the recommended first step must be audio-first in that case.
- This is a one-time snapshot audit, not the maintained, continuously-updated scorecard the parent project publishes — always label the output with the date it was produced and note it will go stale.
- Do not recommend or sketch a full model-training plan — the skill's job stops at "what exists, what's missing, and the one right next data-collection step," not a build roadmap.
