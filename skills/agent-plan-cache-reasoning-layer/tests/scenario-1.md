# Scenario 1 — Support-ticket triage agent, 42 traces, two clear clusters

## Setup

A SaaS company's support-ticket triage agent (built on LangGraph) has been logging execution traces to JSONL for two weeks. The user exports a 42-run sample and pastes it in, asking: "we're considering a plan cache for this agent — is it worth it, and which part?"

## Input (representative sample — the full paste contains 42 such entries; counts below are exact)

```jsonl
{"run_id":"t-001","steps":[{"tool":"classify_category","args":{"category":"enum","confidence":"float"},"tokens_in":820,"tokens_out":140},{"tool":"check_sla_breach","args":{"ticket_age_hours":"int","priority":"enum"},"tokens_in":310,"tokens_out":60},{"tool":"draft_response","args":{"category":"enum","customer_tier":"enum"},"tokens_in":950,"tokens_out":410}]}
{"run_id":"t-002","steps":[{"tool":"classify_category","args":{"category":"enum","confidence":"float"},"tokens_in":790,"tokens_out":135},{"tool":"check_sla_breach","args":{"ticket_age_hours":"int","priority":"enum"},"tokens_in":300,"tokens_out":55},{"tool":"draft_response","args":{"category":"enum","customer_tier":"enum"},"tokens_in":910,"tokens_out":390}]}
{"run_id":"t-003","steps":[{"tool":"classify_category","args":{"category":"enum","confidence":"float"},"tokens_in":805,"tokens_out":142},{"tool":"escalate_to_human","args":{"reason":"enum"},"tokens_in":420,"tokens_out":90}]}
{"run_id":"t-004","steps":[{"tool":"classify_category","args":{"category":"enum","confidence":"float"},"tokens_in":840,"tokens_out":138},{"tool":"check_sla_breach","args":{"ticket_age_hours":"int","priority":"enum"},"tokens_in":295,"tokens_out":58},{"tool":"draft_response","args":{"category":"enum","customer_tier":"enum"},"tokens_in":880,"tokens_out":400}]}
```

- **28 of the 42 runs** follow the exact pattern of t-001/t-002/t-004: `classify_category → check_sla_breach → draft_response`, with argument shapes identical across all 28, token counts varying only mildly (770–950 in / 380–420 out on the draft_response step). This is "Cluster A."
- **9 of the 42 runs** follow t-003's pattern: `classify_category → escalate_to_human`, consistent shapes, token counts within a tight band (400–440 in / 85–95 out on escalate_to_human). This is "Cluster B."
- **5 of the 42 runs** are one-off patterns: one has a 6-step sequence involving a `request_customer_info` loop that repeats a variable number of times per run (2–5 loops), argument shapes shift between runs, token totals range from 1,200 to 4,800. These do not cluster with anything or each other.

## Pass criteria

- Report correctly identifies two dominant clusters (sizes ~28 and ~9) and does not force the 5 one-off runs into either cluster.
- Cluster A is rated structural variance LOW and verdict GOOD CANDIDATE (high frequency: 28/42 ≈ 67%, consistent shape).
- Cluster B is rated LOW-to-MEDIUM variance; verdict GOOD CANDIDATE or MARGINAL is acceptable (9 occurrences clears the 5-occurrence floor), but it must not be rated RISKY given how tight its token band is.
- The 5 one-off/loop runs are flagged as RISKY — DO NOT CACHE YET or excluded as too infrequent/variable, explicitly citing the variable loop count as the reason — they must not be clustered together as if they were one repeatable type.
- Savings for Cluster A are given as a range (not a single number) with the slot-filling assumption stated, and the token-vs-cost caveat (step 7) appears in the report.
- Report does not fabricate any tool name, argument, or token figure not present in the input.

## Fail conditions

- Treating all 42 runs as one undifferentiated cluster, or treating the 5 variable-loop runs as cacheable.
- Giving a single-point savings percentage ("this will cut tokens by 73%") instead of a range with stated assumptions.
- Omitting the token-vs-cost caveat entirely.
