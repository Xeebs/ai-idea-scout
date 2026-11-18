---
name: enterprise-risk-tiered-agent-autonomy-framework
description: One-shot recommendation of an autonomy tier (observe-only, propose-and-confirm, auto-execute-with-audit, fully autonomous) for a specific agent task type, scored against reversibility/financial/blast-radius/regulatory risk dimensions, plus a drafted policy-DSL entry ready to paste into a live enforcement config. Use before writing a policy entry for a new agent capability, or when deciding whether to re-tier an existing one after an incident.
---

# Autonomy Ladder: Risk-Tier Advisor

## When to use this
A team is about to grant an AI agent a new capability or task type (e.g., "the support agent can issue refunds," "the ops agent can reschedule shipments," "the travel agent can rebook flights") and needs to decide which autonomy tier it belongs in *before* writing a policy entry — instead of defaulting to a binary "let it run" vs. "ban it entirely" choice. Also use this after an incident, to re-evaluate whether a task type that was banned wholesale could instead be safely re-enabled at a lower tier for the specific slice of risk that caused the incident.

Do not use this to build or operate the always-on enforcement middleware that intercepts live agent tool calls — that is a separate, persistent infrastructure build (the parent project this skill was distilled from). This skill produces a one-shot recommendation and a draft policy entry for a human to review and enter into that system; it does not enforce anything itself.

## Inputs
**Data source**: Manual — the user pastes a description of the task (what the agent would actually do, step by step) and answers to the four risk-dimension questions below. (The parent idea is classified Data Sources: CONNECTED, because the always-on enforcement middleware reads live tool-call execution from the agent framework/MCP client — a mature, existing interception point. This skill is the one-shot authoring/review half of that BOTH-format idea and runs entirely on manually supplied task descriptions; it has no live connection to any agent framework, tool-call stream, or policy store. If the user has an existing policy-DSL file, they may optionally paste it so new entries stay consistent with existing ones, but this is also manual paste, not a live read.)

Required for every request:
1. **Task description** — what the agent does, concretely, in this task type (e.g., "issue a refund to a customer's original payment method for orders under $500").
2. **Reversibility** — can the action be undone, and how costly is undoing it? (fully reversible / reversible with effort or delay / irreversible)
3. **Financial exposure** — the dollar range or scale of a single action, and of the task type's plausible worst case (e.g., "$500 per action, no cap on how many per day").
4. **Blast radius** — who is affected if it goes wrong: one customer, a team, the whole org, or external third parties/public reputation.
5. **Regulatory/compliance sensitivity** — is the task type governed by a named regulation or industry rule (e.g., aviation booking rules, HIPAA, PCI-DSS, financial services compliance), internal policy only, or none.

If any of 2–5 is missing or vague, ask a targeted follow-up question for that specific dimension before scoring — never silently assume a value.

## Procedure
1. **Confirm all five inputs are present and concrete.** If the task description is vague ("the agent handles customer stuff"), ask for the specific action, not a category.
2. **Score each of the four risk dimensions 0–3** using these anchors:
   - **Reversibility**: 0 = fully reversible with no cost (e.g., re-sending an email) · 1 = reversible but with delay/cost (e.g., a correction requires a manual follow-up) · 2 = reversible only via an external party or with material cost/delay (e.g., clawing back a payment) · 3 = irreversible (e.g., a non-refundable booking, a deleted record, a message already seen by a customer).
   - **Financial exposure**: 0 = effectively $0 or internal-only · 1 = under a small threshold the org sets (default assumption: under $100/action unless the user states their own threshold) · 2 = moderate, up to a few thousand dollars per action or meaningful cumulative exposure across many actions · 3 = large single-action exposure or uncapped/unbounded cumulative exposure.
   - **Blast radius**: 0 = affects only internal test/sandbox state · 1 = affects one external customer or one internal user · 2 = affects a team, a batch of customers, or a visible internal system · 3 = affects the org broadly, the public, or a regulator-visible population.
   - **Regulatory sensitivity**: 0 = no policy or regulation touches this · 1 = internal policy only · 2 = named industry rule or contractual obligation (e.g., airline booking conditions, a SLA) · 3 = named law/regulation with penalties (e.g., HIPAA, PCI-DSS, financial services compliance, aviation safety rule).
