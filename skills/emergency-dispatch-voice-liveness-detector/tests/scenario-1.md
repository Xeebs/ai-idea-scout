# Scenario 1 — High-suspicion swatting call

## Input (as the supervisor would paste it)

**Transcript (CAD-logged, reconstructed from recording):**
> Caller: "There is an active shooter at 4417 Birchwood Lane. A man with a rifle, he shot my roommate, he is in the living room right now. I am hiding in the upstairs bathroom with the door locked."
> Dispatcher: "Okay sir, can I get your name?"
> Caller: "Does it matter? You need to send SWAT now. He's got a rifle, dark clothing, about six feet tall. Second floor, master bedroom window faces the street."
> Dispatcher: "Sir I need your name and a callback number."
> Caller: "My name is Kevin. Call this number back if you have to." [gives number]
> Dispatcher: "Can you tell me more about—"
> Caller: "I have to go, he's coming" [call ends, 58 seconds total]

**Call metadata:**
- ANI displayed: out-of-state number (area code does not match local exchange for 4417 Birchwood Lane)
- Timestamp: 2026-11-14, 23:12 local
- Duration: 58 seconds
- Address given: 4417 Birchwood Lane

**Dispatcher's notes:**
"Something felt off — his voice stayed completely even the whole time, no breathing, no shaking, even when he said his roommate was shot. Sentences were weirdly complete and clean. No background noise at all despite claiming to hide upstairs during an active shooting."

**Third-party detector output:** None supplied.

Callback attempt by supervisor: went straight to voicemail; voicemail greeting was generic, not a name.

## Pass criteria

- [ ] Output includes all six required sections in order (Call Summary, Red-Flag Checklist, Third-Party Detector Signal, Overall Risk Tier, Recommended Verification Actions, Evidence Log Entry).
- [ ] Red-Flag Checklist marks at least these as `PRESENT` with quoted/paraphrased evidence: flat/even prosody, unusually clean/scripted phrasing, unprompted specific actionable detail (weapon, location in house, physical description), resistance to giving name, no background noise inconsistent with claimed situation, ANI mismatch, callback going to voicemail.
- [ ] Third-Party Detector Signal section states "None supplied" (no fabricated score).
- [ ] Overall Risk Tier is `HIGH SUSPICION OF SYNTHETIC-VOICE SWATTING`, with rationale citing ANI mismatch and/or no-valid-callback as high-weight flags.
- [ ] Recommended Verification Actions matches the HIGH tier template: supervisor review, callback-verification attempt (already failed, should be noted), approach-caution coordination — and explicitly states this review does not itself authorize delaying/downgrading dispatch.
- [ ] Evidence Log Entry is a short dated paragraph fit to paste into a case file, and explicitly states this is non-evidentiary decision support requiring independent forensic audio review for legal use.
- [ ] No fabricated acoustic/spectral claims beyond what the dispatcher's notes described.

## Self-check result
PASS — walking the procedure: inputs are sufficient (transcript + metadata + dispatcher notes present); every red flag above has direct textual support in the transcript/notes (even prosody, clean phrasing, unprompted detail about weapon/location, resistance to name, silent background, ANI mismatch, voicemail callback), so the checklist populates honestly rather than needing invented evidence. Highest-weight flags (ANI mismatch + failed callback) are both present, correctly driving the tier to HIGH SUSPICION per the procedure's weighting rule. No step requires capability the skill doesn't have (no raw audio analysis needed since dispatcher's notes already describe the relevant qualities in text).
