# Scenario 2 — 48-person B2B SaaS startup

## Input (as the user would paste it)

> We're a 48-person SaaS company. Sales (9 people), customer support (12 people), onboarding/customer-success (6 people), and engineering/ops (the rest) all have individual Claude seats. Sales uses Salesforce, which is connected via Salesforce's MCP server already — that part works fine. Support uses Zendesk, not connected to any AI agent currently. We don't have an accounting connector set up (we use a third-party payroll/billing vendor for that, nobody's agent touches it).
>
> Pain points: (1) support reps have given customers different answers about our refund policy because each rep's agent only knows what that rep has personally been told or has pasted into their own chat — we've had at least three customer complaints about this in the last two months. (2) When sales closes a deal, onboarding finds out days later via a Slack message someone remembered to send, not automatically, so onboarding has started customers late twice this quarter.
>
> We're not trying to replace Salesforce or Zendesk — we want to stop each of the 27 sales/support/CS people needing to separately explain context to their own agent.

## What a passing output looks like

- **Role Roster**: 3–5 roles scoped mainly to sales, support, and onboarding/customer-success (engineering/ops may reasonably be marked out of scope since no pain point or tool was given for it — a good output either omits it or flags it as "no evidence provided, not included in this pilot"). Must not force a 1:1 role-per-department split beyond what the evidence supports.
- **Tool/Connector Scope**: Salesforce marked as "already connected via MCP server, live" — matches what the user said. Zendesk marked as "named, not yet connected." Must NOT invent an accounting/billing connector or claim one is wired up, since the user explicitly said payroll/billing is untouched by any agent.
- **Handoff Map** must include a handoff that directly targets pain point (2): a `deal.closed_won` (or equivalently named) event from the sales role to the onboarding/CS role, replacing the "someone remembered to send a Slack message" step — with a payload (e.g., account name, start date, contract terms) specific enough to be useful, not just "notify onboarding."
- **Memory scope for the support role** must directly address pain point (1): a single shared refund-policy / support-knowledge memory scope the support role agent owns, so individual reps stop relying on what they personally were told.
- **Ambiguous Ownership & Escalation**: a believable fuzzy case for this team — e.g., a customer mid-onboarding who files a support ticket (does support or onboarding/CS own it?) — with an explicit human-fallback rule.
- **Migration Plan**: pilots the roles with evidence (support and/or sales→onboarding handoff) first, not engineering/ops.
- **Success Metrics** include something that would catch pain point (1) directly — e.g., count of contradictory policy answers given to customers, trackable against the "three complaints in two months" baseline — and something for pain point (2) — e.g., time from deal-closed to onboarding kickoff.
- **Existing Infra Check**: notes Salesforce's MCP connector is already live and usable as the sales role's data source; does not recommend replacing Salesforce or Zendesk (the user explicitly said they don't want that).

## Fail conditions
- Includes engineering/ops as a full role with an invented memory scope and connector despite zero evidence given.
- Marks Zendesk or a billing/accounting connector as already live.
- No handoff event addresses the sales-to-onboarding delay (pain point 2).
- No shared memory scope addresses the support contradictory-answer problem (pain point 1).
- Recommends building a brand-new CRM or support system instead of using Salesforce/Zendesk as stated.
- Produces more than 5-6 roles, re-fragmenting the 27-person group back toward one-per-function-per-shift rather than consolidating.
