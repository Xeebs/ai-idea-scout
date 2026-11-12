# Scenario 2 — Greenfield, setting up tracing for the first time

## Input (realistic, not a toy example)

> We're about to ship GenAI tracing for our customer-support copilot. Nothing is instrumented yet — we're planning to use the OpenTelemetry GenAI semantic conventions and send everything to Honeycomb. We want to get the default policy right before we turn it on, because we've heard horror stories about prompt-capture cardinality blowing up bills. We expect to ramp to about 2 million LLM calls/month within the quarter, currently more like 200k/month while we're in limited beta. We don't have real error-rate data yet since nothing is live, but our dev environment testing suggests failures (model errors, content-filter rejections, malformed tool calls) happen around 5% of the time. We do want to be able to replay the exact prompt for any support conversation where a customer complained, for up to 30 days. We haven't set a specific cost target — we just don't want to repeat what we've heard other teams go through.

## Pass criteria

- [ ] Output has all six sections in order.
- [ ] Inputs Received flags that the exact production error rate is not yet known (dev-environment 5% estimate) and labels it as an assumption/estimate rather than a measured figure; states the 200k/month current vs. 2M/month ramp target volumes.
- [ ] Because the input says "nothing is instrumented yet," the Attribute Classification Table is built from OpenTelemetry's standard GenAI semantic-convention attribute set (`gen_ai.prompt`, `gen_ai.completion`, `gen_ai.request.model`, `gen_ai.usage.*` tokens, etc.) rather than refusing to proceed for lack of an existing config.
- [ ] Truncation Plan default cap (~2KB, root-span-only) is proposed and explicitly reconciled against the stated 30-day full-replay requirement for complained-about conversations — the output must address the tension (e.g., recommending either a specific "flagged conversation" exception that captures full content for complaint cases, or otherwise explicitly resolving how 30-day full replay is preserved despite the general truncation default) rather than silently ignoring the replay requirement.
- [ ] Sampling Policy proposes a concrete default rate (since no target reduction was given) and shows the math using the ~5% estimated error rate and one of the two stated volumes, with that error rate clearly marked as a dev-environment estimate, not a production measurement.
- [ ] Sampling Policy explicitly reserves 100% capture for errors/failures and offers or discusses a way to flag/retain complaint-linked conversations in full (tying back to the 30-day replay need) rather than leaving that requirement unaddressed.
- [ ] Debuggability-tradeoff sentence is present and specific to this scenario's proposed rate.
- [ ] PII/Compliance Flags raises the customer-support content angle explicitly — customer conversations plausibly contain PII, and the output should name this as a decision the team must confirm for any Hash-and-truncate or Excluded-by-default attribute touching conversation content.
- [ ] Open Questions includes at minimum: confirmation of real production error rate once live, and explicit confirmation of the PII handling decision for support-conversation content.
- [ ] Output explicitly states this is a draft to implement/validate, not already-enforced policy.
- [ ] Fail if: the skill refuses to produce a policy because "nothing is instrumented yet"; the 30-day complaint-replay requirement is never mentioned or reconciled with the truncation default; any error-rate or volume number is presented as measured fact rather than flagged as a dev-environment estimate/stated ramp target.
