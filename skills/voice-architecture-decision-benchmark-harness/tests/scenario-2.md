# Scenario 2: Consumer retail support bot (fast, casual, lean team)

## Input

A 2-person team at a direct-to-consumer retail brand wants a voice agent that answers phone calls about order status, returns, and basic product questions. They give the following answers:

1. **Domain/regulatory context**: Retail customer support, no compliance/audit requirement beyond normal call-quality monitoring they already do for human agents.
2. **Languages/vocabulary**: English only, everyday conversational language about orders and products — no specialized or technical vocabulary.
3. **Latency/conversational feel**: This is explicitly the differentiator for them — they want the bot to feel like talking to a fast, friendly human, with natural interruption handling (customers often talk over the bot to correct an order number).
4. **Tool-calling needs**: One or two simple lookups (order status API, return policy lookup) — nothing safety- or money-critical if a lookup occasionally needs a retry.
5. **Team size/expertise**: Just 2 engineers, neither with deep speech/NLP background; they explicitly want a single managed vendor rather than integrating and maintaining three separate components.
6. **Vendor lock-in tolerance**: High — they're a small team moving fast, comfortable re-platforming in a year if a better option comes along, since nothing regulatory is at stake.

## Expected output characteristics (pass/fail checklist)

- [ ] Restates the use case correctly (retail support, no compliance need, casual English, simple lookups, small team wanting a managed vendor)
- [ ] Scores compliance/observability at 0 (no compliance need)
- [ ] Scores vocabulary specificity at +1 (everyday conversational)
- [ ] Scores latency/naturalness priority at +2 (explicitly the differentiator, barge-in handling matters)
- [ ] Scores tool-calling needs at -1 (a couple of simple lookups, not costly failures) — not -2
- [ ] Scores team expertise/bandwidth at +2 (small team wants one managed vendor)
- [ ] Scores lock-in tolerance at +1 (comfortable re-platforming)
- [ ] Total sum is clearly ≥ +2, producing a **Speech-to-Speech** recommendation
- [ ] Confidence is stated as High or Medium (most factors agree in direction; tool-calling factor is a mild drag against perfect unanimity)
- [ ] Names at least one specific risk of the speech-to-speech path tied to a factor (e.g., harder to debug tool-call failures without text-level tracing, some vendor lock-in despite stated tolerance)
- [ ] Names at least one specific risk of the cascaded alternative tied to a factor (e.g., added integration/maintenance burden this 2-person team doesn't want, given they explicitly asked for a managed vendor)
- [ ] Does NOT cite a specific invented latency number for any named vendor
- [ ] Closes with a concrete validation step (e.g., run a short pilot with real customer call recordings to confirm barge-in/interruption handling feels natural before full launch)

**Fail conditions**: recommends cascaded; treats the simple order-lookup tool calls as safety-critical (-2) and inflates them into a reason to recommend cascaded; omits the barge-in/naturalness driver from the reasoning; presents the result as a guaranteed outcome rather than a same-day judgment call.
