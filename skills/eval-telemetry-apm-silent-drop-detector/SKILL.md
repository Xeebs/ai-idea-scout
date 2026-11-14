---
name: eval-telemetry-apm-silent-drop-detector
description: Audits a team's description of its LLM eval/experiment tracing setup (vendor, SDK/collector version, custom span-processor config) against known per-vendor payload-size limits to flag which attributes (long prompts, judge rationales, multi-turn transcripts) are likely being silently truncated or dropped before scoring. Use when someone asks "is our eval data actually intact?" or is about to trust eval/experiment scores built on top of a general-purpose APM/OTel pipeline they didn't design for LLM payloads.
---

# Eval Telemetry Silent-Drop Risk Audit

## When to use this
Someone has bolted LLM eval/experiment tracing (prompts, completions, judge rationales, multi-turn transcripts) onto a general-purpose APM or OTel pipeline — Datadog, New Relic, Grafana/Tempo, a self-managed OTel Collector, Langfuse, Lumigo, Groundcover, Braintrust, or similar — and either (a) is about to start trusting eval dashboards/judge scores as ground truth, or (b) explicitly asks "could our APM pipeline be silently truncating or dropping our LLM eval data?" This is a one-time, before-you-trust-the-numbers audit, not a runtime fix — it diagnoses risk from a description, it does not instrument anything live.

## Inputs
**Data source**: Manual — the user pastes a description of their current tracing setup: the vendor/SDK/collector name and version, any custom span-processor or exporter configuration they've applied, and a rough sense of how large their typical eval payloads run (prompt length, judge-rationale verbosity, number of turns in multi-turn transcripts). No live access to the pipeline is required or used.

Required for a useful audit:
1. **Vendor/stack** — e.g. "Datadog APM + dd-trace-py 2.x", "generic OTel Collector forwarding to Grafana Tempo", "Langfuse SDK v3", "Vercel AI SDK with OTel exporter".
2. **Any custom config** — span-attribute length limits set, batch processor settings, exporter type (OTLP/gRPC vs HTTP), whether eval spans ride inside the same trace as regular APM spans or go through a separate pipeline.
3. **Typical payload shape** — rough byte/character size of a typical prompt, completion, judge rationale, and whether multi-turn transcripts get concatenated into one span attribute.

If 1 is missing, ask for it before proceeding — a vendor-less audit is a guess, not a diagnosis. If 2 or 3 are missing, proceed but explicitly mark every finding that depends on them as "unconfirmed — need payload size" rather than asserting a verdict.

