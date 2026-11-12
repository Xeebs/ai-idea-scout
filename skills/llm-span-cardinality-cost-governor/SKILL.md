---
name: llm-span-cardinality-cost-governor
description: Audits a team's existing (or planned) OTel GenAI span instrumentation and drafts a cardinality-safe policy — attribute truncation plan, tail-sampling rate with the debuggability tradeoff spelled out, and a three-tier attribute classification table. Use when a team's LLM trace/observability bill is climbing from full prompt/completion capture, or before they turn on GenAI tracing for the first time.
---

# LLM Span Cardinality Cost Governor

## When to use this

Reach for this skill the moment someone says something like "our trace bill is climbing since we turned on full prompt capture," "Langfuse/Datadog/Honeycomb ingestion costs spiked after we added LLM tracing," or "we're about to instrument our LLM calls with OpenTelemetry and want to avoid the cardinality/cost mistake before we ship it." It applies specifically to **GenAI/LLM span attributes** (`gen_ai.prompt`, `gen_ai.completion`, tool-call args/results, free-text metadata) — not generic app traces with no LLM calls in them.

Do not use this for: implementing the actual OTel `SpanProcessor` code that enforces the policy (this skill produces a design document a human or a separate build step then implements, not working middleware); auditing non-LLM span cardinality (e.g., HTTP route cardinality, database query tagging) with no GenAI attributes involved; or picking a tracing vendor — this skill is vendor-agnostic and assumes whatever backend the team already has or is evaluating.

## Inputs

