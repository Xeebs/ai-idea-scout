# Scenario 2: deepeval judge swap, cross-provider (OpenAI to Anthropic), structured-output and temperature range changes

## Setup

A team runs deepeval in their CI pipeline to score a customer-support agent's responses for policy compliance, using a `GEval` metric whose judge is currently `gpt-4o` with a JSON-schema structured output and a deliberately high temperature to sample judge variance. They want to migrate the judge to `claude-sonnet-4-5-20250929` (a pinned, dated Anthropic snapshot) for cost/quality reasons. This is a harder case than Scenario 1 because it crosses providers entirely, not just model generations within one provider.

## Input handed to the skill

Current judge config (deepeval-style, as pasted by the user — paraphrased from their custom judge wrapper):

```python
judge_config = {
    "provider": "openai",
    "model": "gpt-4o",
    "response_format": {"type": "json_schema", "json_schema": {"name": "verdict", "schema": {...}}},
    "max_tokens": 1024,
    "temperature": 1.5,
}
```

Target judge model: `claude-sonnet-4-5-20250929`

Target model docs: not provided — skill must search live.

## Expected output

- Parameter table includes at minimum:
  - `response_format: json_schema` → should land as `RENAMED` or `INCOMPATIBLE` with a clear note that Anthropic's API does not have an OpenAI-style `response_format`/`json_schema` field, and that structured output on Claude models is typically achieved via tool-use/forced-tool-choice or prompt-based schema instructions instead — action should point at that remapping path, not just say "drop it" with no replacement guidance, since this is load-bearing for the eval actually working.
  - `max_tokens: 1024` → `COMPATIBLE` or `RENAMED` depending on what the tool finds — Anthropic's Messages API also uses `max_tokens`, and additionally requires it (unlike OpenAI where it's often optional), so the tool should at minimum confirm it's still a valid, required field for Claude rather than skipping it.
  - `temperature: 1.5` → `RANGE-CHANGED`: Anthropic's documented temperature range is 0–1, so 1.5 is out of bounds and must be flagged with a suggested clamp (e.g. to 1.0) and an explicit note to the user that this changes judge-variance behavior, not just a mechanical fix.
- Alias risk section: `claude-sonnet-4-5-20250929` is a dated snapshot, so no alias warning needed for the target; `gpt-4o` (bare, no date) should be flagged as an unpinned alias on the current side.
- Corrected config: a Python dict/JSON block reflecting the Anthropic provider, the remapped structured-output approach (even if described in a comment rather than full code, given it requires an architectural change, not just a key rename), `max_tokens` confirmed/kept, and `temperature` clamped to within range.
- Confirm-manually list flags the structured-output remapping as needing human implementation (not a pure mechanical fix) and includes the canary-run reminder.

## Pass / fail criteria

- PASS requires: `temperature: 1.5` correctly flagged `RANGE-CHANGED` against Anthropic's 0–1 bound, with a clamp suggestion — this is the core cross-provider range-mismatch test and failing it is a hard fail.
- PASS requires: `response_format`/`json_schema` is flagged as needing structural remapping (not silently marked compatible, and not just dropped with no guidance on the replacement mechanism).
- PASS requires: alias risk correctly distinguishes the pinned target (`claude-sonnet-4-5-20250929`, no warning needed) from the unpinned current model (`gpt-4o`, warning needed) — this tests that the skill doesn't blanket-flag or blanket-skip alias risk regardless of input.
- PASS requires: the tool does not claim deepeval or Anthropic "natively" supports OpenAI's `response_format` syntax unchanged.
- FAIL if: the tool treats this as a same-provider swap and skips the cross-provider structured-output and temperature-range issues entirely.
- FAIL if: temperature is left at 1.5 in the corrected config with no flag.
