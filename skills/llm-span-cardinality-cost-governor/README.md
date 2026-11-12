# LLM Span Cardinality Cost Governor

A paste-into-any-AI-chat prompt that audits your team's LLM/GenAI trace instrumentation (OpenTelemetry or similar) and drafts a cardinality-safe policy — before your observability bill spikes, or before you turn on tracing for the first time.

## When to use this

Use this the moment you notice (or want to avoid) your LLM trace/observability ingestion costs climbing because you're capturing full prompt and completion text on every span. Typical trigger phrases: "our trace bill is climbing since we turned on full prompt capture," "Langfuse/Datadog/Honeycomb costs spiked after we added LLM tracing," or "we're about to instrument our LLM calls with OpenTelemetry and want to avoid the cardinality mistake before we ship it."

This is scoped to **GenAI/LLM span attributes** specifically — things like `gen_ai.prompt`, `gen_ai.completion`, tool-call arguments/results, and similar free-text fields attached to LLM call spans. It is not for generic app-trace cardinality unrelated to LLM calls (HTTP route tagging, database query labels, etc.), and it does not write or implement the actual enforcement code — it produces the policy document a human or a follow-up engineering task then implements.

## What to hand over

Before using the prompt below, gather:

1. **Your current or planned instrumentation.** Describe or paste what gets captured per LLM span today: which attributes, whether prompt/completion text is captured in full, whether it's captured on every span or just the root span of a multi-call chain, and any tool-call or retrieval-context attributes attached. If you haven't instrumented anything yet, say so — the policy will be drafted from OpenTelemetry's standard GenAI semantic-convention defaults instead.
2. **Rough traffic volume.** An order-of-magnitude estimate is fine: "~50k LLM calls/day" or "~2M/month, still ramping."
3. **Error rate, or your definition of a trace that must always be kept.** A current error percentage if you know it, plus anything else that should always be captured regardless of sampling (e.g., traces above a latency or token-cost threshold, anything a human has flagged).

Nice to have: your trace backend/vendor (Langfuse, Datadog, Honeycomb, Superlog, self-hosted, etc.) and its pricing unit if you know it; any retention/incident-replay requirement (e.g., "need to reconstruct incidents up to 30 days back"); a target cost or volume reduction if you already have one in mind.

## The prompt

Copy everything below the line, fill in the bracketed sections with your own details, and paste it into any AI chat tool.

---

You are auditing my team's LLM/GenAI span instrumentation and drafting a cardinality-safe tracing policy. Do not write or assume any enforcement code is already running — this is a design document for us to implement and test, not a live policy.

**My current/planned instrumentation:**
[Describe or paste what you capture per LLM span today — which attributes, whether gen_ai.prompt/gen_ai.completion are captured in full, on every span or root-span-only, and any tool-call or retrieval-context attributes. If nothing is instrumented yet, say "greenfield — nothing set up yet" and note it should use OpenTelemetry's standard GenAI semantic-convention defaults as the starting attribute list.]

**Traffic volume:** [e.g., ~50k calls/day, or "~2M/month, still ramping"]

**Error rate / must-keep definition:** [e.g., "3% error rate" and/or "always keep anything over 5 seconds latency or flagged by a human reviewer"]

**Trace backend (optional):** [e.g., Langfuse, Datadog, Honeycomb, self-hosted — or "not decided yet"]

**Retention/incident-replay requirement (optional):** [e.g., "need to reconstruct incidents up to 30 days back"]

**Target reduction (optional):** [e.g., "want to cut ingestion by half" — or leave blank for a default recommendation]

Using exactly these inputs — never inventing a volume, error rate, or dollar figure I didn't give you or you didn't clearly label as an assumption — produce:

1. **Inputs Received** — restate my traffic volume, error rate, and backend, flagging anything you had to assume.
2. **Attribute Classification Table** (Attribute | Tier | Rationale) — classify every attribute I listed (or the standard GenAI defaults if I said greenfield) into exactly one of three tiers:
   - **Always-safe**: low-cardinality, bounded (model name, finish reason, token counts, latency bucket, status/error code).
   - **Hash-and-truncate**: high-value but unbounded free text (prompt, completion, tool-call args/results) — capped and/or hashed, not dropped.
   - **Excluded-by-default**: low debugging value relative to cost, or PII/compliance-sensitive — call out any PII angle explicitly as a decision I need to confirm, don't decide it for me.
3. **Truncation Plan** (Attribute | Cap/Treatment | Scope | Template-ID alternative) — for every Hash-and-truncate attribute: a specific size cap (default suggestion: ~2KB for prompt/completion combined, root-span only, not duplicated on child spans), and whether a "store a template ID instead of full content" mode is worth offering, with the tradeoff stated plainly (incidents needing exact prompt text won't be reconstructable in that mode). If I gave you a retention or full-replay requirement, do not let the default cap silently override it — propose a named exception path (e.g., a flag tied to a complaint/support-ticket ID that routes that specific trace to full, untruncated capture and longer retention) and say so explicitly. If I gave no such requirement, state plainly that the default cap applies with no exception.
4. **Sampling Policy** — the must-keep rule(s) at 100% capture (errors, plus anything else I named), a proposed sampling rate for everything else (back into it from my target reduction if I gave one, otherwise propose a sensible default like 10-20% of non-error traffic), the volume-reduction arithmetic shown explicitly using my actual error rate and volume, and one plain-language sentence on what debugging capability I lose at that rate (e.g., "roughly 5 out of 6 successful requests will have no stored trace; an incident found after the fact in a non-sampled success case won't be reconstructable").
5. **PII / Compliance Flags** — list, by name, every attribute placed in Excluded-by-default (or any Hash-and-truncate attribute) that carries a PII or compliance angle, as a decision for my team to confirm.
6. **Open Questions** — anything you need from me to firm up the numbers (exact error rate, exact volume, retention requirement, a PII policy decision) rather than guessing further.

Never present this as already enforced — note explicitly that it's a draft to implement and validate against real traffic before relying on it.

---

## What you get back

A single document with six sections in this order: Inputs Received, Attribute Classification Table, Truncation Plan, Sampling Policy (with the reduction math and the debuggability-tradeoff sentence spelled out), PII/Compliance Flags, and Open Questions. Every attribute you listed appears exactly once in the classification table, and no sampling rate is given without the plain-language cost of that rate attached to it.

## What this will not do

- It will not write the OpenTelemetry `SpanProcessor` code or any other enforcement middleware — it hands you the policy to implement, or to hand to an engineer.
- It will not invent a dollar savings figure, a byte-volume number, or a traffic/error number you didn't give it — anything not provided gets flagged as an assumption or added to Open Questions instead.
- It will not drop error traces or any other must-keep category you named, no matter what sampling rate is proposed elsewhere.
- It will not silently decide a PII or compliance question for you — it surfaces it, you decide.
- It does not apply to generic, non-LLM trace cardinality (HTTP routes, DB query tags) — it's scoped to GenAI/LLM span attributes.
