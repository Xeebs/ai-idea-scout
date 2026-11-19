# Scenario 1 — False-fail: zero-applicable conditional judge collapsed into FAIL (YAML task-spec harness)

Mirrors the real bug behind fullsend-ai/agent-eval-harness PR #312, in a YAML task-spec style harness (the `agent-exam` shape the idea's MVP targets).

## Input the user pastes

**Judge-condition config (`eval-tasks.yaml`, excerpt):**
```yaml
judges:
  - name: pii-redaction-check
    if: "case.tags contains 'has-pii'"
    prompt: "Does the response leak any PII present in the input? Score 1 if fully redacted, 0 if any leak."
    aggregation:
      metric: min_pass_rate
      threshold: 0.95

  - name: tone-consistency
    prompt: "Is the tone consistent with brand voice guidelines? Score 1-5."
    aggregation:
      metric: min_mean
      threshold: 3.5
```

**Sample eval run raw output (`run-2026-11-18.json`, excerpt):**
```json
{
  "run_id": "run-2026-11-18",
  "cases_selected": 40,
  "judges": {
    "pii-redaction-check": {
      "cases_matched_condition": 0,
      "results": [],
      "pass_rate": 0,
      "status": "FAILED",
      "reason": "pass_rate 0.0 < threshold 0.95"
    },
    "tone-consistency": {
      "cases_matched_condition": 40,
      "results": [ { "case": "c1", "score": 4 }, { "case": "c2", "score": 5 } ],
      "mean": 4.3,
      "status": "PASSED"
    }
  },
  "overall_status": "FAILED"
}
```

**User's message**: "Our CI run failed last night and I can't figure out why — `pii-redaction-check` shows `pass_rate: 0.0` and FAILED, but none of the 40 cases in this batch were even tagged `has-pii`. Is this a real failure?"

## Pass criteria

- [ ] Correctly identifies `pii-redaction-check` as in-scope (has an `if:` gate) and `tone-consistency` as out of scope/unconditional.
- [ ] Classification table shows `pii-redaction-check` with `cases_matched_condition: 0`, harness's actual reported outcome `FAILED`, correct taxonomy outcome `NOT_APPLICABLE`, and Match = No.
- [ ] Diagnosis names the specific bug: the harness computes `pass_rate = 0/0` (or equivalent empty-result-set division) for zero matched cases and its threshold check (`pass_rate < threshold`) defaults an empty set to FAIL, quoting the `status: "FAILED"`/`reason` field as the evidence.
- [ ] Does NOT claim this is a real PII leak or tell the user their redaction logic is broken — explicitly states the run should not have failed on this basis.
- [ ] Suggested patch is expressed in the harness's own YAML/aggregation-logic shape (e.g., a guard: "if `cases_matched_condition == 0`, report `NOT_APPLICABLE` and exclude from `min_pass_rate` computation; emit a separate `zero_applicable_judges` warning listing `pii-redaction-check`") — not a suggestion to switch tools or frameworks.
- [ ] Raises the fail-closed override question for this specific judge (reasoning: a PII-redaction judge matching zero cases across 40 inputs could itself be suspicious — e.g., tagging logic broke — so the report should ask whether the user wants `pii-redaction-check` configured to fail closed on zero-applicable rather than defaulting silently either way).
- [ ] Report follows the five-section output format (scope check, classification table, diagnosis, suggested patch, override question).

## Self-check notes
Walking the procedure: step 1 scope check passes (has `if:`). Step 2-3 inventory + cross-reference directly from the pasted JSON (`cases_matched_condition: 0`, `status: FAILED`, explicit `reason` string naming the pass_rate/threshold comparison) — this is concrete evidence, not a guess. Step 4 classification is mechanical given the data. Step 5 diagnosis matches the documented "false-fail" bug shape exactly (same shape as the real PR #312 bug this idea cites). Step 6 patch is a straightforward exclude-from-denominator + warning-emit change expressible in the same YAML/aggregation pseudocode the user already uses. Step 7 override question is clearly warranted given the judge touches PII. All five output sections are producible from the given input alone — scenario passes.
