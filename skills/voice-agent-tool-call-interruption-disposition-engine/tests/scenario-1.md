# Scenario 1: Telehealth appointment voice agent

## Input (what the user pastes)

> We're hardening our telehealth scheduling voice bot before launch. Here's our tool manifest:
>
> 1. `check_appointment_availability` — looks up open slots for a provider. Read-only. ~200ms, hits our own scheduling DB. Result useful for about 30 seconds (slots can get taken fast).
> 2. `check_insurance_eligibility` — calls a third-party clearinghouse API to verify the caller's insurance covers the visit type. Read-only. Slow, ~3 seconds, and it costs us a small per-call fee to the clearinghouse. Result is valid for the rest of the day (eligibility doesn't change hour to hour).
> 3. `reschedule_appointment` — writes the new appointment time to our EHR the moment it's called; there's no "preview" step, it commits immediately. No idempotency key support currently. If called twice with different times, both calls would apply in sequence (last write wins), which could leave the wrong time if a caller interrupts partway through correcting themselves.
> 4. `send_confirmation_sms` — sends a text confirming whatever just changed. Side-effecting (sends a real SMS) but trivial cost, and sending it twice just means the caller gets two identical texts, which is annoying but harmless.
> 5. `cancel_appointment` — side-effecting, writes to the EHR immediately on invocation, same as reschedule. No way to preview or abort before it writes. Cancelling twice is a no-op (idempotent in that narrow sense — the second call just confirms "already cancelled").

## Expected output characteristics (pass/fail criteria)

- [ ] Produces the four-section output structure (Recommendations table, Needs Classification, Must Resolve Before Launch, Notes) — fail if any section is silently dropped.
- [ ] `check_appointment_availability` → `finish-and-cache` with TTL ~30 seconds (idempotent, and though cheap-ish, has a stated staleness window so caching is reasonable) OR `finish silently, discard` is acceptable only if justified as "cheap enough that caching adds little value" — either is defensible as long as the 30s staleness tolerance is referenced, not invented differently.
- [ ] `check_insurance_eligibility` → `finish-and-cache` with a TTL on the order of "rest of the day" / hours, justified by slow+costly+idempotent. Fail if it recommends discarding this result (wastes a paid, slow call) or if it invents a different TTL number not grounded in "rest of the day."
- [ ] `reschedule_appointment` → `finish-then-confirm`, NOT `cancel-and-discard` (it commits instantly, so cancellation is impossible) and NOT a bare "finish silently, discard" (that's the exact harm the idea is built to prevent — a reschedule to the wrong time proceeding after a caller's correction attempt). Justification must reference the no-idempotency-key / commits-immediately / harmful-if-wrong combination. This is the single most important line in the scenario — fail the scenario outright if this is wrong.
- [ ] `send_confirmation_sms` → `finish silently, discard`, justified by "side-effecting but low-harm if duplicated."
- [ ] `cancel_appointment` → `finish-then-confirm` (commits instantly, no pre-commit cancellability stated) is the expected/safe answer; `finish silently, discard` would only be acceptable if explicitly justified by "cancelling twice is a harmless no-op," which is defensible given the input — either is a pass as long as the commits-instantly-so-no-cancel-and-discard point is made explicitly. Fail if it recommends `cancel-and-discard` for this tool.
- [ ] No tool lands in "Needs Classification" or "Must Resolve Before Launch" incorrectly — all five tools have enough stated information to get a real recommendation, not a punt. Fail if the output dodges a clear case by asking for more info it already has.
- [ ] Does not invent any number (TTL, cost, latency) not present in the input.
