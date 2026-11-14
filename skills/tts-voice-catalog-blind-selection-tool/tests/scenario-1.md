# Scenario 1: Indie audiobook producer, 7 candidate voices

## Input

> Task description: I'm narrating a self-published middle-grade fantasy novel, "The Clockwork Orchard." Narrator needs to sound warm, a little mischievous, and able to handle an 11-year-old protagonist's dialogue as well as a gruff old wizard's dialogue in the same passage.
>
> Candidate voices (from ElevenLabs Voice Library, already shortlisted): Aria, Brennan, Clara-Narrator, Finch, Guinevere, Hollis, Ivy-Storyteller.
>
> Script text: "Mira pressed her palm against the orchard gate, and the brass gears beneath the bark groaned awake. 'You're late,' rasped a voice from the twisted apple tree — old Thistlewood, his wooden jaw creaking with every word. 'Thirty-seven years I've waited for someone fool enough to turn that key.' Mira swallowed hard. 'I'm not fool,' she said, though her voice cracked on the second word, 'I'm just the only one who showed up.' The tree's eyes, two clockwork lanterns, flickered amber, then gold. 'Good enough,' Thistlewood said. 'Good enough has opened stranger doors than this one.'"
>
> Listeners available: 6 (my critique group).
>
> Constraints: none specified.

## Expected output characteristics (pass/fail checklist)

- [ ] Test overview section quotes the full script text verbatim (not paraphrased or shortened), restates the task/tone (warm, mischievous, dual child/old-man dialogue range), and lists all 7 candidate voices.
- [ ] Clip production checklist explicitly instructs identical script for all 7 voices, loudness normalization to a stated consistent target, and holding voice settings (speed/stability) constant across candidates.
- [ ] Since N=7 (in the 6-10 range), the comparison schedule uses the capped/balanced design, NOT full round-robin (full round-robin would be 21 pairs — schedule should be noticeably fewer, roughly ~21 capped toward 3×7=21 is actually at the boundary; acceptable if it explains the cap reasoning, but it should not silently blow past a sane per-listener load). Each of the 7 voices appears in at least 4 comparisons per the procedure.
- [ ] Left/right (Clip A/B) assignment and presentation order are explicitly stated as randomized, and voice names are never exposed to listeners in the rating sheet — only "Clip A"/"Clip B" labels.
- [ ] Rating sheet includes forced choice (prefer A/B/no preference) plus naturalness, task-fit, and fatigue scores (fatigue is relevant since this is a short clip, so the output should note fatigue scoring is most relevant for longer clips — not force it awkwardly for this short excerpt, or at minimum not omit it from the template even if flagged as less critical here).
- [ ] Results tally template table has the specified columns (Voice | wins | losses | no-preference | win-rate | avg naturalness | avg task-fit | avg fatigue).
- [ ] Interpretation notes explicitly caveat that 6 listeners is a small/directional sample, not a statistically definitive ranking.
- [ ] Output does not attempt to actually synthesize audio, call an ElevenLabs API, or claim to have done so — it is a design document only.

## Self-check notes
With 7 candidates and 6 listeners, the procedure's N=6-10 branch applies: capped schedule near 3×7=21 comparisons total, each voice in ≥4 comparisons — this is achievable (e.g., a near-round-robin minus a few non-critical pairs) and distributable across 6 listeners (~3-4 comparisons per listener). The task description and script give real differentiating content (two character voices in one short passage), which is exactly the kind of script this skill asks for — scenario passes.
