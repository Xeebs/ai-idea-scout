# Scenario 2: Exact match plus one partially-visible field (should flag MATCH overall, UNKNOWN on one field — not a guessed match)

## Input the user pastes

**Calibration snapshot** (from the eval repo's `calibration/judge_config.yaml`, used when the code-review judge was validated against a 150-item human-graded set last quarter):

```yaml
model: gpt-4.1-2025-04-14
system_prompt: |
  You are an expert code reviewer. Given a diff and its PR description, score
  1 if the diff fully addresses the PR description's stated intent with no
  obvious regressions, else score 0. Be strict about silent behavior changes.
context_template: "diff + PR description + repo CONTRIBUTING.md excerpt"
tool_catalog:
  - name: run_static_analysis
    params: {diff: string}
sampling_params:
  temperature: 0
  top_p: 1
  max_tokens: 150
response_format:
  type: json_object
  schema: {score: int, rationale: string}
```

**Runtime snapshot** (copied from the production CI job's logged request — the team's logging pipeline does not capture sampling parameters, only the request body fields):

```json
{
  "model": "gpt-4.1-2025-04-14",
  "system": "You are an expert code reviewer. Given a diff and its PR description, score 1 if the diff fully addresses the PR description's stated intent with no obvious regressions, else score 0. Be strict about silent behavior changes.",
  "context": "diff + PR description + repo CONTRIBUTING.md excerpt",
  "tools": [
    {"name": "run_static_analysis", "params": {"diff": "string"}}
  ],
  "response_format": {"type": "json_object", "schema": {"score": "int", "rationale": "string"}}
}
```

(The team explicitly notes: "we don't log temperature/top_p/max_tokens anywhere, so I can't paste what runtime actually used for sampling params.")

## Pass criteria

- [ ] `model_version`, `system_prompt`, `context_template`, `tool_catalog`, and `response_format` are all reported as MATCH — text, tool catalog, and schema are identical between the two sides.
- [ ] `sampling_params` is reported as **UNKNOWN**, not MATCH and not DIVERGED — the skill does not assume the missing runtime sampling params equal the calibration ones.
- [ ] The missing-field note explicitly names which field (sampling_params) is unknown and from which side (runtime), and states what additional input (e.g. enabling logging of request params, or pasting the actual SDK call) would resolve it.
- [ ] Overall verdict is **UNKNOWN** (not MATCH) — per the procedure, any required field that can't be compared forces an UNKNOWN verdict rather than a clean pass, even though every visible field matches.
- [ ] No impact line is written for the matching fields (system_prompt, tool_catalog, etc.) — impact lines only appear for genuinely DIVERGED fields, and there are none here.
- [ ] Recommendation reflects the UNKNOWN status (e.g., "confirm runtime sampling params before calling this a full match") rather than declaring the judge fully verified.
- [ ] Does not fabricate a temperature/top_p/max_tokens value for the runtime side under any circumstance.
