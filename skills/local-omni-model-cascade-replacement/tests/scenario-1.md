# Scenario 1 — Appointment-booking shop, straightforward tools, clear GO/CONDITIONAL case

## Input (as the user would paste it)

> We run a dental-clinic appointment-booking voice line. Current stack: Deepgram Nova-3 for STT, GPT-4o-mini for the LLM, Cartesia Sonic for TTS. Combined vendor cost is about $0.016/minute. We handle roughly 42,000 call-minutes a month (around 1,100 calls, avg 6 min each), peaking at about 18 concurrent calls during business hours. Measured latency: STT p50 180ms/p95 310ms, LLM p50 220ms/p95 450ms, TTS p50 140ms/p95 260ms (end-to-end p50 ~540ms, p95 ~1020ms).
>
> Tools our agent calls:
> - `check_availability(date, service_type)` — single call, returns a list, no streaming.
> - `book_appointment(patient_name, date, time, service_type)` — single call per turn, waits for full args.
> - `cancel_appointment(confirmation_id)` — single call.
> - `send_sms_confirmation(phone, appointment_id)` — currently fired in parallel with `book_appointment` in the same turn so the text goes out the instant booking succeeds, without an extra round-trip.
>
> We have budget for at most 2 on-prem GPUs (24GB each) if we self-host. We don't have a load test yet.

## Expected output must include

- [ ] A verdict line: given one tool (`send_sms_confirmation`) depends on parallel tool calls, the three single-call tools are fine, so the correct verdict is **CONDITIONAL-GO** (not GO, since one tool needs redesign; not NO-GO, since there's a clear workaround — sequential calls, i.e. send SMS right after booking confirms, costing one extra turn/latency tick).
- [ ] Cost comparison table showing current cost ≈ $0.016 × 42,000 ≈ $672/month, projected hardware+electricity cost using the stated reference defaults (labeled as defaults), and a GPU count recommendation.
- [ ] Capacity math: peak 18 concurrent calls converted to a GPU count using the ~8-15 concurrent/GPU reference (so roughly 2 GPUs needed at the stated default), checked against the user's 2-GPU budget — should note it's right at the edge and flag the load test as mandatory before committing.
- [ ] Latency estimate using the user's actual stage-by-stage numbers (marked as measured, not purely directional, since real numbers were given) — should note the cascade's current p95 1020ms vs. a single-hop local estimate, directionally favoring local.
- [ ] Tool-calling compatibility audit table listing all 4 tools, correctly classifying `check_availability`, `book_appointment`, `cancel_appointment` as Likely compatible, and `send_sms_confirmation` as Needs redesign (parallel call dependency) with the sequential-call workaround named.
- [ ] A "Required validation" section naming the load test for the 18-concurrent-call peak against the 2-GPU budget, plus a barge-in/tool-accuracy benchmark.
- [ ] No fabricated GPU/electricity prices — reference defaults must be explicitly labeled as defaults, not stated as fact.

## Fail if

- The verdict is a flat GO (ignores the parallel-call dependency) or a flat NO-GO (treats one fixable tool as a blocker without noting the workaround).
- The capacity/GPU math is skipped or the 18-concurrent-call number isn't converted into a GPU count.
- Any dollar figure is presented as certain rather than a projection.