Required:
1. **Current or planned instrumentation** — a description or pasted config/code of what gets captured per LLM span today (or what they're planning to capture): which attributes, whether `gen_ai.prompt`/`gen_ai.completion` are captured in full, on every span or just the root span, any existing truncation, and any tool-call or retrieval-context attributes attached to spans. If nothing exists yet (greenfield setup), say so explicitly — the skill still produces a policy, built from the OTel GenAI semantic-convention defaults.
2. **Rough traffic volume** — calls per day or month (an order-of-magnitude estimate is fine, e.g., "~50k/day" or "~2M/month, still ramping").
3. **Error rate or definition of a "must-keep" trace** — the current error rate (%) if known, and/or any other trigger that makes a trace worth keeping at 100% regardless of sampling (e.g., latency above a threshold, cost above a token-count threshold, any trace flagged by a human reviewer).

Optional but useful:
- Trace backend/vendor in use or being evaluated (Langfuse, Datadog, Honeycomb, Superlog, self-hosted collector, etc.) and its pricing unit if known (per-span, per-byte, per-trace).
- Retention/debugging requirements (e.g., "we need to replay incidents up to 30 days back").
- A target volume or cost reduction if the team has one in mind (e.g., "we want to cut ingestion by half").

If traffic volume or error rate is missing, proceed but state the number as an assumption in the output and flag it as needing the team's own figure before the policy is finalized — never invent a specific volume, error rate, or dollar figure that wasn't given or clearly labeled as an assumption.

## Procedure

1. **Inventory the attributes.** List every span attribute currently captured (or, for greenfield setups, every attribute the OTel GenAI semantic conventions would capture by default: `gen_ai.prompt`, `gen_ai.completion`, `gen_ai.request.model`, `gen_ai.usage.*` tokens, tool-call name/arguments/result, any custom metadata mentioned). Flag which ones are unbounded free text (prompt, completion, tool-call arguments/results, any user-supplied string) versus bounded/enumerable (model name, status code, token counts, boolean flags).

2. **Classify every attribute into exactly one tier**:
   - **Always-safe** — low-cardinality, bounded values that cost almost nothing to keep everywhere (model name, finish reason, token counts, latency bucket, boolean flags, status/error code).
   - **Hash-and-truncate** — content with real debugging value but unbounded size (prompt, completion, tool-call arguments/results). Gets capped and/or hashed rather than dropped.
   - **Excluded-by-default** — attributes that add little debugging value relative to their cost, or carry PII/compliance risk the team must consciously opt back into (full retrieved-context dumps duplicated on every child span, verbose stack traces repeated per span, raw user identifiers in free-text fields). Name the PII/compliance risk explicitly for any attribute placed here — never silently exclude or silently include a PII-bearing field; call it out as a decision the team must confirm.

3. **Draft the truncation plan** for every Hash-and-truncate attribute: a specific cap (default heuristic, stated as a default and adjustable: ~2KB for `gen_ai.prompt`/`gen_ai.completion` combined, captured on the root span only — not duplicated on every child span in a multi-call chain), and whether a "template ID, not full content" mode is offered as an alternative for teams willing to trade raw-prompt debugging for near-zero cardinality cost. State the tradeoff of template-ID mode plainly: incidents needing the exact prompt text will not be reconstructable from the trace alone. **If the team named any retention or full-replay requirement** (e.g., "need to reconstruct complaint conversations for 30 days"), the truncation plan must explicitly reconcile it — never let the default cap silently override a stated replay need. Propose a named exception path (e.g., a flag/tag that routes a specific trace to full, untruncated capture and longer retention — triggered by a human flag, a complaint ID, or a support-ticket link) and say so in the plan; if no such requirement was given, state plainly that the default cap applies with no exception.

4. **Draft the tail-sampling rate.** Carve out 100% capture for: all error traces, and any other must-keep category named in the inputs (cost/latency threshold, human-flagged). For everything else, propose a sampling rate. If the team gave a target reduction, back into the rate; if not, propose a default starting point (e.g., 10-20% of non-error traffic) and show the arithmetic using their stated error rate and volume: e.g., "at a 3% error rate, 100% error capture + 15% sampling of the remaining 97% keeps ~3% + 14.55% ≈ 17.5% of total traces, a ~82% volume reduction." Never compute this arithmetic without the team's own error rate and volume — if either is an assumption, label it as an assumption in the output, not a measured figure.

5. **Spell out the debuggability tradeoff** in plain language tied to the actual sampling rate chosen: how many non-error requests out of N will have no full trace available, and what that means in practice (e.g., "roughly 5 out of 6 successful requests will have no stored trace; an incident discovered after the fact in a non-error, non-sampled request will not be reconstructable from this backend alone"). Never present a sampling rate without this sentence.

6. **Assemble the three-tier classification table** applied to the team's *actual* attributes from step 1 — not a generic template. Every attribute named in step 1 must appear exactly once in this table.

7. **List open questions.** Anything needed to firm up the numbers (exact error rate, exact volume, retention requirement, PII policy decision on any Excluded-by-default attribute) that wasn't provided — ask for it rather than guessing further.

## Output format

A single markdown document, in this order:

1. **Inputs Received** — restate traffic volume, error rate, and backend as given or flagged as assumed.
2. **Attribute Classification Table** — columns: Attribute | Tier | Rationale. One row per attribute found in step 1.
3. **Truncation Plan** — columns: Attribute | Cap/Treatment | Scope (root-span-only vs. all spans) | Template-ID alternative (yes/no + tradeoff). One row per Hash-and-truncate attribute. If a retention/full-replay requirement was given, add the named exception path here (or state explicitly that none applies).
4. **Sampling Policy** — the must-keep rule(s), the proposed rate for everything else, the volume-reduction arithmetic from step 4, and the debuggability-tradeoff sentence from step 5.
5. **PII / Compliance Flags** — any Excluded-by-default attribute with a PII/compliance angle, named explicitly as a decision for the team to confirm, not a decision this skill makes for them.
6. **Open Questions** — anything needed to firm up the draft, from step 7.

## Guardrails

- Never fabricate a specific dollar savings figure, byte-volume number, or percentage without it being computable from the user's own stated (or clearly labeled assumed) volume and error rate — show the formula, not an invented number.
- Never recommend sampling that drops error traces, or any other must-keep category the team named — those always stay at 100%.
- Never silently include or silently exclude a PII-bearing or compliance-sensitive attribute — always surface it as a named decision in the PII/Compliance Flags section.
- Never skip the debuggability-tradeoff sentence when proposing a sampling rate — a rate with no stated cost is an incomplete recommendation.
- Never produce this policy as if it were already enforced — this is a draft design document for a human (or a separate build step) to implement and test against real traffic before relying on it; say so explicitly in the output.
- If the described spans contain no GenAI/LLM attributes at all, say this skill doesn't apply rather than forcing a generic cardinality audit onto unrelated traces.
