---
name: agent-tool-grant-admission-validator
description: Cross-checks an agent application's declared tool/MCP-server manifest against the platform's actual grant records, before a deploy or PR merge, to catch missing grants and silent policy collisions that would otherwise surface as a runtime 403 or an unenforced rule. Use when a platform team hands over an agent manifest and grant export and asks "will this deploy cleanly" or "did we actually grant what this agent declares it needs."
---

# Grant Gate: Admission-Time Validation for Agent Tool/MCP Permission Declarations

## When to use this
Use this when someone is about to deploy or merge a change to an agent application's tool/MCP-server declarations (e.g., a Kubernetes-style Application manifest, an `agentgateway`/MCP-gateway config, or an internal agent-platform spec) and wants a pre-deploy audit of whether every capability the agent *declares* it will use actually has a matching *grant* on the platform — before finding out at runtime via a 403, or worse, via a policy collision that silently drops enforcement. This is a one-shot manual audit; it does not replace a CI-integrated admission gate, it tells you what one would catch.

## Inputs
**Data source**: Manual — the user pastes or uploads (1) the agent's declared tool/MCP manifest (YAML or JSON: every `mcpServers`/tool entry plus the scope or permission it claims to need) and (2) an export of the platform's actual grant records for that agent's identity (YAML/JSON/CSV: every grant actually issued, including which policy/rule issued it and that rule's specificity/scope). No specific named connector is assumed mature across platforms (agentgateway, AWS open-agentic-platform, Bifrost, and internal systems all expose grants differently) — this skill works from whatever export the user already has.

Optional third input: the raw policy/rule set (if the platform expresses grants as rules rather than flat records) so collisions between two rules of equal specificity can be detected instead of just inferred from the flattened grant list.

If either required input (manifest or grant records) is missing, ask for it explicitly. Do not proceed by assuming an un-provided grant export means "no grants" or "all grants" — say the cross-check cannot run.

## Procedure
1. **Parse the manifest.** Extract every declared capability as a tuple: `(tool/mcp-server identifier, required scope/permission, agent identity it belongs to)`. Note any entry that's ambiguous (e.g., a server declared with no explicit scope — treat the scope as "unspecified, assume broadest").
2. **Parse the grant records.** Extract every granted capability as the same tuple shape: `(tool/mcp-server identifier, granted scope/permission, issuing rule or policy, that rule's specificity)`. "Specificity" means how narrowly the rule targets the resource (e.g., an exact server+path match is more specific than a wildcard).
3. **Match each declared capability against grants:**
   - No grant exists for that identifier at all → **BLOCKER: MISSING_GRANT**.
   - A grant exists but its scope is narrower than what's declared as required → **BLOCKER: SCOPE_SHORTFALL**.
   - A grant exists and covers the declared need → matched, no finding.
   - The tool/server identifier in the manifest doesn't exactly match any grant identifier but looks like it might be an alias (e.g., `github-mcp` vs `github_mcp_prod`) → **WARNING: NAME_MISMATCH_UNCERTAIN** — flag for human confirmation, never silently treat as matched or as missing.
4. **Detect policy collisions** (only possible if the policy/rule set input was provided, or if the grant export itself shows multiple rules issuing grants for the same resource): for any tool/server where two or more rules have equal specificity but would produce different effective grants (different scope, or one allow/one deny), flag **BLOCKER: COLLISION** — this models the known failure mode where the enforcement layer "keeps one at random and silently drops the other while both report Accepted." Do not downgrade this to a warning; a silent collision is the worst-case failure this skill exists to catch. If no optional policy/rule-set input was given and the flat grant export shows no duplicate-specificity entries for any resource either, state explicitly in the report that collision detection was limited to what the flat grant list shows — never silently skip this disclosure, and never fabricate a collision that the available data doesn't support.
5. **Flag unused grants (informational only):** a grant exists for a capability the manifest never declares. Report as **INFO: OVER_GRANTED** — this is a least-privilege hygiene note, never a blocker, and never withhold a PASS verdict because of it alone.
6. **Compute the verdict:** `FAIL` if any BLOCKER exists, `PASS_WITH_WARNINGS` if only WARNING/INFO findings exist, `PASS` if no findings at all. Never report `PASS` if the grant-records input was missing or empty — report `INCOMPLETE` instead and say why.
7. **Write remediation for every BLOCKER and WARNING** — the specific grant to add, the specific rule collision to resolve (e.g., "merge these two rules" or "assign distinct specificity"), or the specific identifier to confirm.

## Output format
A markdown report with, in order:
1. **Verdict** line: `FAIL`, `PASS_WITH_WARNINGS`, `PASS`, or `INCOMPLETE` (with reason if incomplete).
2. **Findings table**: columns `ID | Severity (BLOCKER/WARNING/INFO) | Tool/MCP Server | Issue | Remediation`. One row per finding, grouped BLOCKER first.
3. **Summary counts**: number of declared capabilities checked, number matched, number of each severity.
4. **What this does not cover**: one line reminding the reader this is a one-shot manual check, not the always-on CI/admission gate — recurring deploys need the automated version of this same cross-check wired into CI.

## Guardrails
- Never invent a grant, a manifest entry, or a policy rule that wasn't in the provided input — if an input is incomplete or truncated, say so rather than filling gaps with assumptions.
- Never return `PASS` when the grant-records input is missing, empty, or clearly partial — return `INCOMPLETE`.
- Never silently resolve a `NAME_MISMATCH_UNCERTAIN` finding in either direction (treating it as matched or as missing) — it always needs a human confirmation, flagged as such.
- Never downgrade a detected policy collision to a warning — it is always a BLOCKER, because the entire point of this skill is that collisions fail silently in production otherwise.
- Never claim this one-shot check is equivalent to, or a substitute for, a CI-integrated admission gate that runs on every deploy — say explicitly that it is a point-in-time audit.
- Never match tool/server identifiers fuzzily without flagging the fuzziness — exact-string matches are findings, near-matches are always `NAME_MISMATCH_UNCERTAIN`, never auto-resolved.
