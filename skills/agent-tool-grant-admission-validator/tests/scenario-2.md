# Scenario 2 — Clean match with a name-alias ambiguity and an unused grant (expect PASS_WITH_WARNINGS)

## Setup
A different team is auditing the `billing-reconciliation-agent` before its first deploy on a platform where grants are exported flat (no separate policy/rule set was provided — this is realistic, since not every platform exposes that detail). They paste the manifest and the grant export.

### Input 1 — declared manifest (`billing-reconciliation-agent.yaml`)
```yaml
agent: billing-reconciliation-agent
mcpServers:
  - name: stripe-mcp
    scope: read
  - name: netsuite-mcp
    scope: read
  - name: github_mcp_prod
    scope: read
```

### Input 2 — grant records export (`grants-billing-reconciliation-agent.csv`)
```csv
agent,server,grantedScope,issuingRule,specificity
billing-reconciliation-agent,stripe-mcp,read,R2,exact
billing-reconciliation-agent,netsuite-mcp,read-write,R3,exact
billing-reconciliation-agent,github-mcp,read,R4,exact
billing-reconciliation-agent,slack-mcp,read,R7,exact
```

Notes embedded in the test (not told to the skill): `netsuite-mcp` has a grant broader than declared (read-write granted, only read declared — not a shortfall, so no finding needed there beyond optional over-grant note). `github_mcp_prod` in the manifest doesn't exactly match the grant record's `github-mcp` — this is a plausible aliasing situation (prod suffix), not a guaranteed match. `slack-mcp` has a grant but is never declared. No policy/rule set was provided, so no collision check should be attempted beyond what the flat grant list shows (and there are no duplicate-specificity conflicts in this data regardless).

## Expected output (pass/fail criteria for the evaluator)

The skill's output MUST:
1. State verdict **PASS_WITH_WARNINGS** — no BLOCKER should exist, but at least one WARNING (the name mismatch) must be present, which rules out a plain `PASS`.
2. Confirm `stripe-mcp` as cleanly matched (read declared, read granted via R2).
3. NOT flag `netsuite-mcp` as a blocker — granted scope (read-write) is equal-or-greater than declared (read), so this is a match or at most an informational over-grant note, never a BLOCKER or SCOPE_SHORTFALL.
4. Flag `github_mcp_prod` vs `github-mcp` as a **WARNING: NAME_MISMATCH_UNCERTAIN**, explicitly asking a human to confirm whether these are the same server — must NOT silently resolve it as matched, and must NOT silently resolve it as a missing-grant BLOCKER either.
5. Flag `slack-mcp` as **INFO: OVER_GRANTED** (granted, never declared) — informational only.
6. NOT attempt to report a policy collision for any server, since no duplicate-specificity conflicting rules exist in this flat data and no separate rule set was supplied — the output should not hallucinate a collision that isn't there.
7. Explicitly note that no policy/rule set was provided, so collision detection was limited to what the flat grant list shows (per the SKILL.md procedure's handling of an optional input not being supplied).

Fails the scenario if: the output returns a plain `PASS` (missing the name-mismatch warning), treats the name mismatch as either a silent match or a silent BLOCKER, flags `netsuite-mcp`'s broader grant as a blocker, or fabricates a collision finding that the input data doesn't support.
