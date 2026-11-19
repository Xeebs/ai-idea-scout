# Scenario 1: Material drift — stale prompt + dropped tool catalog (should flag MATERIAL DRIFT)

## Input the user pastes

**Calibration snapshot** (used 6 weeks ago when the support-escalation judge was validated against 200 human-labeled tickets):

```json
{
  "model": "claude-sonnet-4-20250514",
  "system_prompt": "You are grading whether a support agent's reply correctly escalates a billing dispute. Score 1 if the reply offers a refund, opens a dispute case, OR calls the escalate_to_billing tool when the customer explicitly disputes a charge. Score 0 otherwise. Consider the full conversation, not just the last message.",
  "context_template": "Full conversation transcript + customer account tier + prior ticket count",
  "tool_catalog": [
    {"name": "escalate_to_billing", "params": {"ticket_id": "string", "reason": "string"}},
    {"name": "lookup_refund_policy", "params": {"account_tier": "string"}}
  ],
  "sampling_params": {"temperature": 0, "top_p": 1, "max_tokens": 200},
  "response_format": {"type": "json_object", "schema": {"score": "int", "rationale": "string"}}
}
```

**Runtime snapshot** (pulled from the live judge-invocation code running in production today):

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system="You are grading whether a support agent's reply correctly escalates a billing dispute. Score 1 if the reply offers a refund OR opens a dispute case. Score 0 otherwise.",
    messages=[{"role": "user", "content": transcript_only}],
    temperature=0.3,
    max_tokens=200,
)
# response is parsed with a regex for "Score: (0|1)", no tool catalog is passed to this call
```

## Pass criteria

- [ ] Verdict is **MATERIAL DRIFT** (not MATCH or MINOR DRIFT).
- [ ] Flags `system_prompt` as DIVERGED — notes the runtime prompt drops the `escalate_to_billing` tool-call criterion and the "consider the full conversation" instruction, and judges this as meaning-changing (not cosmetic), clearly labeled as a judgment.
- [ ] Flags `context_template` as DIVERGED/truncation — runtime only passes `transcript_only`, calibration used full transcript + account tier + prior ticket count.
- [ ] Flags `tool_catalog` as DIVERGED — both tools (`escalate_to_billing`, `lookup_refund_policy`) present in calibration, zero tools passed at runtime.
- [ ] Flags `sampling_params.temperature` as DIVERGED — 0 vs 0.3.
- [ ] Flags `response_format` as DIVERGED or UNKNOWN — calibration used structured JSON output, runtime uses an unstructured regex parse (no explicit response_format set).
- [ ] `model_version` is correctly reported as MATCH (both are `claude-sonnet-4-20250514`).
- [ ] Each DIVERGED field has a grounded, qualitative impact line (no invented percentages or score deltas).
- [ ] Recommendation explicitly says to re-run calibration before trusting current scores.
- [ ] Does not claim this check will catch future drift automatically — it's a one-shot audit of these two snapshots.
