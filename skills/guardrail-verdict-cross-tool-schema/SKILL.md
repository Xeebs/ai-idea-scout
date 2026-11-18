---
name: guardrail-verdict-cross-tool-schema
description: One-shot diagnostic that maps a pasted guardrail-verdict sample (NeMo Guardrails span, Langfuse score export, Arize/OpenInference guardrail span, or a raw log line) against a 9-field canonical verdict schema, showing exactly what data a team would gain or is already losing before they build a cross-tool adapter. Use when a team running more than one guardrail enforcement point wants to know how much verdict detail survives today.
---

# Guardrail Verdict Cross-Tool Schema Mapper

## When to use this
Use this when someone running guardrail checks across more than one backend — for example NeMo Guardrails at the pre-inference layer, a custom post-inference check, and Langfuse or Arize for trace storage — asks a version of: "if I wanted to compare or reconcile guardrail verdicts across these tools, what would I actually be able to see?" or "why can't I tell which check blocked this request and with what confidence once it lands in my observability backend?" This is a one-time assessment, not a running integration — it does not build or operate an adapter.

## Inputs
**Data source**: Manual — the user pastes a sample guardrail-verdict log line, config snippet, or exported trace from whichever tool they currently run (e.g. a NeMo Guardrails OTel-exported span, a Langfuse score export, an Arize/OpenInference `GUARDRAIL`-kind span, or a raw application log line). Nothing is fetched automatically; the skill only ever reasons over what is pasted into the conversation.

Required:
1. One sample verdict record (JSON, YAML config + span, or a single log line) from the tool(s) in question. Multiple samples from different tools may be pasted in one turn.
2. Optionally, which backend(s) the team wants to compare against or migrate toward — if omitted, the skill reports against the canonical schema only, not a specific target tool.

## Procedure

1. **Identify the source format** from the sample's shape, matching against known signatures before falling back to "custom/raw":
   - **NeMo Guardrails (OTel GenAI, v0.16+)**: span/attribute names like `rail.name`, `rail.type`, `action.result`, `gen_ai.operation.name` with a `guardrail`-flavored value, or a YAML `rails:` config block. Verdicts typically appear as a boolean-ish result (e.g. `allow`/`refuse`/`bot_refuse`) rather than a 4-way enum.
   - **Langfuse**: a `score` object with `name`, `value`, `dataType`, `traceId`, and optionally `comment` — Langfuse records a guardrail verdict as a score attached to the trace it protected, not as its own event type.
   - **Arize / OpenInference**: a span with `openinference.span.kind` set to `GUARDRAIL` (or a payload shaped for Arize's guardrails-scoring endpoint), carrying attributes under an `openinference.guardrail.*`-style prefix.
   - **Custom/raw**: anything else — a bespoke log line, CSV row, or internal JSON shape with no vendor signature. Treat every field name as the team's own naming, not a standard.
   State the detected format in one line before the mapping table. If two or more samples are pasted, repeat steps 2–4 once per sample — never merge samples from different tools into a single table, since collapsing them would hide the exact incompatibility this skill exists to surface.

2. **Extract every field and value present in the sample verbatim.** Do not infer a value that isn't actually there (e.g. don't assume a confidence score exists because the check "sounds like" a classifier). If a field's meaning is ambiguous (e.g. a bare `result: 1`), note the ambiguity rather than silently picking an interpretation.

