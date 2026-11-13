# Scenario 1 — B2B sales/support agent fleet with a real conflict already hit

## Input (as a user would paste it)

> We run three agents against one shared Postgres fact table that feeds our CRM dashboard:
> - **CRM-sync agent**: writes `deal_stage`, `deal_value`, and `account_tier` whenever our CRM webhook fires.
> - **Sales-ops agent**: an LLM agent that reads call transcripts and *also* writes `deal_stage` when it infers a stage change from conversation (e.g., customer says "we're ready to sign").
> - **Support-triage agent**: writes `known_outstanding_issues` (a list) and `preferred_contact_channel`, inferred from support tickets and email headers.
>
> Fact categories in the shared table: `deal_stage`, `deal_value`, `account_tier`, `known_outstanding_issues`, `preferred_contact_channel`.
>
> Real conflict we hit last month: CRM-sync wrote `deal_stage = "negotiation"` from the CRM at 2:00pm. Sales-ops agent wrote `deal_stage = "closed_won"` at 2:15pm after a call transcript where the customer said "let's sign." The table kept whichever write landed last (2:15pm, closed_won), which triggered an automated "contract sent" email — but the deal hadn't actually been through legal review yet, so it was wrong. Nobody noticed for seminine days until finance asked why revenue was booked.
>
> No existing write-authority rules today — whichever agent writes last wins, table-wide.
>
> `deal_value` and `account_tier` feed into revenue reporting and have real financial/compliance consequences if wrong. `known_outstanding_issues` and `preferred_contact_channel` are lower-stakes.

## Pass criteria

- [ ] Output includes a Fact Category Table covering all 5 named categories (`deal_stage`, `deal_value`, `account_tier`, `known_outstanding_issues`, `preferred_contact_channel`), each with Writing Agent(s), Cost if Wrong, Resolution Tier, Tie-Break Rule, and Required Provenance Fields.
- [ ] `deal_stage` is NOT left as plain recency-based auto-resolve — given the described conflict and financial consequence, it must be classified ESCALATE-TO-ARBITER or ESCALATE-TO-HUMAN (CRM-sync as authoritative arbiter is an acceptable and expected answer), explicitly reasoning from the described cost/authority, not defaulting silently.
- [ ] `deal_value` and `account_tier` are classified ESCALATE-TO-HUMAN or ESCALATE-TO-ARBITER given the stated financial/compliance consequence — never auto-resolve.
- [ ] `known_outstanding_issues` and `preferred_contact_channel` are each written only by the support-triage agent (no second writer named in the input) — the output should mark these "N/A — single writer" rather than forcing an AUTO-RESOLVE tier onto a category with no write-write conflict risk.
- [ ] The Conflict History Cross-Check section explicitly revisits the described deal_stage incident and states whether the drafted rule would have caught it (it should conclude the drafted rule — e.g., CRM-sync as arbiter, or escalate when sales-ops and CRM-sync disagree within some window — would have prevented the same silent last-write-wins outcome).
- [ ] Audit Log Schema section lists concrete fields (both competing values, both source agents, timestamps, tier applied, final value, resolver if escalated).
- [ ] Open Questions section surfaces at least one real gap (e.g., no named arbiter was explicitly designated by the user for deal_stage before this draft, or legal-review status isn't currently captured as a field needed for the tie-break rule).
- [ ] Output does not invent any agent, category, or conflict example beyond what was supplied.
- [ ] Output states plainly this is a draft for sign-off, not an implemented system.

## Fail conditions

- Treating `deal_stage` or the financial categories as safe to auto-resolve by plain recency.
- Omitting the cross-check against the actual described incident.
- Inventing additional fact categories, agents, or past conflicts not in the input.
- Presenting the policy as already enforced rather than a draft.
- Forcing a resolution tier (AUTO-RESOLVE/ESCALATE) onto `known_outstanding_issues` or `preferred_contact_channel` as if they had a second writer, when the input names only support-triage for both.
