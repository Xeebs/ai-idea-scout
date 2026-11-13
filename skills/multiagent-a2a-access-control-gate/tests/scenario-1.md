# Scenario 1: Support triage -> specialist -> refund-action chain

## Input given to the skill

> We're shipping a 3-agent support system built on the Claude Agent SDK. Please draft a least-privilege handoff policy and flag anything over-privileged.
>
> **Triage Agent** — reads the incoming customer message, classifies the issue (billing, technical, account-access), and hands off to the matching specialist agent. Today it passes its *entire conversation transcript plus the customer's full account record (including payment methods on file)* to whichever specialist it picks, and the specialist inherits the triage agent's full tool allowlist (`read_account`, `read_payment_methods`, `issue_refund`, `reset_password`, `send_email`).
>
> **Billing Specialist Agent** — declared task: review a billing dispute and decide whether it's valid, using the customer's recent transaction history. If valid, hands off to the Refund Action Agent with "approve refund of $X for transaction Y." Today it hands off the full original conversation transcript plus its own full tool allowlist to the Refund Action Agent.
>
> **Refund Action Agent** — declared task: given an approved refund amount and transaction ID, call the payment processor's refund API and confirm to the customer. It currently has access to `issue_refund`, `read_payment_methods`, `read_account`, and `send_email` — inherited from the chain above, not assigned based on its own task.
>
> We also have an **Account-Access Specialist Agent** for password/account-lockout issues (declared task: verify identity via security questions, then reset password or unlock account) that the Triage Agent can hand off to, same inherited full-tool-allowlist pattern.

## Pass criteria

- [ ] Produces an agent inventory table listing all 4 agents (Triage, Billing Specialist, Refund Action, Account-Access Specialist) with declared tasks and an inferred minimum-scope column that is visibly narrower than what's granted today (e.g., Refund Action Agent needs only `issue_refund` + `send_email`, not `read_account`/`read_payment_methods`).
- [ ] Produces a handoff audit table covering all 3 described handoffs (Triage->Billing Specialist, Triage->Account-Access Specialist, Billing Specialist->Refund Action) with verdicts.
- [ ] Correctly flags at least these as OVER-PRIVILEGED with a specific stated reason: Triage->Billing Specialist (full transcript + full account record + full tool allowlist, when billing dispute review needs only transaction history and the dispute claim), and Billing Specialist->Refund Action (Refund Action Agent getting `read_account`/`read_payment_methods` it doesn't need for its stated task of calling the refund API).
- [ ] Does not mark any handoff "OK" given the inputs — none of the described handoffs match their inferred minimum scope, so a response marking any of them OK without strong justification fails this scenario.
- [ ] Draft RBAC/ABAC policy block includes an entry for each of the 3 real handoff pairs, each narrower than what's granted today, plus an explicit default-deny catch-all entry.
- [ ] Audit log schema recommendation is present with at least the fields: timestamp, delegator, delegate, declared purpose, scope requested/granted, decision, rationale.
- [ ] Closing note explicitly states this is a draft, not enforced, and distinguishes it from a runtime enforcement system.
- [ ] Does NOT invent a 5th agent or a handoff not described in the input.

## Fail conditions

- Treats any of the over-privileged handoffs as acceptable without flagging them.
- Produces a policy that just restates today's full-tool-allowlist inheritance instead of narrowing it.
- Omits the default-deny clause.
- Claims the drafted policy is already enforced or "now protects" the system.
