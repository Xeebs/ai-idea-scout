---
name: mcp-hosted-deploy-approval-gateway
description: Drafts the governance checklist and PR body needed to approve a new (or changed) internal MCP server before it deploys, flags missing/overbroad fields, and recommends approve/escalate/block. Use when a team wants to request approval to stand up or modify an internal MCP server and needs the checklist filled and a recommendation before a human reviewer signs off.
---

# MCP Hosted Deploy Approval Gateway (Skill Angle)

## When to use this
A developer or platform team is about to request that a new internal MCP server (or a scope/tool change to an existing one) go live, and needs a filled-out governance checklist, a drafted approval PR body, and a flagged list of risks *before* a human approver looks at it. Reach for this skill the moment someone says something like "I need to get this MCP server approved," "can you draft the PR for adding this server," or "review this MCP manifest before we request sign-off." It is a one-shot authoring/review aid for a human preparing or reviewing a request — it does not deploy anything itself. (The full project this skill is drawn from also builds an always-on deploy-and-merge gateway that *enforces* this same checklist automatically; this skill is the standalone version anyone can run today without that infrastructure.)

## Inputs
**Data source**: Manual — paste the MCP server's manifest/tool list (tool names, descriptions, and the scope/permission each tool requests), its README or one-line purpose, and the checklist answers: auth type, data the server reads/writes, named maintainer, and intended hosting target. If you are running this inside Claude Code with access to the server's repository, the manifest and README can instead be read live from disk using the same checklist schema — but no live API or connector is required; this skill works standalone from pasted text alone.

Minimum required fields before any recommendation can be made:
1. Server name and one-line purpose
2. Full tool list with each tool's requested scope(s)
3. Auth type (e.g., OAuth with specific scopes, static API key, mTLS, service account, none)
4. Data the server reads and/or writes (be specific: "customer PII," "internal Jira tickets," "read-only public docs")
5. Named human maintainer (not a team alias)
6. Intended hosting target (optional but note it if given)
7. Any existing automated scan/trust-check output (optional — treat as advisory only)

## Procedure
1. **Extract the checklist.** Pull the six required fields above out of whatever was pasted. List each as Present or Missing.
2. **Block immediately on missing required fields.** If #1, #3, #4, or #5 above is missing, stop the risk analysis for that field and mark the overall recommendation no higher than ESCALATE (if some fields are missing but what's there looks low-risk) or BLOCK (if multiple required fields are missing, or the one missing is the maintainer or auth type).
3. **Score each tool's requested scope for least privilege.** For every tool, ask: does the tool's stated purpose require this scope, or a narrower one? Flag as OVERBROAD any scope that grants more than the stated purpose needs — e.g., a "post status comments" tool requesting `repo:admin` or `delete` rights, or a "read tickets" tool requesting write access. Never assume a scope is fine just because the manifest's description sounds benign; check the actual permission string against the actual stated purpose.
4. **Cross-check auth strength against data sensitivity.** Build a 2x2 read: if data touched includes anything resembling PII, credentials, financial data, or source code with secrets, and the auth type is "none," a shared static key with no rotation mentioned, or an overly broad service account, flag this combination as HIGH RISK regardless of how clean the tool scopes look individually.
5. **Note scanner output as advisory only, never as a pass/fail gate.** If scan/trust-check results were provided, summarize what they found, but explicitly state that a clean scanner result does not substitute for the scope and auth-strength checks in steps 3–4.
6. **Produce the recommendation.** Choose exactly one:
   - **APPROVE** — all required fields present, no overbroad scopes found, auth strength matches data sensitivity.
   - **APPROVE WITH CONDITIONS** — required fields present, but one or more scopes should be narrowed or a specific follow-up (e.g., scope reduction, maintainer confirmation, scanner re-run) is needed before merge.
   - **ESCALATE** — a HIGH RISK auth/data combination exists, or a non-blocking required field is missing, and a named security reviewer (not just the requesting team) needs to weigh in before this can merge.
   - **BLOCK** — multiple required fields are missing, or the maintainer or auth type field specifically is missing; do not let this proceed to any reviewer until the requester fills the gap.
7. **Draft the PR body** in the Output format below, ready to paste into a GitHub pull request for the approval workflow.

## Output format
Always produce, in this order:

1. **Checklist table** — the 6 fields, each marked Present/Missing, with the pasted value (or "MISSING — requester must provide").
2. **Scope risk table** — one row per tool: Tool name | Requested scope | Stated purpose | Verdict (OK / OVERBROAD) | Note.
3. **Auth/data risk line** — one sentence stating the auth type, the data sensitivity classification, and whether that combination is flagged HIGH RISK.
4. **Recommendation** — one of APPROVE / APPROVE WITH CONDITIONS / ESCALATE / BLOCK, in bold, with a 1–3 sentence rationale citing the specific table rows that drove it.
5. **Draft PR body** — a fenced markdown block containing a ready-to-paste PR description with headers: `## Server`, `## Requested Scopes`, `## Auth Type`, `## Data Accessed`, `## Maintainer`, `## Hosting Target`, `## Scanner Results (if any)`, `## Reviewer Recommendation` (populated with the recommendation and rationale from step 4).

## Guardrails
- Never output APPROVE if the maintainer field, auth type field, or data-touched field is missing — missing identity/accountability or data-sensitivity information always forces ESCALATE or BLOCK, no exceptions.
- Never invent a tool, scope, or checklist value that wasn't present in the input. If something is ambiguous, mark it Missing and ask for it rather than guessing a plausible-sounding answer.
- Never treat a clean automated scanner result as sufficient on its own — it is one input among several, not a substitute for the scope and auth-strength analysis.
- Never claim this skill deploys, merges, or approves anything. It drafts and recommends; a named human reviewer always makes the actual approve/reject call, and the PR body text must say so explicitly if asked to restate what happens next.
- Never soften an OVERBROAD scope finding into an OK verdict because the manifest's prose description sounds reasonable — verdict is driven by the permission string against the stated purpose, not by tone.
