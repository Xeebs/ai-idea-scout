# Oral-Tradition Language Voice-Readiness Audit

A self-contained prompt template for producing a sourced, one-time readiness audit of ASR (speech-to-text) and TTS (text-to-speech) AI support for one specific low-resource or oral-tradition language. Paste the prompt below into any AI chat tool with web search enabled (ChatGPT with browsing, Claude with web search, Gemini, Perplexity, etc.) and fill in the bracketed details about your language.

## When to use this

Use this when you (a language-community organization, field researcher, grant officer, funder, or someone evaluating whether a language-AI coalition commitment has actually translated into shipped tooling) need a clear, documented answer to: "What is the current state of voice AI for this specific language, and what should we do next?" This produces a snapshot assessment for one language at one point in time — it is not a running tracker, and results will go stale as new tools ship, so re-run it periodically for languages you're actively tracking.

## What you need to provide

This skill runs on information you supply plus live web research — it does not connect to any live database or API on your behalf (no such unified database of ASR/TTS coverage across languages exists today, as of this writing).

Before running it, gather:
- **Language name** (and any alternate names/spellings)
- **ISO 639-3 code**, if you know it (optional — the search can proceed without it)
- **Region/country** where it's spoken
- **Approximate speaker population**, or state plainly that you don't have a reliable figure — never guess
- **Orthography status**: does it have a standardized written script, an emerging/informal script, or no standard written form (strong oral tradition)?
- **Any resources you already know about**: existing audio recordings, text corpora, academic papers, apps, or models you've heard of for this language

## The prompt

Copy everything below the line, fill in your language's details, and paste it into your AI tool of choice (make sure web search/browsing is turned on if the tool supports it):

---

You are conducting a voice-AI (ASR and TTS) readiness audit for one specific language. Here is the language record:

- Language name: [LANGUAGE NAME]
- ISO 639-3 code: [CODE OR "unknown"]
- Region/country: [REGION]
- Approximate speaker population: [NUMBER OR "not provided"]
- Orthography status: [standardized script / emerging script / no standard written form — strong oral tradition]
- Known existing resources: [describe anything you already know about, or write "none known"]

Do the following, using web search:

1. **Search ASR (speech recognition) coverage.** Check by name: AfroLID, AfriSpeech's 92-language catalog, Masakhane/AfriQA, AI4Bharat (Airavata and related Indic-language work), Sunbird AI, Mozilla Common Voice, Google FLEURS, VoxPopuli. Then run a general search for "[LANGUAGE NAME] automatic speech recognition" and "[LANGUAGE NAME] ASR corpus". Record every hit with its source, and note which catalogs returned nothing.

2. **Search TTS (text-to-speech) coverage.** Check the same catalog list, plus commercial providers' published language-support lists: Google Cloud TTS, Azure Speech, Amazon Polly, ElevenLabs. Run a general search for "[LANGUAGE NAME] text-to-speech" and "[LANGUAGE NAME] TTS model". Record hits and misses.

3. **Score ASR and TTS independently on this 4-tier rubric**, citing a named source for every tier assigned:
   - Tier 0 — None: nothing found after the full search.
   - Tier 1 — Research-grade: an academic paper or small dataset exists (roughly under 10 hours of audio, or a one-off system), no deployable model/API.
   - Tier 2 — Narrow-production: a usable model/API exists but is limited (single dialect, restricted vocabulary, non-commercial, or beta).
   - Tier 3 — Broad-production: a maintained, general-purpose model or commercial API with reasonable dialect breadth.
   If you find nothing for a modality, say so explicitly as Tier 0 — do not round up to be generous.

4. **If the orthography status is "no standard written form" or "strong oral tradition,"** explicitly flag that text-based ASR training (which needs aligned transcripts) is a poor fit, and that any recommended next step must be audio-first.

5. **Compute an overall readiness score as the LOWER of the ASR and TTS tiers** (the bottleneck) — a language needs both to count as voice-ready, not just one.

6. **Recommend exactly one concrete first data-collection step**, sized to the tier found and the orthography status. Examples: Tier 0 + no written form → a native-speaker-recorded set of 50-100 common phrases with documented community consent, not a text corpus. Tier 1 → contact the holder of the existing research dataset about reuse/licensing before collecting anything new. Never recommend building a full production model as a "first step."

Produce your answer as a report with exactly these sections, in this order:

1. **Language Record** — restate the inputs above.
2. **ASR Readiness** — tier, 1-3 sentence justification, named sources.
3. **TTS Readiness** — tier, 1-3 sentence justification, named sources.
4. **Overall Voice-Readiness** — the bottleneck tier and which modality is the limiting factor.
5. **Gaps Identified** — bullet list of specifically what's missing.
6. **Recommended First Step** — one concrete action.
7. **Sources Checked** — every catalog and search you ran, explicitly listing which returned hits and which returned nothing, plus today's date (this is a snapshot, not a live feed — note that it will go stale).

Do not invent a speaker population, dialect count, or coverage figure that wasn't provided or found. Do not assign a tier without naming a checkable source. Do not propose a full model-build plan — stop at the one recommended first step.

---

## Guardrails (built into the prompt, don't skip them when adapting)

- Every tier claim needs a named, checkable source. "Nothing found" is a legitimate Tier 0 — don't let the model round up to avoid saying "none."
- Never let the model invent a population figure or coverage statistic it wasn't given or didn't find.
- Never accept a text-corpus recommendation for a language described as having no standard written form — insist on an audio-first recommendation.
- This produces a one-time snapshot, not a running tracker. If you're monitoring a language over time, re-run this periodically and compare the "Sources Checked" and tier sections across runs — don't trust a single run to still be accurate months later.
- This is an assessment and a next-step recommendation only — it is not a substitute for an actual data-collection effort, a funding proposal, or a maintained public scorecard tracking many languages over time.
