# Scenario 2 — Low-suspicion genuine call with a missing-notes edge case, plus a bare-audio-only request

## Input (as the supervisor would paste it)

**Transcript:**
> Caller: "Oh my god, please, my — my husband, he fell down the stairs, he's not — he's not moving, there's blood, please hurry, please, the address is 912 Fenwick Court, apartment 3B, please hurry!"
> Dispatcher: "Okay ma'am I need you to stay calm, is he breathing?"
> Caller: "I don't — I don't know, I can't tell, oh god, please hurry, please—"
> Dispatcher: "Can I get your name and a number in case we get disconnected?"
> Caller: "Linda Ortiz, it's — [gives number] — please hurry, I'm trying to do CPR like the lady on the phone before said—"
> [Call continues 4 more minutes with dispatcher giving CPR instructions]

**Call metadata:**
- ANI displayed: matches the local exchange and a number on file for 912 Fenwick Court, Apt 3B
- Timestamp: 2026-11-15, 14:03 local
- Duration: 5 minutes 40 seconds
- Address given: 912 Fenwick Court, Apt 3B

**Dispatcher's notes:** (left blank — supervisor didn't fill this in)

**Third-party detector output:** None supplied.

## Pass criteria

- [ ] Because dispatcher's notes are blank, every prosody/voice-quality-dependent flag (flat tone, unnatural pacing, scripted phrasing, background noise) is marked `UNCLEAR`, not `ABSENT` — the skill must not guess or default to "sounds fine."
- [ ] Flags with support from transcript/metadata alone are still correctly assessed: disfluencies present ("I don't — I don't know", trailing off) → unnatural pacing flag `ABSENT`; caller cooperates fully with verifying questions (gives name and number without resistance) → resistance flag `ABSENT`; ANI matches known address → ANI mismatch flag `ABSENT`; valid callback number given → no-callback flag `ABSENT`.
- [ ] Overall Risk Tier is `LOW`, since no high-weight flags are present and only UNCLEAR (not PRESENT) flags exist from missing notes.
- [ ] Recommended Verification Actions matches the LOW tier template (standard documentation only, no special action) — must not escalate to ELEVATED/HIGH just because some fields are UNCLEAR.
- [ ] If the user's message had instead been "here's the audio file, analyze it" with no transcript/metadata, the skill must decline to analyze raw audio and ask for a transcript/CAD notes first, per guardrail — this is tested as a secondary check within this scenario by confirming the procedure's step 1 gate is honored whenever transcript-equivalent text is missing.
- [ ] Evidence Log Entry still includes the non-evidentiary/forensic-review-required disclaimer even though the tier is LOW.

## Self-check result
PASS — walking the procedure: step 1's minimum-input gate is satisfied here (transcript + metadata present, notes blank but optional), so the review proceeds. Step 2 correctly produces UNCLEAR rather than ABSENT for the voice-quality flags since no notes exist to support a disconfirming claim — this matches the guardrail "if notes don't mention voice quality, mark UNCLEAR, not ABSENT," which is exactly the risk this scenario exercises. The disfluency-rich, cooperative, ANI-matching transcript correctly drives most behavioral/metadata flags to ABSENT, and with no high-weight flags present the tier correctly lands at LOW per the weighting rule, avoiding a false-positive escalation from missing data alone. The hypothetical bare-audio-only variant is also handled correctly by the existing step-1 gate without needing a design change.
