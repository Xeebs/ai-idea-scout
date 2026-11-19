# Scenario 1 — Classic cascaded bot (expect mostly BOLTED-ON)

## Input (what the user pastes)

> We built an appointment-booking voice bot on LiveKit Agents. Here's roughly how our main loop works:
>
> ```python
> async def on_user_turn_finished(transcript: str):
>     is_speaking = True
>     response = await llm.complete(transcript)  # blocks until full text is back
>     audio = await tts.synthesize(response.text)  # whole response at once
>     await room.publish_audio(audio)
>     is_speaking = False
>
> async def on_user_started_talking():
>     if is_speaking:
>         await room.stop_audio()
>         is_speaking = False
>     # that's it, nothing else happens
> ```
>
> `is_speaking` is a global bool checked in a couple of other places too (like deciding whether to accept a new transcript). We're using LiveKit's STT/VAD out of the box. Latency is fine for simple questions but people complain the bot "goes blank" for a second or two on longer answers, and if you interrupt it mid-sentence it just restarts the whole thing with no memory of where it was.

## Expected output characteristics (pass/fail checklist)

- [ ] Checkpoint A (reasoning-to-speech handoff) scored **BOLTED-ON**, citing the `llm.complete` → `tts.synthesize(response.text)` sequence as evidence (full text generated before synthesis starts at all).
- [ ] Checkpoint B (turn-state) scored **BOLTED-ON**, citing `is_speaking` as an untyped global boolean checked in multiple places.
- [ ] Checkpoint C (commit-confidence gating) scored **BOLTED-ON**, since there's no chunking or confidence concept at all — the whole response is synthesized as one unit.
- [ ] Checkpoint D (barge-in) scored **BOLTED-ON** or **PARTIAL**, citing that interruption just stops audio and flips a flag with "nothing else happens" / restarts from scratch with no recovery logic.
- [ ] Migration tier for A and C is **Rebuild** (the synchronous full-completion-then-synthesize call needs the reasoning call itself restructured); tier for B is **Adapt** (boolean → explicit state machine is feasible without rebuilding the LLM call); tier for D is **Rebuild** or **Adapt** depending on reasoning given, but must be justified, not asserted.
- [ ] "What to keep" explicitly names LiveKit's STT/VAD and audio transport as untouched — does NOT recommend discarding LiveKit.
- [ ] "What to change, in order" sequences B (state machine) before or alongside D (interruption recovery), with a stated reason (D depends on B existing).
- [ ] No specific millisecond/latency number is invented anywhere in the output (user gave no real numbers, only "a second or two" as a vague complaint) — if a time figure appears, it must be hedged as qualitative/hypothesis, not asserted as fact.
- [ ] Report includes a "Validate before and after" section recommending the user measure something concrete post-migration (e.g., time-to-first-audio on sample calls).

**Fail conditions**: any checkpoint scored without citing something from the pasted code; any recommendation to drop/replace LiveKit's transport; any fabricated latency number; proceeding to a full scorecard despite all 5 inputs actually being present here (they are, so a full scorecard IS expected — don't flag this as missing-input).
