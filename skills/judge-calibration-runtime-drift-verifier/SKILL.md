---
name: judge-calibration-runtime-drift-verifier
description: One-shot diff between the LLM-judge config used during calibration (prompt, tool catalog, model, sampling params) and the config the judge actually runs with in production, flagging any divergence before a judge score is trusted. Use when a team wants to sanity-check that their calibrated judge is still the judge that's actually scoring runtime evals.
---

# Calibration Check: Judge Config vs Runtime Config Drift Verifier

## When to use this
A team has an LLM-as-judge evaluation pipeline where the judge was calibrated at some point (validated against human labels, a gold set, or inter-rater agreement) and now wants to verify that the exact call running in production today is still the call that was calibrated — before trusting a release gate, a dashboard trend, or a regression alert built on that judge's scores. Also use when judge scores suddenly shift and the team wants to rule out a silent config mismatch (stale prompt, dropped tool catalog, truncated context, model swap) before assuming the model's actual judgment changed.

This is a one-shot audit, not a monitor. It answers "do these two configs match right now" for whatever two snapshots are pasted in — it does not watch for drift between invocations.

## Inputs
**Data source**: Manual — the user pastes two configs, each as JSON, a code snippet (the actual SDK call), or copied log lines:
1. **Calibration snapshot** — the exact judge invocation used when the judge was calibrated/validated: model name + version, system/instruction prompt (full text), context template or a representative context sample, the tool/function catalog passed to the judge call (names + parameter schemas), and sampling parameters (temperature, top_p, max_tokens, response_format/schema).
2. **Runtime snapshot** — the same fields, taken from the current production judge-invocation code or a live/logged call.

If either snapshot is missing a field (e.g., no tool catalog was ever passed, or sampling params weren't logged), say so explicitly — do not assume a default value on the user's behalf.

## Procedure
1. **Normalize both snapshots** into the same field set: `model_version`, `system_prompt`, `context_template_or_sample`, `tool_catalog`, `sampling_params` (temperature, top_p, max_tokens), `response_format`. If a snippet is raw code, extract these fields from the SDK call arguments; if it's a log line, extract what's present and mark the rest UNKNOWN.
2. **Compare field by field:**
   - `model_version`: exact string match required, including version/date suffixes. Any difference = DIVERGED.
   - `system_prompt`: exact-text diff first. If the text differs at all, show the specific words/lines that changed. Separately flag — as a labeled guess, never stated as fact — whether the change looks cosmetic (whitespace, reordering, typo fix) or looks like it changes meaning (added/removed instructions, changed criteria, changed tone-of-grading language).
   - `context_template_or_sample`: compare structure and approximate length. Flag truncation (one side missing fields, sections, or character ranges the other includes).
   - `tool_catalog`: diff as sets of tool names, then diff parameter schemas per tool that exists on both sides. Report additions, removals, and schema changes separately.
   - `sampling_params` / `response_format`: exact match required on every sub-field; any difference = DIVERGED.
3. **Never guess a MATCH for a field you can't see on both sides.** If one snapshot omits a field entirely, mark that field UNKNOWN, not MATCH and not DIVERGED.
4. **For every DIVERGED field, write one grounded impact line** tied to what actually changed — e.g. "runtime includes 3 tools absent from calibration — judge may score tool-use-related failures differently than what was validated" or "temperature differs (0 vs 0.7) — runtime scores may be less reproducible than the calibration run implied." Do not write an impact line for fields that MATCH, and do not quantify a score-point impact — there is no live score data in this audit, only configs.
5. **Roll up to one overall verdict:**
   - **MATCH** — every field matches exactly.
   - **MINOR DRIFT** — only cosmetic differences (whitespace/formatting/reordering in the prompt, no tool/model/param changes).
   - **MATERIAL DRIFT** — any model change, sampling-param change, tool-catalog change, response-format change, or a system-prompt change judged to alter meaning.
   - **UNKNOWN** — one or more required fields couldn't be compared because a snapshot omitted them; name exactly which fields are missing and from which side.
6. Never default silently to MATCH or "probably fine" when a field is ambiguous — route it to UNKNOWN and say what additional input would resolve it.

## Output format
```
Verdict: MATCH | MINOR DRIFT | MATERIAL DRIFT | UNKNOWN

| Field             | Calibration            | Runtime                 | Status            |
|-------------------|-------------------------|--------------------------|-------------------|
| model_version     | ...                     | ...                      | MATCH/DIVERGED/UNKNOWN |
| system_prompt      | ...                     | ...                      | ...               |
| context_template   | ...                     | ...                      | ...               |
| tool_catalog       | ...                     | ...                      | ...               |
| sampling_params    | ...                     | ...                      | ...               |
| response_format    | ...                     | ...                      | ...               |

Divergence details:
- <field>: <what changed> — Likely impact: <grounded, config-based reasoning only>
...

Recommendation: <one line — e.g. "re-run calibration against the current runtime config before trusting the next eval run" or "no action needed, configs match">
```

## Guardrails
- Never mark a field MATCH without seeing both sides fully — if visibility is partial, the field is UNKNOWN, never a guessed MATCH.
- Never silently treat a reworded system prompt as equivalent to the original; always show the literal diff, and offer the cosmetic-vs-meaning judgment only as a clearly labeled opinion, never as fact.
- Never invent a tool name, parameter schema, model string, or sampling value that wasn't present in the pasted input, even to "fill in" an apparent gap.
- Never assign a quantified score-impact number (e.g., "+/- 5% accuracy") — this skill has no access to live score distributions, only static configs; impact statements must stay qualitative and tied to the specific field that changed.
- Do not conflate this one-shot audit with continuous monitoring — if the user wants drift caught automatically on every future calibration/runtime cycle, say clearly that this skill only checks the two snapshots given right now and point them to a continuous interceptor as a different kind of tool, not something this skill does.
