---
name: multiagent-archetype-fleet-governance-library
description: Drafts a per-archetype governance-tier config (guardrail profile, token-bucket rate limit, financial spend cap, isolation rules) for a multi-agent fleet from a plain-language description of each archetype's role and risk. Use when someone is standing up or auditing an agent fleet with distinct roles (support bot, code-review bot, finance-ops bot, etc.) and needs a starting tiering scheme before wiring up real enforcement.
---

# Multi-Agent Archetype Fleet Governance Config Drafter

## When to use this
A user is running, or about to run, more than one distinct type ("archetype") of AI agent in production — e.g. a customer-support agent, a code-review agent, a finance-ops agent that can issue refunds or move money — and either:
- has no governance tiering at all (one blanket policy for every agent), or
- is hand-rolling a tier scheme from scratch and wants a second opinion / starting draft, or
- just had an incident (runaway spend, an agent taking an irreversible action it shouldn't have) and wants to retrofit tiers.

This skill drafts the *design* — the tier assignments and the config values. It does not run, enforce, or wire up anything. It is the design/review step that precedes building or configuring the actual runtime enforcement middleware (the library half of this idea).

## Inputs
**Data source**: Connected (per the parent idea) — the runtime enforcement half of this idea hooks into each agent framework's own tool-dispatch/budget extension point (CrewAI task callbacks, LangGraph node hooks, AutoGen's agent wrapper, Claude Code subagent hooks) and optionally a provider usage/billing API (OpenAI's or Anthropic's), all mature today. This skill, however, is the upstream design aid, not the runtime library, so its actual input is **Manual**: the user describes each archetype in plain language — what it is, what tools/actions it can invoke, how reversible those actions are, and any blast-radius or incident history. The user may optionally paste real numbers from their provider's usage/billing dashboard to ground the spend caps instead of letting the skill estimate them, but nothing is read automatically — this skill never connects to anything itself.

Required, per archetype:
1. Name/role (e.g. "customer-support agent", "finance-ops agent").
2. What it's allowed to do — the concrete tool/action list, not a vibe ("can read tickets and draft replies" vs. "can issue refunds up to $X" vs. "can merge PRs to main").
3. How reversible its actions are (a drafted reply a human approves before sending vs. an auto-sent refund vs. a code merge that ships).

Helpful if available, not required:
- Current or desired call volume / concurrency per archetype.
- Any existing budget number (daily/monthly spend target) per archetype.
- Target framework(s) in use (CrewAI, LangGraph, AutoGen, Claude Code subagents) — only used to phrase the "wire this into..." note, never to fabricate a specific hook call the user didn't confirm.
- Any past incident ("it looped and sent 400 replies before we caught it") — this directly tightens the rate-limit draft.

