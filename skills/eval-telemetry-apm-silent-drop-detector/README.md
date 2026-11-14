# Eval Telemetry Silent-Drop Risk Audit

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then add your own tracing setup details at the bottom where marked, and send it. No installation, no connectors, no code required.

## What this does

If your team added LLM eval/experiment tracing (prompts, completions, judge rationales, multi-turn transcripts) on top of a general-purpose APM or observability pipeline — Datadog, New Relic, Grafana/Tempo, a self-managed OpenTelemetry Collector, Langfuse, Lumigo, Groundcover, Braintrust, or similar — there's a real, documented failure mode: that pipeline was built for short, low-cardinality trace attributes, not multi-kilobyte LLM payloads, and it will silently truncate or drop the oversized fields rather than error out. Your eval dashboard and judge scores can look complete while quietly being built on cut-off data. Datadog itself only caught and fixed this in its own product in November 2026 (dd-trace-py PR #21690) — meaning the failure mode is real enough that a funded observability vendor missed it in its own pipeline for years.

This is a one-time, paste-and-run audit. It does not touch your live pipeline or run any code against it — it reasons from a written description of your setup and tells you where the risk is and what to do about it, ranked by effort. It is not a substitute for actually probing your real pipeline with oversized synthetic payloads (that's a separate, code-level project, not this prompt).

## What you need to provide

1. **Vendor/stack** — e.g. "Datadog APM + dd-trace-py 2.x", "generic OTel Collector forwarding to Grafana Tempo", "Langfuse SDK v3", "Vercel AI SDK with an OTel exporter".
2. **Any custom config** you've applied — attribute length limits, batch processor settings, exporter type (OTLP/gRPC vs HTTP), and whether your eval/experiment spans ride inside the same trace as your regular APM spans or go through a separate export path.
3. **Typical payload sizes** — roughly how long a typical prompt, completion, judge rationale, and full multi-turn transcript run (characters or KB is fine as an estimate).

If you don't have #2 or #3, provide what you can — the audit will mark anything it can't verify as "unconfirmed" rather than guessing, which is still useful.

## How it reasons (the procedure, in prose)

The audit first matches your named vendor/stack against a small catalog of documented limits: Langfuse caps ingested events around 2MB; Groundcover truncates spans around 10KB; Lumigo caps individual fields around 2KB; Braintrust caps OTLP payloads around 10MB; pre-fix Datadog APM makes eval spans inherit ordinary APM trace/attribute limits because there's no dedicated large-payload path; and the Vercel AI SDK has a documented case where span attributes get truncated *even below* a manually raised `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT`, so raising that one setting isn't a reliable fix for that specific stack. If your vendor isn't one of these, the audit says so explicitly and reasons from general OTel/APM mechanics (attribute length caps, OTLP message-size caps, drop-on-overflow in batch processors) instead of inventing a number for your vendor.

It then compares each of your payload shapes — typical prompt, completion, judge rationale, multi-turn transcript — against the matched limit, when one exists. For vendors with a stated numeric cap (Langfuse, Groundcover, Lumigo, Braintrust): same order of magnitude as the limit or larger is HIGH; roughly 10x headroom below is MEDIUM (safe today, fragile against growth); comfortably below is LOW. For vendors with a documented structural risk but no stated number (pre-fix Datadog, the Vercel AI SDK case), it ranks your payload shapes relative to each other instead — short fields LOW, moderately sized fields MEDIUM, large concatenated fields like full transcripts HIGH — and says plainly that this is a relative ranking, not a comparison against a vendor-stated cap. For uncatalogued vendors, it won't assign LOW/MEDIUM/HIGH to individual fields at all; it marks them UNCONFIRMED and tells you to check that vendor's own documented limits directly. Separately, it checks your architecture: if eval/experiment spans ride inside the same trace/export path as regular APM spans with no side-channel, that's flagged HIGH risk regardless of size, because that's the exact structural root cause behind every vendor case in the catalog.

Finally it ranks fixes by effort, cheapest first: raise the relevant size config (noting explicitly if your vendor is the kind where that alone doesn't reliably work); move large fields to attachment/blob offload with a reference ID in the span instead of inlining the full text; or, as the highest-effort but only structural fix, route eval-shaped spans through a separate side-channel export path that bypasses the general APM pipeline's limits entirely — the pattern Datadog itself shipped for its own product.

## Output format you'll get back

```
Eval Telemetry Silent-Drop Risk Audit

Stack described: <your vendor/SDK/collector + version>
Matched catalog entry: <vendor name> | UNCATALOGUED — general OTel/APM risk only

Findings:
- <payload shape>: <size given> vs <matched limit or "unconfirmed, vendor-specific">
  Risk: HIGH | MEDIUM | LOW | UNCONFIRMED (missing payload size)
  Why: <one line tying the number or architecture detail to the verdict>

Architecture risk: HIGH | MEDIUM | LOW
Why: <whether eval spans ride inside the general APM pipeline or a separate path>

Recommended next step (ranked by effort, start at the top):
1. <lowest-effort mitigation that applies>
2. <next>
3. <structural fix if warranted>

Caveat: this audit is based on the description provided, not a live probe of the actual pipeline. It can rule out known risk patterns; it cannot certify the data is complete.
```

## Rules this audit follows (so you can sanity-check the output)

- It will never state a specific size limit for a vendor you didn't name, and never borrow one vendor's number for a "similar" vendor — unnamed/uncatalogued vendors get "unconfirmed, vendor-specific," not a guessed number.
- It will never conclude "your eval data is intact." It only rules out known risk patterns from your description; actual certainty requires running a real oversized-payload probe against your live pipeline, which is outside the scope of this prompt.
- If you give a vendor but no payload sizes, it marks those findings UNCONFIRMED rather than inventing a size to force a verdict.
- If your setup matches the "raised the config limit but it still truncates" shape (documented on the Vercel AI SDK), it will not clear that as low risk just because you raised the limit — it flags it for verification regardless.
- It ranks mitigations cheapest-first and won't jump straight to recommending you rebuild your export pipeline if a config change or attachment offload would plausibly cover a MEDIUM-risk finding.

---

## Your setup (fill in and send)

**Vendor/stack**: <e.g. Datadog APM + dd-trace-py 2.x>
**Custom config**: <attribute limits set, exporter type, whether eval spans share a path with APM spans>
**Typical payload sizes**: <prompt length, completion length, judge rationale length, multi-turn transcript length>
