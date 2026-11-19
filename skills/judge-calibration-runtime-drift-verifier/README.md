# Calibration Check: Judge Config vs Runtime Config Drift Verifier

Paste this whole file into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with your two configs, and it will run the audit below.

## What this is for

If you run an LLM-as-judge evaluation pipeline, you probably calibrated your judge once — validated its scores against human labels, a gold set, or inter-rater agreement — and now trust its ongoing scores because of that calibration. But calibration and the runtime judge call are almost always two separate code paths. If someone edits the runtime prompt, drops a tool from the catalog, swaps a model version, or changes a sampling parameter without re-running calibration, the judge that's actually scoring production traffic is no longer the judge that was validated — silently. Nothing checks for this by default.

This is a one-shot audit: paste in the exact config used during calibration and the exact config running in production right now, and get back a field-by-field diff with a verdict. It does **not** continuously monitor anything — it only compares the two snapshots you give it, once.

## What to hand over

You need two things, each as JSON, a code snippet (the actual SDK call), or copied log lines:

1. **Calibration snapshot** — the exact judge invocation used when the judge was calibrated/validated:
   - Model name + version
   - The full system/instruction prompt text
   - The context template or a representative context sample
   - The tool/function catalog passed to the judge call (tool names + parameter schemas)
   - Sampling parameters (temperature, top_p, max_tokens, response_format/schema)

2. **Runtime snapshot** — the same fields, pulled from the current production judge-invocation code or a live/logged call.

If a field is missing from either side (e.g. no tool catalog was ever logged, or sampling params weren't recorded), say so when you paste it in rather than letting the assistant guess a default.

## The procedure the assistant should follow

1. **Normalize** both snapshots into the same field set: model/version, system prompt, context template/sample, tool catalog, sampling parameters, response format. If a snapshot is raw SDK code, pull these fields out of the call arguments; if it's a log line, extract what's present and mark anything absent as UNKNOWN.

2. **Compare field by field:**
   - **Model/version** — exact string match required, including version or date suffixes. Any difference is a divergence.
   - **System prompt** — do an exact-text diff first and show the specific words/lines that changed. Then, as a clearly labeled opinion (never stated as fact), note whether the change looks purely cosmetic (whitespace, reordering, a typo fix) or looks like it changes meaning (added/removed instructions, changed grading criteria, changed tone).
   - **Context template/sample** — compare structure and approximate length; flag truncation if one side includes fields or sections the other doesn't.
   - **Tool catalog** — diff as a set of tool names first, then diff parameter schemas for any tool present on both sides. Report additions, removals, and schema changes as separate findings.
   - **Sampling parameters / response format** — exact match required on every sub-field; any difference is a divergence.

3. **Never guess a match for a field you can't see on both sides.** A field present in only one snapshot is UNKNOWN, not a match and not a divergence.

4. **For every field that diverged, write one grounded impact line** tied to the actual change — for example: "runtime includes 3 tools absent from calibration — the judge may score tool-use-related failures differently than what was validated," or "temperature differs (0 vs 0.7) — runtime scores may be less reproducible than the calibration run suggested." Do not write an impact line for matching fields, and never quantify a score-point or accuracy-percent impact — this audit only has configs, not live score data.

5. **Roll up to one overall verdict:**
   - **MATCH** — every field matches exactly.
   - **MINOR DRIFT** — only cosmetic prompt differences (whitespace/formatting/reordering), nothing else changed.
   - **MATERIAL DRIFT** — any model change, sampling-parameter change, tool-catalog change, response-format change, or a system-prompt change judged to alter meaning.
   - **UNKNOWN** — one or more required fields couldn't be compared because a snapshot omitted them; name exactly which fields and from which side.

## Output format

```
Verdict: MATCH | MINOR DRIFT | MATERIAL DRIFT | UNKNOWN

| Field             | Calibration | Runtime | Status |
|-------------------|-------------|---------|--------|
| model_version     | ...         | ...     | MATCH/DIVERGED/UNKNOWN |
| system_prompt     | ...         | ...     | ...    |
| context_template  | ...         | ...     | ...    |
| tool_catalog       | ...         | ...     | ...    |
| sampling_params    | ...         | ...     | ...    |
| response_format    | ...         | ...     | ...    |

Divergence details:
- <field>: <what changed> — Likely impact: <qualitative, config-grounded reasoning only>
...

Recommendation: <one line, e.g. "re-run calibration against the current runtime config before trusting the next eval run" or "no action needed, configs match">
```

## Rules this must follow

- Never mark a field as matching unless both sides are fully visible — partial visibility means UNKNOWN, not a guessed match.
- Never treat a reworded system prompt as automatically equivalent to the original. Always show the literal diff; offer the cosmetic-vs-meaning judgment only as a clearly labeled opinion.
- Never invent a tool name, parameter schema, model string, or sampling value that wasn't in what was pasted — if something is missing, say it's missing.
- Never attach a quantified score-impact number (like "+/- 5% accuracy") — only qualitative, config-grounded impact statements are allowed.
- This is a single audit of two pasted snapshots, not ongoing monitoring. If drift needs to be caught automatically every time calibration or runtime code changes, that requires a continuously running interceptor wired into the eval pipeline — a different kind of tool than this one-shot check. Say so plainly rather than implying this skill does that.
