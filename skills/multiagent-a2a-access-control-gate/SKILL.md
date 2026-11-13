---
name: multiagent-a2a-access-control-gate
description: Drafts an RBAC/ABAC policy for a multi-agent system's agent-to-agent handoffs (who may hand off to whom, with what scope) and flags today's handoffs that grant a downstream agent more access than its declared task needs. Use before shipping a delegation-heavy agent system (triage -> specialist -> action, or similar), during a security review of an existing one, or when a maintainer asks "what should our subagents actually be allowed to do at each handoff."
---

# A2A Policy Draft

## When to use this
Use this when someone describes or pastes the agents in a delegation chain (a triage agent that hands off to specialist agents, which hand off to action agents, or any similar multi-hop setup built on the Claude Agent SDK, LangGraph, OpenCode, or a custom orchestrator) and asks a question shaped like: "what RBAC/ABAC policy should govern our agent handoffs," "are any of our subagents over-privileged relative to what they're supposed to do," or "draft a least-privilege policy for this delegation chain before we ship it." This is a one-shot, point-in-time design and review task — it produces a draft policy document and a list of flagged over-grants from the information given, not a running system. If the user wants that policy actually *enforced* at runtime — minting scoped identities and blocking out-of-policy handoffs as they happen — that is a different, infrastructure-shaped project (a gate wired into the framework's own subagent-spawn/handoff hook with its own identity issuer and audit log); tell them so explicitly rather than implying this skill enforces anything.

Do not reach for this when the ask is about human-to-agent access (who on the team may invoke which agent) — that is multi-user access control, a different and already better-served problem (e.g., Alter's "access control for multi-user agents"). This skill is scoped strictly to agent-to-agent trust boundaries: which agent role may hand off to which other agent role, and with what scope.

## Inputs
**Data source**: Manual — the user describes or pastes, for each agent in the chain: its name/role, its declared task, and the handoffs it makes today (which downstream agent it calls, and what context/tools/credentials get passed at that hop — e.g., "the triage agent passes its entire conversation history and its own tool allowlist to the specialist agent"). Pasting the actual subagent-spawn code or config (a Claude Agent SDK subagent definition, a LangGraph node/edge definition, an OpenCode subagent manifest, or a custom `spawn_child()`/`delegate()` call) is the strongest input and should be requested if the user only gives a vague prose description. When this skill runs inside Claude Code with the repo already open, it may use Read/Grep to pull these definitions directly from the files instead of asking the user to paste them — but no mature cross-framework connector exists today that supplies this input automatically, so file-reading here is a convenience within an already-open session, not a standing data connection. This is deliberately narrower than the parent idea's CONNECTED classification: that classification describes the separate runtime enforcement engine (the Project half of this idea), which wraps the framework's live handoff hook to issue scoped identities on every real invocation. This skill never wraps a live hook and never runs continuously — it is the one-shot design/review half, so its own data source is Manual.

If the input describes zero agents or zero handoffs, say so explicitly and ask for the delegation chain description or code — never fabricate agents or handoffs to have something to draft a policy for.

## Procedure
1. **Inventory every agent.** For each agent named in the input, record `(role name, declared task/purpose, tools or data it needs for its OWN task as stated)`. If an agent's declared task is missing or too vague to infer minimum necessary scope, mark it `UNDERSPECIFIED` and ask the user for its task description rather than guessing.
2. **Inventory every handoff.** For each handoff, record `(from role, to role, trigger condition if stated, scope granted today — what context/tools/credentials actually get passed)`. If the "scope granted today" isn't stated, mark it `UNSTATED` rather than assuming it's either minimal or full.
3. **Infer the minimum necessary scope for each handoff**, derived strictly from the downstream agent's declared task (step 1) — not from what it currently receives. State this as a concrete, narrow list (specific tools, specific data fields/categories, specific actions), never a vague "needs context."
4. **Compare granted vs. minimum necessary for every handoff** and assign a verdict:
   - `OK` — granted scope matches or is narrower than the inferred minimum necessary scope.
   - `OVER-PRIVILEGED` — granted scope is broader than the inferred minimum (e.g., full conversation history or the parent's full tool allowlist passed to an agent whose declared task needs only a summary and two tools). State exactly what's being over-granted.
   - `UNCLEAR` — either the granted scope or the minimum necessary scope couldn't be determined from the input. Never resolve this by guessing in either direction; name what additional detail would resolve it.
5. **Draft the RBAC/ABAC policy.** For every handoff pair that exists today, write one policy entry: `role (from) -> role (to): allowed actions/tools/data [+ any attribute conditions, e.g., "only when task_type == billing_dispute"]`. Base the allowed scope on the inferred minimum necessary scope from step 3, not on what's currently granted (step 2) — the draft policy is the fix, not a restatement of the status quo.
6. **Add an explicit default-deny clause**: any handoff pair not listed in step 5 is denied by default. Call this out as a named line in the output, not an implied assumption.
7. **Recommend an audit log schema** (fields only — this skill does not implement logging): timestamp, delegator role, delegate role, declared task/purpose for the handoff, scope requested, scope granted, decision (allow/deny), rationale.
8. **Compute the summary verdict**: count of agents, count of handoffs, count OK / OVER-PRIVILEGED / UNCLEAR. If any handoff is `OVER-PRIVILEGED`, the overall headline must say so plainly — never bury it under a generic "policy drafted successfully."

## Output format
A markdown report, in this order:
1. **Verdict line**: `<n> agents, <h> handoffs reviewed — <ok> OK, <op> OVER-PRIVILEGED, <u> UNCLEAR`.
2. **Agent inventory table**: columns `Role | Declared Task | Scope Needed for Own Task`.
3. **Handoff audit table**: columns `From -> To | Trigger | Scope Granted Today | Minimum Necessary Scope | Verdict | Why`. OVER-PRIVILEGED rows first, then UNCLEAR, then OK.
4. **Draft RBAC/ABAC policy block** (YAML-style, one entry per handoff pair from step 5, plus the default-deny clause as the final entry).
5. **Recommended audit log schema** (the field list from step 7).
6. **What this does not cover**: a fixed closing note — this is a point-in-time draft based only on the input given; it is not wired to anything and enforces nothing by itself; it cannot see handoffs that happen outside what was described/pasted; re-run it after any change to the agent roster or handoff code. For live enforcement, the user needs the separate runtime gate project, not this draft.

## Guardrails
- Never invent an agent, a handoff, or a declared task that wasn't in the input — if the chain described is incomplete, say what's missing and ask, rather than filling gaps with assumptions.
- Never mark a handoff `OK` by assuming the granted scope is minimal just because the user didn't describe it as excessive — if scope granted today isn't stated, it's `UNSTATED`/`UNCLEAR`, not `OK`.
- Never draft a policy entry broader than the inferred minimum necessary scope "to be safe" or "to avoid breaking things" — when in doubt, draft narrower and flag the ambiguity for the user to widen deliberately if needed.
- Never omit the default-deny clause — a policy draft with no explicit catch-all deny is not a least-privilege policy, it's a list of exceptions with an implicit allow-all underneath.
- Never claim this policy is enforced, wired into the agents, or protecting anything until a human implements it in a real policy engine (OPA, Cedar, a custom gate, etc.) — this skill produces a document for review, not a running control.
- Never conflate agent-to-agent handoff scope with human-to-agent access control. If the entire input is about which humans may invoke which agents, say this skill doesn't cover that and stop rather than drafting an irrelevant policy. If the input mixes a real agent-to-agent handoff question with a human-access question, answer the agent-to-agent part in full using the procedure above, call out the human-access part by name as out of scope for this skill (without answering it), and do not let the mixed input shrink or skip the agent-to-agent analysis.
