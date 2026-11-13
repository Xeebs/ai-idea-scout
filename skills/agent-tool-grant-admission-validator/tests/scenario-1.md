# Scenario 1 — Missing grant plus a silent policy collision (expect FAIL)

## Setup
A platform engineer is about to merge a PR that updates the `support-triage-agent` Application manifest on an internal `agentgateway`-style platform. Before merging, they paste in the manifest and a grant-records export pulled from the platform's admin API.

### Input 1 — declared manifest (`support-triage-agent.yaml`)
```yaml
agent: support-triage-agent
mcpServers:
  - name: github-mcp
    scope: read
  - name: jira-mcp
    scope: write
  - name: internal-crm-mcp
    scope: read-write
```

### Input 2 — grant records export (`grants-support-triage-agent.json`)
```json
[
  {
    "agent": "support-triage-agent",
    "server": "github-mcp",
    "grantedScope": "read",
    "issuingRule": "R1",
    "specificity": "exact"
  },
  {
    "agent": "support-triage-agent",
    "server": "internal-crm-mcp",
    "grantedScope": "read-write",
    "issuingRule": "R5",
    "specificity": "path-exact:/crm/*"
  },
  {
    "agent": "support-triage-agent",
    "server": "internal-crm-mcp",
    "grantedScope": "deny-write",
    "issuingRule": "R6",
    "specificity": "path-exact:/crm/*"
  },
  {
    "agent": "support-triage-agent",
    "server": "slack-mcp",
    "grantedScope": "read",
    "issuingRule": "R9",
    "specificity": "exact"
  }
]
```

Note: `jira-mcp` has no grant record at all. `internal-crm-mcp` has two rules (R5, R6) with identical specificity (`path-exact:/crm/*`) producing conflicting effective grants (one allows write, one denies it) — this models the real `agentgateway` bug cited in the source idea where the gateway "keeps one at random and silently drops the other while both report Accepted." `slack-mcp` has a grant but is never declared in the manifest.

## Expected output (pass/fail criteria for the evaluator)

The skill's output MUST:
1. State verdict **FAIL** (at least one BLOCKER exists).
2. Include a BLOCKER finding for `jira-mcp` — missing grant (write scope declared, no grant record of any kind).
3. Include a BLOCKER finding for `internal-crm-mcp` — policy collision between rules R5 and R6 (equal specificity, conflicting effective grants on write). The finding must name both rule IDs and describe the conflict, not just flag "something's wrong with crm."
4. Include an INFO finding for `slack-mcp` — granted but never declared (over-granted / least-privilege note) — and this finding must NOT be a BLOCKER and must NOT by itself change the verdict.
5. Confirm `github-mcp` as matched (read declared, read granted via R1) — no finding for it.
6. Include remediation text for both blockers (e.g., "add a grant for jira-mcp:write" and "merge or re-specify rules R5/R6 for internal-crm-mcp so only one applies at matched specificity").
7. NOT return PASS or PASS_WITH_WARNINGS.
8. NOT silently drop the collision to a WARNING severity.

Fails the scenario if: the collision is missed or downgraded, the missing jira-mcp grant is missed, or the over-granted slack-mcp finding is reported as a blocker (over-grant alone must never fail the audit).
