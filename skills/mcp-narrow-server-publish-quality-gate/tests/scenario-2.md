# Scenario 2 — Weather MCP server, manifest pasted directly (no repo access)

## Input

A user pastes this directly into the chat with no repo URL and no permission/scope info:

"Here's my MCP server's tool manifest, can you check it over before I post it on Show HN?"

```json
{
  "tools": [
    {
      "name": "get_current_weather",
      "description": "Gets weather data.",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": { "type": "string" },
          "alert_radius": { "type": "number" }
        },
        "required": ["location"]
      }
    },
    {
      "name": "get_forecast",
      "description": "Gets weather data for the future.",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": { "type": "string" },
          "days": { "type": "number" }
        },
        "required": ["location"]
      }
    },
    {
      "name": "get_historical_weather",
      "description": "Gets past weather.",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": { "type": "string" },
          "start_date": { "type": "string" },
          "end_date": { "type": "string" },
          "temp_unit": { "type": "string" }
        },
        "required": ["location", "start_date", "end_date"]
      }
    }
  ]
}
```

No README, no permissions info, no source code given — manifest only.

## Expected output characteristics (pass/fail criteria)

A passing run must:

1. **List all 3 tools by name** correctly from the pasted JSON.
2. **Flag all three descriptions as WARN (or FAIL)** for description clarity — "Gets weather data.", "Gets weather data for the future.", and "Gets past weather." are all near-restatements of the tool name with no guidance on when to call them or what the response shape looks like.
3. **Flag `get_current_weather`'s `alert_radius` parameter** as a units/ambiguous-values issue (WARN/FAIL) — it's a bare number with no indication of km vs. miles, and no default is shown. Contrast correctly against `get_historical_weather`'s `temp_unit` field, which *is* an explicit, named units parameter and should NOT be flagged for the same issue (checking the model actually differentiates ambiguous-numeric-with-no-unit from a tool that already lets the caller specify the unit, rather than blanket-flagging all three tools identically). `get_forecast`'s `days` parameter is a count, not a unit-ambiguous value, and should not be flagged under this category either.
4. **Must explicitly state that the permission-scope-creep check (step 3) was skipped** because no permission/scope info was provided — this is the core test of the "never guess, say what you couldn't check" guardrail. Fails the scenario if it either silently omits this check with no mention, or fabricates a permission finding with no scope data to back it.
5. **Must NOT flag any tool for missing destructive-action safeguards** — none of the three tools delete, send, or mutate state; a run that fabricates a "destructive action" finding here fails the scenario.
6. **Must NOT flag pagination** on any of these three tools — none return an open-ended list (they return weather data for one location/date range), so a run that demands a pagination param here is misapplying the checklist and fails the scenario.
7. **`get_historical_weather`'s unbounded `start_date`/`end_date` range** (no min/max bound mentioned) is a reasonable WARN under input schema typing/validation, though not required for a pass — acceptable either way as long as it isn't the only finding reported.
8. **Overall verdict should be WARN** (no destructive/pagination FAILs present, but 3+ description-clarity WARNs clears the WARN threshold from the rubric). A run returning a bare PASS despite three vague descriptions fails the scenario; a run returning FAIL with no FAIL-level finding to justify it also fails.
9. Output must include the "Not covered by this review" disclaimer.

Fails the scenario if: it treats the missing scope info as an automatic FAIL (fabricating a scope-mismatch finding from nothing), misapplies pagination/destructive-action checks to tools that don't warrant them, flags `get_forecast`'s `days` count as a unit-ambiguity issue, or fails to differentiate `get_historical_weather`'s explicit `temp_unit` field from `get_current_weather`'s unitless `alert_radius`.
