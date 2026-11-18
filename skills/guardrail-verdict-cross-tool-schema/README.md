# Guardrail Verdict Cross-Tool Schema Mapper

A paste-and-run prompt for anyone running AI guardrail checks (jailbreak filters, PII detectors, toxicity classifiers, topic restrictions, etc.) across more than one tool or backend — for example NeMo Guardrails on the way in, a custom check on the way out, and Langfuse or Arize for trace storage. It answers one specific question: **if you pasted your current guardrail-verdict output into a shared schema, how much detail would survive — and how much are you already losing?**

This is a one-time diagnostic, not a running integration. It does not build or operate anything; it reads one sample you paste and tells you exactly what's there and what isn't.

## When to use this

Use it when you're running guardrail checks on more than one backend and you've hit any of these:
- You can't tell, after the fact, which specific check blocked an interaction, with what confidence, without manually digging through each tool's own export format.
- You're about to wire up a cross-tool integration (e.g. feeding NeMo Guardrails verdicts into Langfuse or Arize) and want to know what you'll actually gain before building it.
- You want to compare false-positive rates or verdict accuracy between two different guardrail backends, but your two tools don't capture the same fields.

## What to hand over

Paste one of the following (or several, one per tool):
1. A **NeMo Guardrails** exported span or config — e.g. the OTel-exported JSON for a `rail.name`/`rail.type`/`action.result` span, or the relevant `rails:` block from your config plus a captured result.
2. A **Langfuse** score export — the JSON object with `name`, `value`, `dataType`, `traceId`, and any `comment`.
3. An **Arize / OpenInference** guardrail span — a span with `openinference.span.kind: GUARDRAIL` and its attributes.
4. A **raw/custom log line** — whatever your own guardrail check actually logs today, even a single unstructured line.

You don't need to label which tool it's from — the procedure below identifies it from its shape. If you're comparing two tools, paste a sample from each; they'll be mapped separately.

## What this does with it (the procedure)

1. **Identifies the source format** by shape: NeMo Guardrails spans carry `rail.name`/`rail.type`/`action.result`-style attributes and usually express the verdict as a boolean-ish result rather than a 4-way enum. Langfuse expresses a verdict as a `score` attached to a trace. Arize/OpenInference marks a span's kind as `GUARDRAIL`. Anything else is treated as a custom/raw format where every field name is yours, not a standard's. If multiple samples are pasted, each gets its own pass through steps 2–4 below — they are never merged into one table, because merging would hide exactly the kind of incompatibility this check exists to surface.

2. **Extracts only what's actually in the sample.** No field is assumed to exist because the tool "probably" supports it — if it's not in what you pasted, it's marked missing, not guessed at.

3. **Maps the sample against a 9-field canonical "verdict event" schema** that captures what any team reconstructing an incident actually needs:

   | # | Field | What it means |
   |---|---|---|
   | 1 | `check_name` | Which specific check/rail fired |
   | 2 | `verdict` | Normalized to: allow / block / escalate / warn |
   | 3 | `trace_or_span_reference` | A real trace/span ID linking the verdict to the protected interaction (not just a request ID or a timestamp) |
   | 4 | `category` | What kind of risk it targets (jailbreak, PII, toxicity, topic restriction, hallucination, etc.) |
   | 5 | `confidence` | A numeric score, not just pass/fail |
   | 6 | `policy_version` | Which version of the check's config/prompt produced this verdict |
   | 7 | `latency_ms` | How long the check took |
   | 8 | `stage` | pre-inference / post-inference / both |
   | 9 | `reason_code` | A human-readable or coded explanation beyond the bare verdict |

   Each field gets one of three statuses:
   - **Present** — it's there, as-is.
   - **Partial** — something related is there but loses fidelity to get there (a boolean that collapses escalate/warn into block; a request ID standing in for a real trace ID; a latency you'd have to derive by subtracting two timestamps; a check name doing double duty as the category because there's no separate field).
   - **Missing** — nothing corresponds to it.

4. **Redacts anything sensitive** before showing it back to you — API keys, tokens, or full end-user message content get replaced with `[REDACTED]` in the output rather than echoed verbatim.

5. **Explains what you'd gain** — a few sentences, specific to your sample's actual gaps, about what becomes possible once those gaps close (e.g. comparing two backends' false-positive rates on equal footing instead of only knowing both "fired").

6. **Ranks your top 3 gaps** by how much diagnostic value closing them would unlock, each with a concrete, tool-specific suggestion — e.g. "NeMo's self-check rails only emit a Yes/No judgment from the base LLM; to get a real confidence number you'd need a scoring-classifier rail instead of a self-check rail" or "Langfuse's `comment` field is free text — park your reason code there until a dedicated field exists."

## Output you should expect

For each sample pasted, a block like:

```
## Detected source: <tool name or "custom/raw log">

### Field mapping
| Canonical field | Status | Found as | Note |
|---|---|---|---|
| check_name | Present | ... | ... |
| verdict | Partial | ... | collapses escalate/warn into block |
| trace_or_span_reference | ... | ... | ... |
| category | ... | ... | ... |
| confidence | ... | ... | ... |
| policy_version | ... | ... | ... |
| latency_ms | ... | ... | ... |
| stage | ... | ... | ... |
| reason_code | ... | ... | ... |

Coverage: X/9 Present, Y/9 Partial, Z/9 Missing

### What you'd gain
<grounded in your actual gaps>

### Top gaps to close first
1. ...
2. ...
3. ...
```

## Rules this follows

- Never invents a value that isn't in what you pasted — an absent field is always reported Missing, never guessed at as Present.
- Never merges two tools' samples into one table.
- Never echoes secrets or raw user content back to you — it redacts them.
- Never claims this is a finished adapter or a full audit of a vendor's API — it's a read of exactly the one sample you gave it.
- Never tells you to "go build the full cross-tool adapter" as the fix for a gap — that's a separate, ongoing engineering project, not something a one-shot prompt can hand you.
- If what you pasted looks cut off or incomplete, it says so instead of inventing the missing structure.

## How to use this with any AI chat tool

Paste this entire README into the chat along with your sample(s) under a line like "Here's my guardrail verdict output:", and ask it to run the mapping. No Claude Code installation or repo access is required — this file is the whole prompt.
