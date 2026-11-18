# Autonomy Ladder: Risk-Tier Advisor

A self-contained prompt template for deciding which autonomy tier a new (or existing) AI agent task should run at, instead of a binary "fully allowed" vs. "banned entirely" decision. Paste this whole document into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with your task details, and it will walk you through the tiering and hand you a draft policy entry.

## When to use this

You're about to let an AI agent take on a new capability — issuing refunds, rebooking travel, rescheduling shipments, editing records, sending customer communications, anything with real-world side effects — and you want a defensible, specific answer to "how much autonomy should it have for *this* task" rather than defaulting to "let it run free" or "ban agents from this entirely." It's also useful after an incident: instead of banning the whole task type (the pattern behind real cases like an airline banning AI agents from booking flights, or a food-delivery platform's agent usage collapsing to near-zero after trust issues), you can find the narrow slice of risk that actually caused the problem and gate just that.

This is a one-shot advisory tool. It does not connect to, monitor, or enforce anything live — it gives you a recommendation and a draft policy entry that a human then reviews and enters into whatever system actually gates your agent's real tool calls (an API, an MCP client wrapper, a framework-level hook, etc.).

**Data source**: Manual. You paste in a description of the task and answer four risk questions yourself (see below). This tool never reads your live systems, agent logs, or policy store — if you want it to stay consistent with policy entries you've already drafted, paste those in too, but that's still a manual paste, not a live connection.

## What to hand it

Give it, in plain text:

1. **The task description** — exactly what the agent would do, concretely (e.g., "issue a refund to a customer's original payment method for orders under $500" — not "handle customer stuff").
2. **Reversibility** — can the action be undone, and at what cost? Fully reversible with no cost / reversible but with delay or cost / irreversible.
3. **Financial exposure** — the dollar scale of one action, and the plausible worst case across many actions (state your own threshold if you have one; otherwise it will assume $100/action as the low-risk cutoff and say so).
4. **Blast radius** — who's affected if it goes wrong: nobody but a sandbox, one customer/user, a team or batch of customers, or the whole org/public/regulators.
5. **Regulatory sensitivity** — is this governed by a named law or industry rule (HIPAA, PCI-DSS, aviation booking conditions, financial compliance), internal policy only, or nothing.

If you leave any of 2–5 vague, expect it to ask a follow-up before giving you a tier — it will not guess silently.

## What it does with that information

1. Scores each of the four risk dimensions 0–3 using fixed anchors (e.g., irreversible = 3, affects the whole org/public = 3, governed by a named regulation = 3).
2. Takes the *highest* of the four scores as the task's overall risk — one severe dimension is enough to force a stricter tier, even if everything else is low.
3. Maps that overall score to one of four tiers:
   - **0 → Fully Autonomous** — agent acts with no gate, logged for routine audit.
   - **1 → Auto-Execute-with-Audit** — agent acts immediately, flagged for review within a set window.
   - **2 → Propose-and-Confirm** — agent drafts the action, a human must approve before it executes.
   - **3 → Observe-Only** — agent may recommend but may never execute.
4. Applies a hard override: if the action is irreversible *and* carries any nonzero financial or regulatory exposure, the tier can never be looser than Propose-and-Confirm, regardless of what the scoring alone would suggest.
5. Flags genuine edge cases (boundary scores, risk dimensions that don't cleanly capture something like reputational damage) instead of silently picking a side.
6. Drafts a ready-to-paste policy entry in a fixed YAML schema so multiple entries stay consistent.

## What you get back

A short report with four parts, always in this order:

1. **Recommended Tier** — the tier name and a one-sentence reason.
2. **Dimension Scores** — a table: dimension, score 0-3, reasoning, plus whether the hard override kicked in.
3. **Draft Policy Entry** — a YAML block:
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
4. **Caveats** — any assumed defaults, flagged edge cases, and a reminder that nothing here is live until a human puts it into your actual enforcement system.

## Guardrails (the tool will refuse or push back if asked to violate these)

- It will never recommend Fully Autonomous or Auto-Execute-with-Audit for an irreversible action that carries any financial or regulatory exposure — that combination always gets gated behind at least a human-confirmation step.
- It will never quietly fill in a missing risk answer — it either asks, or states plainly which default it assumed.
- It will never claim to have activated or enforced a policy — every output is explicitly a draft pending human approval.
- If you ask it to re-tier a capability that's already live in production, it will flag that as a policy *change* needing its own approval, not treat it like a fresh task type.
- If your task description actually bundles multiple distinct actions with different risk profiles (e.g., "refund orders and also close accounts"), it will tell you to split them into separate entries rather than scoring the bundle as one thing.

## Example prompt to paste

> I need an autonomy tier recommendation for an AI agent capability. Task: the agent can automatically rebook a customer's flight to the next available flight on the same airline, same fare class, with no change fee, when their original flight is cancelled by the airline. Reversibility: reversible — customer can call support to be moved again, no cost to the airline. Financial exposure: the new ticket is already paid for (same fare class), so no incremental spend per action; across a bad weather day this could apply to a few thousand passengers at once. Blast radius: affects individual customers, one at a time, but could spike to a few thousand in a single irregular-ops event. Regulatory: airline ticketing and fare rules apply (DOT rules on involuntary rebooking). Please score this and draft the policy entry.