## Procedure
1. **Identify the vendor/stack** from the input and match it against the known-limit catalog below. If the named vendor/stack isn't in the catalog, say so explicitly and work from general OTel/APM truncation mechanics (span attribute length caps, OTLP message-size caps, batch-processor drop-on-overflow behavior) rather than inventing a specific number for an uncatalogued vendor.

   **Known per-vendor/mechanism limits** (only state these for vendors actually named by the user; never apply one vendor's number to a different vendor):
   - **Langfuse**: ~2MB per ingested event; payloads over this are rejected/dropped, not gracefully truncated.
   - **Groundcover**: ~10KB per span before truncation kicks in.
   - **Lumigo**: ~2KB per field; anything longer than this per attribute gets cut.
   - **Braintrust**: ~10MB OTLP payload cap.
   - **Datadog APM / dd-trace** (pre the dd-trace-py #21690 fix, i.e. any version where eval/experiment spans still ride inside ordinary APM traces rather than using a dedicated LLM Observability export path): eval spans inherit APM's own attribute-size and trace-size limits — no dedicated large-payload path, so long judge rationales or full multi-turn transcripts riding as span attributes are the highest-risk shape.
   - **Vercel AI SDK + generic OTel exporter**: documented case of span attributes getting truncated below the user's own configured `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT`, meaning raising the config limit alone does not reliably fix it — treat any setup matching this shape as still at risk even after a limit increase, and flag it for verification rather than clearing it.
   - **Generic OTel Collector / unnamed OTLP backend**: no universal number — flag as "unconfirmed, vendor-specific" and recommend the user check their specific collector/backend's documented attribute and batch-size limits rather than accepting a generic default as safe.

2. **Map the user's described payload shapes to the limits.** For each of: typical prompt, typical completion, judge rationale, multi-turn transcript:
   - If the matched entry has a **stated numeric limit** (Langfuse, Groundcover, Lumigo, Braintrust): compare the described/estimated size against it. Same order of magnitude as the limit or larger → HIGH. Within roughly 10x headroom below the limit → MEDIUM (safe today, fragile against growth). Comfortably below → LOW.
   - If the matched entry has **no stated numeric limit but a documented structural risk** (Datadog pre-fix, Vercel AI SDK): there is no number to compare against, so rank the payload shapes **relative to each other** instead — a field under ~1,000 characters (e.g. a short user prompt) is LOW; a field in the low-thousands of characters (a judge rationale) carrying real but moderate size on a path with no documented ceiling is MEDIUM; a field in the high-thousands of characters or larger (a concatenated multi-turn transcript) is HIGH, since it is both large and furthest from anything the underlying APM pipeline was designed to carry. State plainly that this ranking is relative, not against a vendor-stated cap.
   - If the matched entry is **UNCATALOGUED**: do not assign LOW/MEDIUM/HIGH to individual payload shapes at all — mark each as UNCONFIRMED and say the vendor's own documented limits need to be checked directly.

3. **Check the architecture, not just the size.** Regardless of payload size, flag HIGH risk if the user's description shows eval/experiment spans riding inside the same trace/export path as regular APM spans (no separate side-channel), since this is the exact root-cause shape documented across every vendor in the catalog — the failure mode is structural, not just a size problem.

4. **Rank mitigations by effort**, from least to most work, and recommend starting at the top of whichever list applies:
   - Raise the relevant config limit (attribute length, OTLP message size) — lowest effort, but note explicitly if the matched vendor (e.g. Vercel AI SDK case) is documented as not reliably fixed by this alone.
   - Move large fields (judge rationale, full transcript) to attachment/blob offload with a reference ID in the span instead of inlining — medium effort, works within the existing pipeline.
   - Route eval/experiment-shaped spans (tagged via `gen_ai.*` or equivalent attributes) through a separate side-channel export path, bypassing the general APM pipeline's limits entirely — highest effort, but the only structural fix, matching the pattern Datadog itself shipped in dd-trace-py PR #21690.

5. **Never assert "your data is intact" as a conclusion** — the audit can only say "no known risk pattern matched the description you gave me," not "your eval data is complete." If the user wants certainty, tell them the only way to get it is to actually run a synthetic oversized-payload probe through their real pipeline and diff sent-vs-received, which this manual audit does not do.

## Output format
```
Eval Telemetry Silent-Drop Risk Audit

Stack described: <vendor/SDK/collector + version, as given>
Matched catalog entry: <vendor name> | UNCATALOGUED — general OTel/APM risk only

Findings:
- <payload shape, e.g. "judge rationale">: <size given/estimated> vs <matched limit or "unconfirmed, vendor-specific">
  Risk: HIGH | MEDIUM | LOW | UNCONFIRMED (missing payload size)
  Why: <one line tying the number or architecture detail to the verdict>

Architecture risk: HIGH | MEDIUM | LOW
Why: <whether eval spans ride inside the general APM pipeline vs. a separate path>

Recommended next step (ranked by effort, start at the top):
1. <lowest-effort mitigation that applies>
2. <next>
3. <structural fix if warranted>

Caveat: this audit is based on the description provided, not a live probe of the actual pipeline. It can rule out known risk patterns; it cannot certify the data is complete.
```

## Guardrails
- Never state a specific byte/KB/MB limit for a vendor the user didn't name, and never apply one vendor's catalogued limit to a different vendor "because they're similar" — say "unconfirmed, vendor-specific" instead.
- Never conclude "your eval data is intact" or any equivalent certainty claim — this is a risk audit from a description, not a measurement; always end with the caveat that only a live synthetic-payload probe can confirm actual loss.
- If the user gives a vendor/stack but no payload-size information, do not guess a payload size to force a verdict — mark those findings UNCONFIRMED and say exactly what's missing.
- If the user's setup matches the Vercel AI SDK / "config limit raised but still truncates" shape, never clear it as LOW risk on the strength of a raised config limit alone — flag it for verification regardless.
- Do not recommend the side-channel/structural fix as the only option when a lower-effort mitigation (raising a limit, attachment offload) would plausibly resolve a MEDIUM-risk finding — rank by effort and let the user choose, don't jump straight to the most invasive fix.
