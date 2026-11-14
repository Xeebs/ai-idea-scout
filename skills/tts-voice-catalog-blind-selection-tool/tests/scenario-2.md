# Scenario 2: Game studio NPC voice, incomplete input requiring clarification

## Input

> Task description: We need a voice for a recurring NPC merchant in our RPG — sly, fast-talking, a little untrustworthy, mostly short barter/dialogue lines.
>
> Candidate voices: Voice_014, Voice_088, Voice_142 (IDs from our Cartesia shortlist).
>
> Script text: (none provided — the user just says "use whatever sample text you think fits")
>
> Listeners available: 3 (just me and two other devs).
>
> Constraints: clips must be under 20 seconds each since these are short barter lines.

## Expected output characteristics (pass/fail checklist)

- [ ] The skill does NOT silently invent a generic placeholder script and proceed — per the guardrails, it must stop and explicitly ask the user for real script/dialogue text from their own project (e.g., actual barter lines), rather than fabricating "sample" NPC dialogue and treating the test as ready to run.
- [ ] If the skill instead demonstrates with a clearly-labeled placeholder while asking for the real text (acceptable variant), it must unambiguously flag that this is a placeholder pending real text, not present it as the finalized test script.
- [ ] Once given real script text (assume the follow-up: "Fine, here's a line: 'Ah, a customer with taste — or maybe just desperation. Either way, forty gold and it's yours, no haggling... well, a little haggling.'"), the output correctly treats N=3 candidates as within the "2-5: full round-robin" branch — exactly 3 pairs (014 vs 088, 014 vs 142, 088 vs 142).
- [ ] With only 3 listeners, the output explicitly notes this is a very small sample and should be treated as a light directional signal, consistent with the guardrail against overclaiming statistical confidence — ideally flags that 3 listeners each judging all 3 pairs is a reasonable minimal setup, not a robust one.
- [ ] Clip production checklist still includes the loudness-normalization callout and identical-script-per-candidate instruction even for these short (<20s) clips, and respects the stated 20-second constraint by noting clips should be trimmed/selected to fit that limit.
- [ ] Rating sheet appropriately downplays or omits heavy emphasis on "listener fatigue" scoring given clips are very short (<20s) — per the procedure, fatigue scoring is primarily meant for longer clips, so the output should not force a fatigue question that doesn't make sense for a 15-second barter line, or should clearly mark it optional for short-clip tasks.
- [ ] Voice IDs (014/088/142) are never exposed to listeners in the rating sheet — only "Clip A"/"Clip B" labels, consistent with the guardrail.
- [ ] No claim that the skill itself generated audio via Cartesia's API — it only produces the test design document.

## Self-check notes
This scenario specifically tests the "never invent a script" guardrail and the N=2-5 full-round-robin branch, plus the fatigue-dimension judgment call for very short clips. Walking through the procedure: step 1 catches the missing script and must pause for clarification before any schedule/rubric is built; once the real line is supplied, step 4's N=3 branch yields a clean 3-pair round-robin solvable by 3 listeners judging all pairs. The 20-second constraint is handled in the clip production checklist (step 3) as a trimming/selection note. This is a realistic, slightly messier input (incomplete on the first pass) and the skill produces a usable, correctly-scoped output after the one necessary clarification — scenario passes.
