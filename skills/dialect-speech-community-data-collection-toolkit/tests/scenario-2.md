# Scenario 2 — Incomplete inputs, web upload fallback, researcher collective

## Input

> We're a small group of three linguistics grad students putting together a side project to collect some recordings of a regional dialect of Quechua spoken in a specific valley in Peru that doesn't have much recorded data. We're planning to put up a simple web form where people can upload audio. Not sure yet exactly what we'll use the data for beyond "building a dataset" — could be ASR, could just be archival. Haven't thought about legal stuff at all yet. No idea if kids would submit anything, probably not but we haven't restricted it.

(Note: this input is deliberately vague on required fields — "intended use" is not clearly pinned down, and "organizing" type is implied (academic/researcher collective) but not labeled explicitly, and the legal/governance context is "haven't thought about it" rather than a clean "none known.")

## Expected output / pass criteria

The output must:

1. **Ask a clarifying question or explicitly flag the ambiguity** on intended use before drafting, or — if it proceeds — draft for the broader case (treat "ASR or archival" as the use, not silently picking just one) and say so.
2. **Not silently invent** a specific valley name, a specific local Quechua dialect feature, or any specific cultural/debate topic for the elicitation prompts — the input gives "a specific valley in Peru" with no further detail, so community-specific prompts must stay generic (e.g., "describe a tradition specific to where you live") rather than naming a real Quechua custom the model wasn't told about.
3. **Flag the complete absence of legal/governance review loudly and early** — "haven't thought about legal stuff at all" is a stronger gap than scenario 1's "no lawyer yet," and the upfront warning must reflect that nothing has been considered, not just that review is pending.
4. **Treat the minors question as unresolved, not as "no"** — "probably not but we haven't restricted it" is not a clear no. The output should flag this as an open item requiring a decision (either add age verification/restriction, or add guardian-consent language) rather than drafting a script that silently assumes no minors.
5. Produce a **web-upload-appropriate written consent version** as the primary version (since the stated channel is a web form), while still including a spoken-script version as the README/SKILL promises both versions regardless of stated channel.
6. **15-25 elicitation prompts** across all five bands, all open-ended/spontaneous, none naming unsupplied local specifics.
7. **Moderator rubric** present and complete even though this group is tiny (three students) — the output should not assume a large moderation team, and the escalation note field should be usable by a single moderator checking their own group's submissions.
8. **Closing "still open" list** must include at minimum: no legal/governance review done, intended use not finalized, and minors policy undecided.

**Fail** if the output picks one intended use silently without flagging the ambiguity, invents real-sounding Quechua-specific cultural content, treats "probably not" as settled as "no minors," or produces a consent script without a loud up-front disclaimer given how little groundwork this group has done.
