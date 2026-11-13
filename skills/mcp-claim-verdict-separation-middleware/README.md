# Split Verdict: Claim/Verdict Role-Collapse Auditor

A self-contained prompt template for auditing whether an autonomous agent is allowed to both do something and grade its own work. Paste the block below into any AI chat tool, fill in your workflow, and run it.

## When to use this

You're designing, reviewing, or inheriting an agent that calls tools to investigate or act on something, and then (via the same model instance) also decides whether that action succeeded, is safe, or is resolved — with nobody structurally different checking it. Common shapes: an on-call/incident-response agent that gathers evidence and then closes its own incident; a code-review bot that runs tests and then merges its own PR; a QA agent that runs a suite and reports its own pass/fail; a compliance-checking agent that gathers facts and issues its own clearance. This is a one-time design review, not a running system — it does not watch your agent live or intercept real tool calls; it works entirely from the description you give it.

## What to hand it

**Data source: Manual.** You paste this directly — nothing is read from a live system:

1. **Your tool list** — every tool the agent can call, and what each one does. Any format works: an MCP tool manifest (JSON), function/tool schemas from your framework, docstrings, or just plain sentences ("`fetch_logs` pulls the last hour of error logs for the affected service"; "`mark_incident_resolved` closes the PagerDuty incident and clears the on-call page").
2. **Who decides the outcome today** — is it the same agent that gathered the evidence, a separate agent, a human, or does nothing currently check it at all?
3. **Optional**: any existing approval or escalation step, even an informal one ("someone skims the Slack summary before closing" counts — mention it).

If you don't know exactly what one of your tools does, describe it as best you can and flag it as uncertain — don't let the reviewer guess from the tool's name.

## The prompt

```
You are auditing my agent workflow for claim/verdict role-collapse: the
risk that the same agent instance both produces evidence/takes an action
(a "claim") and judges whether that action succeeded or is safe/resolved
(a "verdict"), with nobody structurally different checking it.

My tools:
<paste your tool list / manifest / schemas / descriptions here>

Who decides the final outcome today:
<same agent / different agent / human / nobody checks>

Existing approval or escalation steps, if any:
<describe, or write "none">

Do the following:
1. Classify every tool as CLAIM-producing (gathers evidence, acts,
   reports a result) or VERDICT-producing (judges success/safety/
   resolution/pass-fail/approval), based on what it actually does, not
   its name. Mark anything ambiguous as UNKNOWN and ask me instead of
   guessing.
2. Trace which CLAIM tool calls feed into which VERDICT tool calls, and
   whether the same agent/model instance issues both.
3. Flag every chain where the same instance produces the claim AND
   issues the verdict on it, with no distinct reviewer in between.
4. For each flagged chain, rate the stakes: HIGH (gates an irreversible
   or high-blast-radius action — merge to main, close a production
   incident, approve a payment, pass a release gate), MEDIUM (reversible
   but costly to undo), or LOW (cheap to reverse, low blast radius).
5. Recommend a fix per flagged chain: retag the verdict tool explicitly,
   and specify the escalation boundary — a second, independently-
   prompted model instance with no access to the first instance's
   reasoning (okay for LOW/MEDIUM), a genuinely different agent/vendor
   or a human-approval queue (required for HIGH — say explicitly that a
   second call to the same model is NOT sufficient independence for
   HIGH-stakes verdicts).
6. Note any chain that's already properly separated — don't invent a
   finding just to fill the report.
7. Separately call out any rule that lets the agent skip its own
   escalation step (e.g. "skip human review for diffs it judges
   low-risk itself") — this defeats the separation and is its own
   finding.

Output format:

## Workflow Audit: <name>
Tools reviewed: <n> | Chains traced: <n> | Role-collapse findings: <n>

### Findings
| Claim tool(s) | Verdict tool | Same instance? | Stakes | Recommended fix |
|---|---|---|---|---|

### Already separated (no change needed)
- ...

### Bypass clauses found
- ...

### Unknown / needs more detail
- ...

### Tagging manifest recommendation
tool: <name>   role: CLAIM|VERDICT   escalation: <none|second-model|different-agent|human-approval-queue>

If there's no role-collapse anywhere, say so as the headline, listing
the chains you checked — a clean result is a valid outcome.
```

## What you get back

A findings table naming exactly which tool pairs share an instance and how risky that is, a short list of what's already fine (so you don't over-fix), any bypass rules that quietly undo your separation, and a ready-to-use CLAIM/VERDICT tagging manifest you can hand to whoever wires up the actual enforcement.

## What this does not do

This is a one-time paper audit, not a running guardrail. It does not watch your agent live, does not intercept real tool calls, and does not prove your system is secure — it tells you where to put the separation before you build it. The actual fix is wiring a real escalation boundary (a second independent model call, a different agent, or a human-approval step) into your live tool-call path, not just agreeing with the report.

## Guardrails this follows

- Never infers a tool's behavior from its name — unclear tools are flagged, not guessed.
- Never calls a second call to the *same* model sufficient independence for a HIGH-stakes verdict.
- Never treats the audit itself as proof of safety — always points back to needing a real enforcement step.
- Never recommends weakening an existing check to simplify the workflow.
- Never invents tool behavior, engagement numbers, or outcomes you didn't provide.
