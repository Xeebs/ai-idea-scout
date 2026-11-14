# Scenario 1 — promptfoo config with a swallowed exception, genuinely dark run

## Input

**Config (`promptfooconfig.yaml`):**
```yaml
description: "Production support-ticket triage eval"
providers:
  - openai:gpt-4.1-mini
prompts:
  - "Classify this support ticket's urgency: {{ticket}}"
tests:
  - vars:
      ticket: "My payment failed twice and I was charged both times."
    assert:
      - type: javascript
        value: |
          try {
            const parsed = JSON.parse(output);
            return parsed.urgency === 'high' ? 1 : 0;
          } catch (e) {
            return 0;
          }
  - vars:
      ticket: "How do I change my email address?"
    assert:
      - type: javascript
        value: |
          try {
            const parsed = JSON.parse(output);
            return parsed.urgency === 'low' ? 1 : 0;
          } catch (e) {
            return 0;
          }
  - vars:
      ticket: "The app crashes every time I open the settings page."
    assert:
      - type: javascript
        value: |
          try {
            const parsed = JSON.parse(output);
            return parsed.urgency === 'high' ? 1 : 0;
          } catch (e) {
            return 0;
          }
```

**Last 2 run outputs (JSON, trimmed to the relevant fields):**

Run 1 (2026-10-28T02:00:00Z):
```json
{
  "results": [
    {"testIdx": 0, "score": 0, "success": false},
    {"testIdx": 1, "score": 0, "success": false},
    {"testIdx": 2, "score": 0, "success": false}
  ]
}
```

Run 2 (2026-10-29T02:00:00Z):
```json
{
  "results": [
    {"testIdx": 0, "score": 0, "success": false},
    {"testIdx": 1, "score": 0, "success": false},
    {"testIdx": 2, "score": 0, "success": false}
  ]
}
```

**Schedule:** GitHub Actions cron `0 2 * * *` (daily at 02:00 UTC). Most recent provided run timestamp: 2026-10-29T02:00:00Z, audit being run 2026-11-14 (user mentions no runs since then — provider started returning a response format change and the pipeline has been silently scoring everyone 0 for ~2 weeks).

## Pass criteria

- Correctly identifies promptfoo from the `providers:`/`tests:`/`assert:` shape.
- Flags the `javascript` assertions' `catch (e) { return 0; }` pattern as a silent-null risk (config-pattern finding) — this is the root cause: a JSON-parse failure (e.g. the provider now wrapping output in markdown fences or prose) is indistinguishable from a genuine "urgency didn't match" failure.
- Flags Signature 2 (constant-score collapse) with appropriate caution: only 3 samples per run, below the ~10-sample threshold — should note "reduced confidence, not a clean collapse finding" rather than declaring it a confirmed High-severity collapse. This is an important nuance: a smaller/correctly-humble model should still catch the config-pattern finding (which doesn't need 10 samples) as the primary High finding, even if it declines to also call the 3-sample collapse itself a confirmed Signature 2.
- Explicitly distinguishes "legitimately scored 0 because the model got urgency wrong" from "the assertion's try/catch returned 0 because parsing failed" — and states it cannot fully tell which from the score alone, pointing back to the config pattern as the likely explanation given both runs show all-zero.
- Gives a concrete fix: e.g. "log or return a distinguishable error value (e.g. -1 or a `parse_error: true` field) from the catch block instead of 0, so a parse failure is never indistinguishable from a real urgency mismatch."
- Does not flag the schedule as stopped (it fired on time both provided runs) — correctly says "not enough data to flag Signature 3" or confirms it looks on-cadence based on what was given, without inventing claims about gaps after 2026-10-29 that weren't in the pasted run data.

## Fail criteria

- Misidentifies the framework.
- Declares a confirmed, high-confidence "score collapse" finding off only 3 samples without flagging the small sample size.
- Fails to notice or quote the `catch (e) { return 0; }` pattern at all.
- Invents a specific "pipeline has been dark for 2 weeks" claim as if it were demonstrated by the pasted run data, rather than attributing that detail to what the user said in prose.
- Recommends buying/installing a third-party product as the fix instead of a specific code change.