3. **Apply the highest-dimension-wins rule.** The task type's overall risk score is the *maximum* of the four dimension scores, not an average — one severe dimension is enough to force a higher tier even if the other three are low.
4. **Map the overall risk score to a tier**, using the inverse relationship (higher risk → less autonomy):
   - Risk 0 → **Fully Autonomous** — agent acts with no gate; routine audit log only.
   - Risk 1 → **Auto-Execute-with-Audit** — agent acts immediately; action is logged and flagged for review within a set window (e.g., next business day).
   - Risk 2 → **Propose-and-Confirm** — agent drafts the action and a human must explicitly approve before it executes.
   - Risk 3 → **Observe-Only** — agent may analyze and recommend but may never execute the action itself.
5. **Apply the hard override**: if Reversibility scored 3 (irreversible) AND Financial exposure or Regulatory sensitivity scored ≥1, force the tier to Observe-Only or Propose-and-Confirm (never allow Auto-Execute or Fully Autonomous for irreversible actions carrying any nonzero financial or regulatory exposure), regardless of what the highest-dimension-wins rule alone would produce.
6. **Flag genuine edge cases** — if two dimensions are both at the boundary between tiers, or the task description describes something the four dimensions don't cleanly capture (e.g., reputational risk with no direct financial exposure), say so explicitly and recommend the more conservative tier rather than resolving the ambiguity silently.
7. **Draft the policy-DSL entry** in the fixed YAML schema below, using the task description as the `task_type` identifier (kebab-case) and the recommended tier.
8. **State plainly that this is a recommendation for human review**, not an enforced policy — it must be entered into the organization's actual policy store/enforcement middleware by someone with authority to do so.

## Output format
A single markdown report with four sections, in this order:

1. **Recommended Tier** — one line: the tier name and a one-sentence plain-language justification.
2. **Dimension Scores** — a 4-row table: Dimension | Score (0-3) | Reasoning, one row per dimension from Step 2, plus a final row noting whether the hard override from Step 5 applied.
3. **Draft Policy Entry** — a fenced YAML block in this schema:
   ```yaml
   task_type: <kebab-case-id>
   description: "<one-line restatement of the task>"
   risk_scores:
     reversibility: <0-3>
     financial_exposure: <0-3>
     blast_radius: <0-3>
     regulatory_sensitivity: <0-3>
   overall_risk: <0-3>
   tier: <observe_only | propose_and_confirm | auto_execute_with_audit | fully_autonomous>
   hard_override_applied: <true | false>
   recommended_by: autonomy-ladder-skill
   status: draft_pending_human_approval
   ```
4. **Caveats** — any missing input that had to be assumed (state the assumption explicitly, e.g., "assumed the default $100 financial-exposure threshold since none was given"), any edge case flagged in Step 6, and a reminder that this entry is not active until a human enters it into the live policy system.

## Guardrails
- Never assign Fully Autonomous or Auto-Execute-with-Audit to a task with Reversibility = 3 and any nonzero Financial exposure or Regulatory sensitivity score — the Step 5 hard override is non-negotiable.
- Never silently fill in a missing risk dimension with a guessed value — ask, or state explicitly in Caveats that a stated default was used and name it.
- Never claim this skill has enforced, deployed, or activated a policy — every output must state it is a draft awaiting human approval and entry into the live enforcement system.
- Never re-tier an *existing* live policy entry without flagging it as a policy change that needs its own approval workflow, distinct from a brand-new task type.
- Keep the YAML field names and structure identical across every invocation so multiple drafted entries can be concatenated into one policy file without reformatting.
- If the task description bundles multiple distinct actions with different risk profiles (e.g., "the agent can refund orders and also cancel accounts"), say so and recommend splitting it into separate task-type entries rather than scoring the bundle as one task.
