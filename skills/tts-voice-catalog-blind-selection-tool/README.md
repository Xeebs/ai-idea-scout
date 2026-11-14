# TTS Voice Catalog Blind Selection Test Designer

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your own task details, and it will design a ready-to-run DIY blind listening test for picking the best text-to-speech voice out of a shortlist you've already pulled from a vendor's catalog.

## What this is for

You've already narrowed a TTS vendor's catalog (ElevenLabs Voice Library, Play.ht, Cartesia, WellSaid, etc.) down to 3-10 candidate voices for one specific task — an audiobook chapter, a game character's dialogue lines, an app's voice assistant. Now you need to pick ONE, and you don't trust the vendor's "popularity" or tag labels to tell you which one actually fits — because they don't: a widely-cited blind test of 32 ElevenLabs voices for audiobooks found that "professional" tags predicted nothing and louder voices simply won regardless of quality. This tool designs the small, structured blind test that gives you a real answer, without you having to invent the methodology yourself.

This is NOT for comparing different TTS engines/vendors against each other (tools like TTS-Arena already do that well). This is specifically for: "I have my shortlist from one catalog — which one of THESE fits THIS task?"

## What you need to provide

1. **Task description** — what is being narrated/voiced, and what tone/audience it needs (e.g., "middle-grade audiobook narrator, warm and playful" or "cyberpunk RPG villain NPC, menacing and clipped speech").
2. **Your shortlisted candidate voices** — 3 to 10 voice names or IDs from the catalog you're choosing from. (If you only have 1-2, this tool will still help but as a simple A/B rather than a ranking.)
3. **The actual script/text** the voices will read — a real excerpt from your project, 150-400 words, ideally including the hardest content for your task (character names, numbers, emotional range, tricky pronunciations). Do not use a generic sample text; the whole point is testing on YOUR real material.
4. **How many listeners you can get** to help judge (default assumption is 5-10 — coworkers, friends, a few testers; you do not need a paid panel for this lightweight version).
5. (Optional) Any constraints — max clip length, deadline, budget for listener thank-yous.

## What you get back

A single document containing:

1. **Test overview** — your task description, the exact script text that will be used (quoted in full so there's no ambiguity), and your candidate list.
2. **Clip production checklist** — step-by-step instructions for generating the audio clips yourself: every candidate reads the IDENTICAL script text, all clips loudness-normalized to the same level (this matters — unnormalized loudness biases results, louder clips win regardless of actual quality), same file format, same default voice settings across candidates.
3. **Comparison schedule** — a table of randomized pairwise matchups. For 2-5 candidates you get every possible pair; for 6-10 candidates you get a capped, balanced subset so no listener is overloaded, with left/right position and presentation order randomized so no one can learn which slot tends to "win."
4. **Listener instructions and rating sheet** — ready to copy into a Google Form, a printed sheet, or a Slack message. Listeners only ever see "Clip A" and "Clip B" — voice names are never revealed to them. For each pair they give a forced choice (prefer A / prefer B / no preference) plus three quick 1-5 scores: naturalness, how well it fits the stated task/tone, and (for longer clips) listener fatigue.
5. **Results tally template** — an empty table (Voice | wins | losses | no-preference | win-rate | avg scores) you fill in once judgments come back, plus a one-line explanation of why simple win-rate is good enough at this scale (you don't need fancy statistics for a 5-10-person test).
6. **Interpretation notes** — honest caveats: with only 5-10 listeners this is a directional signal, not a scientific-grade ranking. Use the top 1-2 voices it surfaces as your finalists for a last creative gut-check, not as an automatic, unquestionable winner.

## How to use this prompt

Copy everything below the line into your AI chat tool, then answer the five questions with your own real project details.

---

**PROMPT:**

"I need you to design a DIY blind listening test to help me pick the best text-to-speech voice from a shortlist I've already pulled from a vendor's catalog, for one specific task. Here are my details:

- Task description: [describe what's being narrated/voiced and the tone/audience needed]
- Candidate voices (3-10): [list the voice names or IDs]
- Script text the voices will read (150-400 words, my actual project text, not a placeholder): [paste the real script excerpt]
- Number of listeners I can get: [number, or say 'assume 5-10']
- Any constraints: [max clip length / deadline / budget, or 'none']

Please produce:
1. A test overview restating my task and quoting my script text in full.
2. A clip production checklist (identical script for every candidate, loudness-normalized clips, consistent format/settings).
3. A randomized pairwise comparison schedule — full round-robin if I have 5 or fewer candidates, a balanced capped schedule if I have 6-10, with left/right and order randomized, and clips labeled only 'Clip A'/'Clip B' (never reveal voice names to listeners).
4. A ready-to-copy listener instruction sheet and rating form: forced choice (prefer A / prefer B / no preference) plus 1-5 scores for naturalness, task-fit, and listener fatigue (for clips over ~30 seconds).
5. An empty results tally template (Voice | wins | losses | no-preference | win-rate | avg scores per dimension).
6. Honest interpretation notes on what confidence I should place in a 5-10-listener result, and a reminder that this should inform, not replace, final creative judgment.

Do not invent a generic sample script if I haven't given you enough text — ask me for more if needed. Do not claim this small test is statistically equivalent to a large paid panel study."

---

## Honest limits

- This designs the test only. You still have to generate the actual audio clips (using whatever TTS access you already have) and recruit your own listeners — this tool does not call any API or synthesize audio itself.
- With only 5-10 listeners, treat the result as a strong hint, not a verdict. If the decision is high-stakes (a flagship product voice, a large audiobook catalog), consider a larger paid-panel study instead — this tool is for everyday production decisions, not that scale.
- If your vendor's catalog later ships a native "best fit for your script" recommender, that may make this manual process less necessary — check first whether your vendor already offers one.
