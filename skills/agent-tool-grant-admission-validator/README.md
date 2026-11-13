# Grant Gate — Admission-Time Validator for Agent Tool/MCP Permission Declarations

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your two input files, and it will run a pre-deploy audit of whether an agent's declared tool/MCP permissions actually have matching grants on your platform — before you find out at runtime via a 403, or worse, via a policy collision that silently drops enforcement while reporting success.

## When to use this

Use this right before deploying or merging a change to an agent application's tool/MCP-server declarations — a Kubernetes-style Application manifest, an `agentgateway`-style config, or any internal agent-platform spec where tool access is expressed as a declared grant rather than hardcoded per-agent. You're asking: "will this deploy cleanly, or does this agent declare something it was never actually granted?"

This is a one-shot manual audit you run yourself, as many times as you like. It is not a CI gate — it tells you what a CI gate would catch, so you can decide whether building one is worth it.

## What you need to provide

**Data source: Manual.** You paste or upload two things:

1. **The agent's declared tool/MCP manifest** — YAML or JSON listing every `mcpServers`/tool entry the agent declares, and the scope or permission it claims to need for each.
2. **The platform's actual grant records export** — YAML, JSON, or CSV showing every grant actually issued to that agent's identity, ideally including which rule/policy issued each grant and how specific that rule is (an exact match vs. a wildcard).

Optional third input: the raw policy/rule set, if your platform expresses grants as rules rather than a flat list — this lets the audit catch collisions between two rules of equal specificity, not just infer them from the flattened grant list.

There's no single standard API this reads from — every gateway (agentgateway, AWS open-agentic-platform, Bifrost, internal systems) exposes grants differently, so just export whatever your platform gives you and paste it in. If you don't have one of the two required inputs, say so — the tool will tell you the audit can't run rather than guessing.

## What it does (the procedure)

1. **Reads the manifest** and extracts every declared capability as: which tool/MCP server, what scope/permission it needs, which agent identity it's for.
2. **Reads the grant records** and extracts every actually-issued grant the same way, plus which rule issued it and how specific that rule is.
3. **Matches each declared capability against the grants**:
   - No matching grant at all → **BLOCKER: missing grant** — this is exactly what would surface as a runtime 403.
   - A grant exists but is narrower than what's declared → **BLOCKER: scope shortfall**.
   - Names look similar but don't match exactly (e.g., `github-mcp` vs `github_mcp_prod`) → **WARNING: uncertain match**, flagged for you to confirm — never silently guessed either way.
4. **Checks for policy collisions** — if two rules of equal specificity would both apply to the same tool/server but produce different effective grants (different scope, or one allows while one denies), that's flagged as a **BLOCKER: collision**. This is the nastiest failure mode: some gateways keep one rule at random and silently drop the other while both report "accepted," so neither you nor the platform sees an error — the agent just randomly has or lacks access depending on which rule won. If you didn't provide the optional rule-set input and the flat grant list itself shows no duplicate-specificity entries, the report will say so explicitly rather than silently skipping the question or inventing a collision that isn't there.
5. **Flags unused grants** as informational only — a grant exists that the manifest never actually uses. This is a least-privilege hygiene note, never something that fails the audit by itself.
6. **Gives a verdict**: `FAIL` if any blocker was found, `PASS_WITH_WARNINGS` if only warnings/info findings exist, `PASS` if everything matched cleanly, or `INCOMPLETE` if one of the required inputs was missing or clearly partial.
7. **Writes a specific remediation for every finding** — which grant to add, which two rules to merge or re-specify, which name to go confirm.

## Output format

You'll get back:

1. A **verdict line**: `FAIL` / `PASS_WITH_WARNINGS` / `PASS` / `INCOMPLETE` (with the reason, if incomplete).
2. A **findings table**: ID, severity (BLOCKER / WARNING / INFO), tool/MCP server name, the issue, and the remediation — blockers listed first.
3. **Summary counts**: how many declared capabilities were checked, how many matched cleanly, and how many of each severity.
4. A one-line reminder that this was a point-in-time manual check, not an always-on gate — if you deploy this agent repeatedly, the same cross-check belongs in CI.

## Rules this tool follows (so you can trust the output)

- It never invents a grant, manifest entry, or policy rule that wasn't in what you gave it. If your input looks truncated or incomplete, it says so instead of filling gaps with assumptions.
- It never returns `PASS` if your grant-records export was missing, empty, or obviously partial — you'll get `INCOMPLETE` instead.
- It never silently decides a fuzzy name match is "probably the same thing" or "probably different" — that's always flagged as uncertain, for you to confirm.
- It never downgrades a detected policy collision to a warning. Collisions are always a blocker, because the entire reason this tool exists is that collisions fail silently in production otherwise.
- It never claims this one-shot audit is the same as having an automated admission gate running on every deploy — it tells you what such a gate would have caught, which is the case for building one if the mismatch rate turns out to be non-trivial.
- It never fuzzy-matches tool/server identifiers without flagging the fuzziness as its own finding.

## Example of what "good" looks like

A clean `PASS` means: every tool/MCP server the manifest declares has an exact-identifier grant of equal or greater scope, with no two rules of equal specificity producing conflicting effective grants for the same resource. Anything less than that gets a finding — the point of this tool is that a mismatch should be loud and specific, not a vague "looks mostly fine."
