# Scenario 1 — Clinic appointment-booking voice bot, per-component metrics only

## Input

A healthcare scheduling startup describes its setup:

1. **What we currently measure**: "We track ASR word-error rate weekly using a vendor dashboard (currently 4.2% WER). We also have an LLM response-quality score — GPT-4o rates each individual bot turn 1-5 on 'was this response appropriate given the previous user turn,' averaged across 200 sampled turns/week. We don't check TTS naturalness at all, our TTS vendor just claims it's 'human-like.'"
2. **How we measure it**: "ASR WER is automated against a fixed 50-call reference set. The LLM response-quality score is also automated — GPT-4o scores each turn right after the call ends, no human ever reviews these scores or checks if GPT-4o is any good at this judgment."
3. **Our call types**: "Appointment booking (new patient), appointment rescheduling, appointment cancellation."
4. **Example transcript** (one provided): a call where a patient says "actually can we push this to next Tuesday instead" mid-call after already confirming a Thursday slot; bot responds "Great, you're confirmed for Thursday at 2pm!" — missing the reschedule request entirely, then the call ends.
5. **Known pain points**: "We've gotten a few complaints about 'the bot ignored what I said' but didn't have a way to track or categorize them."

## Pass criteria

- [ ] Coverage Scorecard correctly identifies ASR as the only `Covered` or near-covered layer, LLM/dialogue as `Partial` (turn-level only, no human calibration), TTS as `Missing`, and conversation-level/multi-turn as `Missing`.
- [ ] Explicitly flags the GPT-4o turn-level judge as unvalidated against human ratings (Partial at best), not Covered, even though it sounds automated and sophisticated.
- [ ] Identifies "per-component-only, no full-call check" as a top gap, and explicitly connects it to the goal-resolution failure shown in the transcript.
- [ ] Failure-mode taxonomy for "appointment rescheduling" includes something equivalent to "mid-call intent change missed" or "stated reschedule not detected," distinct from the booking/cancellation taxonomies (not one generic taxonomy reused across all three call types).
- [ ] Worked Examples section maps the provided transcript's Thursday/Tuesday mixup onto a taxonomy entry, explicitly as a goal-resolution/context-retention failure.
- [ ] Does not invent any statistic (e.g., does not claim a specific complaint count or CSAT number beyond "a few complaints," which is all that was given).
- [ ] Does not recommend a specific named vendor/product as "the" fix.
- [ ] Recommended Next Steps includes something about human-calibrating the existing LLM judge and something about adding a goal-resolution/multi-turn check, prioritized ahead of TTS naturalness.

## Fail conditions

- Scores the GPT-4o turn-level judge as `Covered`.
- Produces one identical taxonomy table reused verbatim across booking/rescheduling/cancellation.
- Fabricates a WER number, complaint count, or CSAT figure not given in the input.
- Omits the Worked Examples mapping despite a transcript being supplied.
- Recommends a specific paid eval vendor by name as the solution.