## Procedure
1. **Parse each archetype** into three axes: action scope (what it can touch), reversibility (can a human undo it, or is it final the moment it fires), and blast radius (how much damage one bad run can do — one ticket vs. the whole refund ledger).
2. **Assign a tier** using this rubric (four tiers, matching the idea's "autonomy-tier" framing):
   - **Tier 1 — Read/Advisory**: can only read or draft; nothing it does takes effect without a human sending/approving it.
   - **Tier 2 — Reversible action**: can act autonomously but the action is cheaply undone (e.g. tag a ticket, post an internal comment, open a draft PR).
   - **Tier 3 — Costly/hard-to-reverse action**: acts autonomously and the action is expensive or slow to undo (e.g. send a customer email, close a ticket, merge to a non-protected branch).
   - **Tier 4 — Financial/irreversible**: can move money, merge to production, or take any action that can't practically be undone.
   If an archetype's description doesn't give enough to place it confidently (e.g. "handles customer stuff" with no action list), do not guess — list it under "Needs more detail" with the specific question that would resolve it, and skip tiering it.
3. **Draft the guardrail profile per tier** — scale strictness to tier, don't give every archetype the same checklist:
   - Tier 1: output filtering only (PII/toxicity check on drafts).
   - Tier 2: output filtering + input validation on the action payload.
   - Tier 3: output filtering + input validation + a human-approval gate above a stated threshold (e.g. "auto-send under $50 equivalent impact, otherwise queue for approval").
   - Tier 4: everything in Tier 3 + mandatory human approval on every invocation, no auto-send threshold, full action logging.
4. **Draft the token-bucket rate limit per archetype** — bucket size (burst capacity) and refill rate (steady-state calls/minute), scaled to the stated or inferred call volume. If no volume was given, propose a conservative starting number explicitly labeled as an assumption (e.g. "assumed starting point: 10 calls/min burst, 2/min refill — tighten or loosen once you have real traffic data"). If the user mentioned a past incident (a loop, a duplicate-action event, a near-miss), the draft must visibly reference it in the rationale and tighten the burst capacity and/or add a dedup/idempotency guardrail accordingly — an incident mentioned and then silently ignored is a failure of this step.
4a. **Flag structural gaps the user's own description reveals** (no staging environment, no human-review step by design, no per-archetype cost tracking) as an explicit called-out risk separate from the standard guardrail checklist — these are process/architecture gaps a config can't fix by itself, and burying them inside a generic guardrail list would let them go unnoticed.
5. **Draft the financial spend cap per archetype** — a per-run cap and a per-day cap. If the user gave a real budget number, use it. If not, state plainly that no number was given and that the drafted figure is a placeholder requiring human sign-off, never present an invented number as if it were derived from data.
6. **Enforce isolation explicitly in the output** — every archetype's bucket and cap are independent; state the fleet-wide aggregate cap as a separate, additional ceiling (not a shared pool each archetype draws from), matching the idea's core isolation guarantee. If some archetypes landed in "Needs more detail" and weren't tiered, the aggregate cap covers only the tiered archetypes — say so explicitly and note it must be revisited once the rest are tiered.
7. **List assumptions and open questions** that need a human's sign-off before this draft is wired into actual enforcement code (the library half of this idea, or any other middleware).

## Output format
Produce, in this order:

1. **Tier table** — one row per archetype: `Archetype | Tier | Why (action scope / reversibility / blast radius)`.
2. **Per-archetype config block**, in YAML, one block per archetype:
   ```yaml
   archetype: finance-ops-refunds
   tier: 4
   guardrails:
     - output_filter: pii_and_toxicity
     - input_validation: action_payload
     - human_approval: always
     - logging: full
   rate_limit:
     burst: <n>
     refill_per_minute: <n>
   spend_cap:
     per_run_usd: <n or "NEEDS INPUT">
     per_day_usd: <n or "NEEDS INPUT">
   ```
3. **Fleet-wide aggregate cap** — one line stating the sum of per-archetype caps plus a stated buffer, and a reminder that it is additional to, not a substitute for, per-archetype isolation. If any archetype wasn't tiered (see #4), say the cap covers only the tiered ones and must be revisited.
4. **Needs more detail** — a list of any archetype that couldn't be tiered, with the specific missing fact.
5. **Flagged risks** — any structural/process gap the user's own description revealed (no staging gate, no review step, no per-archetype cost tracking, a past incident) that this config draft can't fix by itself.
6. **Assumptions to confirm before enforcement** — every number or guardrail choice the skill estimated rather than derived from user-supplied data, each tagged `ASSUMPTION`.

## Guardrails
- Never invent a specific spend-cap or rate-limit number and present it as derived — every estimated figure must be visibly tagged `ASSUMPTION` in the output.
- Never tier an archetype from a vague description — ask for the missing action-scope/reversibility detail instead of guessing a risk level.
- Never draft a shared or pooled rate-limit/spend bucket across archetypes — isolation (one archetype can't borrow another's headroom) is the entire point of this idea; a pooled design defeats it.
- Never claim this draft is itself enforcement — always state explicitly that it is a config draft requiring review and wiring into real middleware (a hook adapter, a provider usage API check, etc.) before it does anything.
- Never fabricate a specific framework hook/API call (e.g. "set `crewai.task.budget_hook = ...`") unless the user confirmed that framework and you are stating it as a general wiring note, not verified working code.