3. **Map the sample against this 9-field canonical schema** (`gen_ai.guardrail.verdict` event, per the open schema this skill is scoped against):

   | # | Canonical field | What it captures |
   |---|---|---|
   | 1 | `check_name` | Which specific check/rail fired |
   | 2 | `verdict` | Normalized to one of: `allow` \| `block` \| `escalate` \| `warn` |
   | 3 | `trace_or_span_reference` | A real trace/span ID linking the verdict to the interaction it protected (not just a request ID or timestamp) |
   | 4 | `category` | What kind of risk the check targets (e.g. jailbreak, PII, toxicity, topic-restriction, hallucination) |
   | 5 | `confidence` | A numeric confidence/score for the verdict, not just a pass/fail boolean |
   | 6 | `policy_version` | Which version of the check's policy/config/prompt produced this verdict |
   | 7 | `latency_ms` | How long the check took |
   | 8 | `stage` | `pre-inference` \| `post-inference` \| `both` |
   | 9 | `reason_code` | A human-readable or coded explanation for why the verdict was reached, beyond the bare verdict label |

   For each of the 9 fields, classify the sample as:
   - **Present** — the field (or a value that unambiguously maps to it) exists in the sample as-is.
   - **Partial** — something related exists but needs normalization or loses fidelity to map cleanly (e.g. a boolean `refuse` flag that collapses `escalate`/`warn` into `block`; a `request_id` that isn't a real trace/span ID; a check name reused as the category because no separate category field exists; a latency that must be derived by subtracting `start_time` from `end_time` rather than being given directly).
   - **Missing** — nothing in the sample corresponds to this field at all.

4. **Redact before echoing.** If the pasted sample contains an obvious secret (API key, bearer token) or clearly identifiable end-user content (a full user message, email, name), redact it in the mapping table's "Found As" column (e.g. `confidence=0.93, user_input=[REDACTED]`) rather than reproducing it verbatim.

5. **Write the "what you'd gain" narrative** — 2–4 sentences on what becomes queryable across tools if this sample's gaps were closed (e.g. "with a confidence field you could compare this check's false-positive rate against a different backend's post-inference check on equal footing, instead of only knowing both fired") grounded specifically in which fields are Present vs. Missing for *this* sample, not a generic pitch.

6. **Rank the top 3 gaps** by how much cross-tool diagnostic value closing them would unlock, each with one concrete, tool-specific remediation suggestion (e.g. "NeMo's self-check rails emit a Yes/No judgment from the base LLM — to get a numeric confidence you'd need to swap in a scoring classifier rail rather than a self-check rail" or "Langfuse's score object has a free-form `comment` field — put the check's reason code there until a dedicated field exists"). If fewer than 3 fields are Missing/Partial, rank only the ones that are.

## Output format

```
## Detected source: <NeMo Guardrails OTel span | Langfuse score export | Arize/OpenInference guardrail span | Custom/raw log | mixed — see per-sample tables below>

### Field mapping

| Canonical field | Status | Found as (redacted if needed) | Note |
|---|---|---|---|
| check_name | Present/Partial/Missing | ... | ... |
| verdict | ... | ... | ... |
| trace_or_span_reference | ... | ... | ... |
| category | ... | ... | ... |
| confidence | ... | ... | ... |
| policy_version | ... | ... | ... |
| latency_ms | ... | ... | ... |
| stage | ... | ... | ... |
| reason_code | ... | ... | ... |

**Coverage: X/9 fields Present, Y/9 Partial, Z/9 Missing**

### What you'd gain
<2-4 sentences, grounded in this sample's specific gaps>

### Top gaps to close first
1. <field> — <one-line, tool-specific remediation>
2. <field> — <remediation>
3. <field> — <remediation>
```

Repeat the whole block once per pasted sample if more than one tool's output was provided.

## Guardrails
- Never invent a field value that isn't in the pasted sample — an absent field is always `Missing`, never a guessed `Present`.
- Never merge two different tools' samples into one mapping table — map each separately so the incompatibility stays visible.
- Never echo secrets (API keys, tokens) or raw end-user message content verbatim in the output; redact them.
- Never present this as a completed adapter, a certification of the vendor's full capability, or an audit of their API — it is a one-shot read of the specific sample pasted, nothing more.
- Never recommend "just build the full canonical-schema adapter" as the fix for a gap — that is the companion project (a separate, ongoing piece of infrastructure), not something this one-shot skill produces or scopes.
- If the pasted sample is truncated or clearly missing context needed to classify a field (e.g. a JSON blob cut off mid-object), say so explicitly rather than guessing at the missing structure.
