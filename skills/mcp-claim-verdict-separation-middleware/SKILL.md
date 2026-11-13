---
name: mcp-claim-verdict-separation-middleware
description: Audits a described agent workflow (its tools, what each does, and who currently decides success/failure) for role-collapse — the same agent instance both producing evidence/taking action and issuing the verdict on it — and recommends a CLAIM/VERDICT tagging plus escalation boundary. Use when designing, reviewing, or hardening an agent that both does something and would otherwise self-certify the outcome (incident response, code-review-and-merge bots, self-testing QA agents, compliance checkers), before wiring in any runtime enforcement.
---

# Split Verdict: Claim/Verdict Role-Collapse Auditor

## When to use this
Someone is designing, reviewing, or inheriting an autonomous agent whose tools both perform/investigate an action AND judge whether that action succeeded, is safe, or is resolved — with no structurally separate reviewer. Trigger phrases: "can this agent mark its own work done", "should the same bot that ran the tests also merge the PR", "does our on-call agent need a second opinion before it closes the incident", or simply pasting a tool list/architecture and asking "is this safe to automate end to end?" This is a one-shot design/review task — it does not touch a live agent or intercept any running tool calls.

## Inputs
**Data source**: Manual — the user pastes a description of the agent's tools. The parent idea's full project (a runtime MCP middleware) is Connected — it intercepts the live tool-call stream via MCP's standard interception point. This skill is deliberately narrower: it is the "do this by hand, once, before writing any enforcement code" half of that idea, so it needs no live connection and runs on whatever the user hands over directly:

1. **Tool list** — for each tool the agent can call: its name and what it does. Accepts any of: an MCP tool manifest (JSON), function/tool schemas, docstrings, or plain prose ("fetch_logs pulls the last hour of error logs; mark_incident_resolved closes the PagerDuty incident").
2. **Current outcome convention** — who or what decides the final pass/fail/resolved/merged/approved status today: the same agent, a different agent, a human, or "nobody checks, it just happens."
3. *(Optional)* Any existing approval/escalation step already in place, even informal ("a human skims the Slack summary before close" counts).

If the tool list omits what a tool actually does (name only, e.g. `tool_7`), ask for a one-line description before auditing it — never infer behavior from a name alone.

## Procedure
1. **Classify every tool** into CLAIM-producing (gathers evidence, executes an action, reports a result) or VERDICT-producing (judges success/safety/resolution/pass-fail/approval) based on its described behavior, not its name. Mark anything genuinely ambiguous as UNKNOWN rather than guessing.
2. **Trace call chains**: for each chain that ends in a VERDICT-producing tool call, identify which CLAIM-producing tool calls feed it and which agent/model instance issued each call.
3. **Flag role-collapse**: any chain where the same instance that issued a CLAIM call also issues the VERDICT call on that same claim, with no distinct reviewer (different model instance, different agent, or human) in between.
4. **Rate stakes per flagged chain**: HIGH (verdict gates an irreversible or high-blast-radius action — merge to main, close a production incident, approve a payment, pass a release gate), MEDIUM (reversible but costly to undo), LOW (low-blast-radius, cheaply reversible).
5. **Recommend a fix per flagged chain**: retag the VERDICT tool explicitly in a tagging manifest, and specify the escalation boundary to insert — a second, independently-prompted model instance with no access to the first instance's reasoning trace (acceptable for LOW/MEDIUM stakes), a genuinely different agent/vendor (for MEDIUM/HIGH), or a human-approval queue (required for HIGH stakes — a same-vendor second model call is not independence by itself; say so explicitly when stakes are HIGH).
6. **Note what's already safe**: chains where a distinct reviewer already sits between claim and verdict need no change — say so, don't manufacture a finding to pad the report.
7. **Call out bypass clauses**: any rule that lets the agent skip its own escalation step (e.g. "skip human review for diffs the bot itself judges low-risk") defeats the separation and must be flagged as its own finding, not folded into the main table.

## Output format
```
## Workflow Audit: <name/description of the agent>

Tools reviewed: <n> | Chains traced: <n> | Role-collapse findings: <n>

### Findings
| Claim tool(s) | Verdict tool | Same instance? | Stakes | Recommended fix |
|---|---|---|---|---|
| fetch_logs, run_diagnostic | mark_incident_resolved | Yes | HIGH | Retag mark_incident_resolved as VERDICT; require human-approval queue before close |

### Already separated (no change needed)
- <tool/chain> — <why it's already safe>

### Bypass clauses found
- <rule/condition> — <why it defeats separation>

### Unknown / needs more detail
- <tool name> — <what's missing>

### Tagging manifest recommendation
tool: fetch_logs       role: CLAIM
tool: mark_incident_resolved  role: VERDICT  escalation: human-approval-queue
```
If no role-collapse exists anywhere in the described workflow, say so plainly as the headline, with the chain(s) checked — a clean audit is a valid, useful result, not a failure to find something.

## Guardrails
- Never infer a tool's behavior from its name alone; an unlabeled or vaguely-described tool is UNKNOWN until the user clarifies, not assumed safe or unsafe.
- Never recommend a same-vendor second model instance as sufficient independence for a HIGH-stakes verdict — say explicitly that HIGH stakes need a different agent/vendor or a human, and that "two calls to the same model" is not separation of duties.
- Never treat this audit as proof the workflow is secure — it is advisory design review, not runtime enforcement; end every report by naming that the actual fix requires wiring the escalation boundary into the real tool-call path (manually, or via a generalized enforcement middleware), not just agreeing with this report.
- Never recommend removing or weakening an existing check to "simplify" the workflow — this skill only ever adds separation or confirms what's already sufficient, never reduces verification.
- Never fabricate engagement numbers, tool behavior, or escalation outcomes not present in what the user provided.
