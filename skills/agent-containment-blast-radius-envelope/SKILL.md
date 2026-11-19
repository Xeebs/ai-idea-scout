---
name: agent-containment-blast-radius-envelope
description: Audits a pasted description or config of an AI agent's tool access, credential scope, approval logic, and session limits, and scores how contained it actually is. Use when a team is about to grant an agent real tool access (file systems, cloud APIs, payment/messaging systems) and wants a concrete exposure score and the single highest-leverage fix before deciding whether to build a real enforcement layer.
---

# Containment Envelope Audit

## When to use this
Reach for this the moment someone is about to let an agent act with real tool access — before a production launch, before widening an existing agent's permissions, or right after a near-miss (an agent did something it technically could but shouldn't have). It is a one-time diagnostic, not a running service: it tells a team how exposed their *current* setup is, so they can decide whether to invest in a real enforcing containment layer (short-lived scoped credentials, a sandboxed runtime, an approval gateway, a budget-and-kill-switch layer) rather than guessing.

Do not reach for this to debug a specific incident already in progress, to design the enforcement layer itself, or to replace a real penetration test / red-team exercise.

## Inputs
**Data source**: Manual — the user pastes a description or exported config of their agent's current tool access, credential scope, and any approval/sandboxing/timeout logic already in place (e.g., an MCP server config, an IAM/STS policy snippet, agent-SDK permission settings, approval-queue code, or just plain prose describing what the agent can do). No connector or API access is required or used by this skill — if the user says "it's wired into our real AWS account," ask them to paste the actual policy/role text rather than assuming details not given.

Minimum needed to run a useful audit:
1. What tools/APIs the agent can call (file system, specific cloud APIs, payment, messaging, etc.)
2. What credential(s) it uses to call them, and how long those credentials live
3. Whether any action requires a human to approve it before it executes
4. Whether there's any cap on session length, call count, or spend, and what happens when a cap is hit

If one of these four is simply missing from what was pasted, treat it as "0 — not stated" rather than assuming it's handled well or badly.

## Procedure
1. Parse the input into the four containment dimensions below. Do not invent capabilities, credentials, or controls the user didn't describe.
2. Score each dimension 0–3:
   - **0** — Not present / unbounded (e.g., one shared long-lived key with full access, no approval anywhere, no cap, no scoping).
   - **1** — Documented or intended only, not actually enforced by any mechanism (a policy doc, a comment, a prompt instruction telling the agent to "be careful").
   - **2** — Partially enforced — a real mechanism exists but has gaps (covers some tools/paths/actions but not others, or enforced only in some code paths).
   - **3** — Enforced with a verifiable mechanism (real scoped/short-lived credentials, a real sandbox boundary, a real blocking approval step, a real auto-terminating cap).
3. The four dimensions, scored independently:
   - **Least privilege** — is the agent's tool/API/file-path surface scoped to the minimum needed for its task, or does it hold broader access "just in case"?
   - **Credential isolation** — does it use short-lived, narrowly-scoped credentials issued per session/task, or a long-lived/shared/admin credential?
   - **Approval gates** — does any class of action (destructive, high-spend, irreversible) require a human or a second system to approve before it executes?
   - **Termination / budget caps** — is there a hard limit on session duration, tool-call count, or spend, with an actual kill mechanism when it's exceeded — not just a soft warning?
4. Compute **Exposure Score** = 12 − (sum of the four dimension scores). Range 0 (fully contained) to 12 (fully unbounded).
5. Map the Exposure Score to a band: 0–2 LOW · 3–5 MODERATE · 6–8 HIGH · 9–12 CRITICAL.
6. Identify the single lowest-scoring dimension (ties broken toward whichever one touches irreversible or financial actions) and state the one concrete, stack-agnostic fix that would raise it by one point — not a vendor product name, a described mechanism (e.g., "issue per-session STS tokens scoped to this one bucket prefix instead of the current long-lived IAM user key").
7. Write one short worst-case paragraph grounded only in what was pasted: if this exact agent were successfully prompt-injected or jailbroken right now, what is the largest plausible blast radius given its stated tools, credential scope, and caps (or lack of them)? Do not invent numbers not derivable from the input (e.g., only state a dollar figure if a spend-capable action and its limit were actually described).
8. Before finalizing, scan the pasted input for anything that looks like a live secret (API key, token, password). If found, do not reproduce it in the output — refer to it generically ("the pasted Zendesk token") and tell the user to rotate it if it was ever shared outside this conversation.

## Output format
A single markdown report, in this order:
1. **Exposure Score: N/12 — BAND** (one line, bolded band)
2. A 4-row table: Dimension | Score (0-3) | One-line justification tied to what was actually pasted
3. **Weakest dimension**: name it, and the one concrete fix (2-3 sentences max)
4. **If this agent were jailbroken right now**: the one-paragraph worst case
5. A one-line caveat: "This is a self-reported audit of what was described, not a penetration test — it can't catch controls that exist but weren't mentioned, or gaps that only show up under adversarial testing."

## Guardrails
- Never score a dimension based on what a "typical" or "best practice" setup would have — score only what was actually described, and mark anything unstated as 0 with "not stated" in the justification, never as a charitable guess.
- Never reproduce a live-looking secret, token, or credential value from the input back into the output.
- Never recommend a specific commercial product or vendor by name as "the fix" — describe the mechanism generically so the fix applies regardless of stack.
- Never present the Exposure Score as a certification, compliance pass/fail, or substitute for a real red-team/penetration test.
- Never skip straight to recommending "build the full enforcing containment layer" without first giving the per-dimension breakdown — the score and the weakest-dimension fix are the deliverable; the enforcing layer is a separate, bigger decision the user makes afterward.
