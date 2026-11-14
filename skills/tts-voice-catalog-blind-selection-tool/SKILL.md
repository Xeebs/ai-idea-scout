---
name: tts-voice-catalog-blind-selection-tool
description: Drafts a ready-to-run DIY blind listening test (matched-script clip plan, randomized pairwise comparison schedule, listener rubric, and results tally template) for picking the best TTS voice out of a shortlist of 3-10 candidates pulled from one vendor's catalog, for one specific narration/dialogue task. Use when someone has already narrowed a TTS catalog (ElevenLabs, Play.ht, Cartesia, WellSaid, etc.) to a handful of candidates and needs a defensible way to choose between them instead of guessing from vendor popularity/tags.
---

# TTS Voice Catalog Blind Selection Test Designer

## When to use this
Someone has a specific narration or dialogue task (an audiobook chapter, a game NPC line set, an app's voice assistant) and has already shortlisted 3-10 candidate voices from a single TTS vendor's catalog (ElevenLabs Voice Library, Play.ht, Cartesia, WellSaid, etc.). They are about to pick one based on vendor tags, "popularity," or a quick gut-check listen, and want instead a small, structured blind test they can run themselves (or hand to 5-10 teammates/testers) to get a defensible answer. This is explicitly for the narrow-catalog decision ("which ONE voice from MY shortlist fits THIS task"), not for comparing TTS engines/vendors against each other — that is a different, already well-covered problem (TTS-Arena-V2, Podonos, etc.).

## Inputs
**Data source**: Manual — this skill itself only needs pasted/typed text: the task description, the list of already-shortlisted candidate voice names/IDs, and the target script text. It does not call any TTS catalog API, synthesize audio, or recruit listeners itself. (Context for anyone comparing this to the full "VoicePick" project this skill is a companion to: the full project is Connected — it reads voice metadata and synthesizes same-script clips directly via a vendor catalog API such as the ElevenLabs Voice Library API, and recruits raters via a panel API such as Prolific or Positly. This skill is the lightweight, no-infrastructure version: you still have to generate the actual audio clips yourself using whatever synthesis access you already have, and recruit your own 5-10 listeners — the skill's job is only to design the test correctly.)

Required from the user:
1. **Task description** — genre/content type, tone, audience (e.g. "middle-grade audiobook narrator, warm and playful" or "cyberpunk RPG villain NPC, menacing and clipped").
2. **Candidate voice list** — 3 to 10 voice names or IDs already shortlisted from the catalog. Fewer than 3 isn't a ranking test (just do a straight A/B); more than 10 should be narrowed first, or split into two rounds.
3. **Target script text** — the actual narration/dialogue excerpt (not a generic sample) that all candidates will read. Ideally 150-400 words covering the hardest content for this task: character names, numbers, emotional range, any tricky pronunciation.
4. **Number of available listeners** (default assumption: 5-10 if not given).

Optional: known constraints (max clip length, listener incentive budget, deadline).

## Procedure
1. **Validate inputs.** If no script text is provided, stop and ask for it — never substitute a generic placeholder script; the entire point of a task-matched test is using the user's real text. If only 1-2 candidates are given, say so and offer a simple A/B design instead of a ranking design. If more than 10 candidates are given, recommend the user pre-narrow to 10 or split into two rounds (comparisons grow quadratically) before proceeding.
2. **Finalize the test script.** If the provided text is over ~400 words, select the 1-2 most representative excerpts (prioritize: the opening hook, and any passage with proper nouns/numbers/emotional shifts) rather than using the whole thing, and state exactly which excerpt(s) were chosen and why.
3. **Write the clip production checklist**: every candidate voice reads the identical finalized script text; clips loudness-normalized to a consistent target (e.g. -18 LUFS integrated, -1 dBFS peak) before any listening — call this out explicitly, since unnormalized loudness is a documented bias (louder clips win regardless of quality). Specify a consistent file format/sample rate and that default vendor settings (speed, stability/expressiveness sliders) should be held constant across candidates unless the task specifically calls for voice-specific tuning.
4. **Build the pairwise comparison schedule.** For N candidates:
   - N = 2-5: full round-robin, all N×(N-1)/2 pairs.
   - N = 6-10: a partial-pairing schedule — each voice appears in at least 4 comparisons, total comparisons capped at roughly 3×N so no single listener is overloaded; distribute pairs round-robin style, skipping some non-adjacent pairs to hit the cap.
   Randomize left/right (Clip A / Clip B) assignment per pair and randomize presentation order across listeners. Label clips only as "Clip A" / "Clip B" per comparison — never reveal voice names/IDs to listeners.
5. **Write the listener rubric and instructions.** For each comparison: a forced choice (prefer A / prefer B / no preference) plus three 1-5 dimension scores per clip — naturalness, task-fit (does this suit the stated genre/tone), and, for clips over ~30 seconds, listener fatigue ("would you want to hear 20 more minutes of this voice"). Include a one-paragraph instruction block: what the listener is judging, that they should listen with headphones/decent speakers once before scoring, and that there are no right answers.
6. **Write the results tally template**: a table with columns Voice ID | wins | losses | no-preference | win-rate | avg naturalness | avg task-fit | avg fatigue, plus a one-line note that win-rate alone is a reasonable small-N ranking signal (a full Bradley-Terry model is overkill below ~50 total judgments) and that the top 1-2 voices by win-rate should be the shortlist for final creative sign-off, not an automatic final pick.
7. **Compile everything into one document** (see Output format) and hand it back as the deliverable — do not just describe the plan in prose.

## Output format
A single Markdown document with these sections, in order:
1. **Test overview** — task description, finalized script text (quoted in full), candidate list.
2. **Clip production checklist** — numbered steps for generating normalized, matched clips.
3. **Comparison schedule** — a table of every pair (Comparison # | Voice X | Voice Y | Randomized A/B assignment note).
4. **Listener instructions and rating sheet** — ready to copy into a form/printout, one block per comparison.
5. **Results tally template** — the empty table described in step 6, ready to fill in after the test.
6. **Interpretation notes** — 3-5 bullets on confidence level given listener count, the caveat that this is a directional/small-N result (not a canonical ranking), and a reminder that final choice should combine this data with the team's own creative judgment.

## Guardrails
- Never invent or substitute a generic/sample script in place of the user's real task text — the entire premise of this test is matched real-text comparison.
- Never produce a design for fewer than 2 candidates, and clearly flag when N=2 means this is a simple A/B, not a ranked comparison.
- Never skip the loudness-normalization callout — it is a known, documented source of biased results in blind TTS comparisons.
- Never reveal voice names/IDs to listeners in the instructions/rating sheet — only "Clip A/B" labels, with the name↔label mapping kept separate for the person tallying results.
- Never claim this lightweight 5-10-listener test is statistically equivalent to a large paid panel (100+ raters) — always state it is directional and should inform, not replace, final creative judgment.
- Never attempt to call a TTS API, generate audio, or recruit listeners as part of this skill — it drafts the test design only; audio generation and listener recruitment remain the user's own steps.
