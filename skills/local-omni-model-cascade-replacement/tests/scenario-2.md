# Scenario 2 — High-volume order-intake line with a genuinely blocking tool dependency

## Input (as the user would paste it)

> We run a food-delivery order-intake phone line at real scale. Current stack: Twilio's built-in transcription (effectively Whisper-based) for STT, Claude Haiku for the LLM, ElevenLabs Flash for TTS. Combined cost comes out to about $0.021/minute. Volume is about 480,000 call-minutes/month, with peak concurrency around 140 simultaneous calls during Friday/Saturday dinner rush. We haven't measured stage-by-stage latency, just end-to-end: p50 around 900ms, p95 around 2.1s.
>
> Tools:
> - `build_order_item(item_name, size, modifiers)` — this one is critical: as the caller lists modifiers ("large, extra cheese, no onions, add bacon..."), we stream the partial arguments into the live order summary shown to the caller in our app in real time, so they can see their order being built as they talk. This is core to the product experience, not a nice-to-have.
> - `lookup_menu_item(query)` — single call, returns matches.
> - `apply_promo_code(code)` — single call.
> - `finalize_order(order_id, payment_method)` — single call.
>
> No GPU hosting budget set yet — we want to know what it would take.

## Expected output must include

- [ ] Verdict should land on **NO-GO** (or at minimum CONDITIONAL-GO phrased as strongly leaning no) specifically because `build_order_item`'s real-time partial-argument streaming into a live UI is flagged as **Blocking** — the skill's default assumption (no streaming partial args unless confirmed) applies, and this feature is core to the product, not a redesignable edge case. If the model marks it CONDITIONAL-GO instead of NO-GO, it must explicitly justify why a blocking core-feature dependency doesn't sink the verdict (e.g. a named workaround); a silent CONDITIONAL-GO with no workaround for a Blocking item fails.
- [ ] Tool-calling compatibility audit correctly lists `build_order_item` as Blocking with reasoning tied to streaming partial args, and the other 3 tools as Likely compatible.
- [ ] Capacity math converting 140 concurrent calls into a GPU count using the stated reference range (roughly 10-18 GPUs depending on which end of the 8-15/GPU range is used), explicitly labeled as a default needing a load test, since no hosting budget was given to check against.
- [ ] Cost comparison table: current cost ≈ $0.021 × 480,000 ≈ $10,080/month vs. projected hardware+electricity cost at the computed GPU count, with every unsupplied price (GPU, electricity) labeled as a reference default.
- [ ] Latency section explicitly marked as directional/low-confidence, since only end-to-end numbers were given, not stage-by-stage.
- [ ] Confidence & caveats section noting that no GPU hosting budget was supplied, so the recommendation is a sizing estimate, not a budget check.

## Fail if

- The skill treats `build_order_item`'s streaming requirement as a minor "needs redesign" item without acknowledging it may not be preservable at all with current local omni-model tool-calling, and issues a clean GO.
- The latency comparison is presented as a hard, measured number despite only end-to-end data being given.
- GPU/electricity costs are stated as fact rather than labeled defaults.
