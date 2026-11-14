# Multi-Agent Archetype Fleet Governance Config Drafter

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then describe your agent fleet below the line. The assistant will draft a per-archetype governance-tier configuration — not run anything, not connect to anything, just produce a reviewable draft.

## When this is useful

You're running, or about to run, more than one distinct *type* of AI agent in production — for example a customer-support agent, a code-review agent, and a finance-ops agent that can issue refunds. Right now you either have no tiering at all (every agent gets the same blanket policy) or you're hand-rolling a tier scheme yourself. This is also useful right after an incident — a runaway agent, an agent that took an action it shouldn't have — when you want to retrofit tiers quickly.

This produces a **design draft only**. It does not enforce anything by itself. Someone still has to wire the resulting config into real enforcement (a hook into your agent framework's own dispatch/callback system, or a middleware layer, or at minimum a human process).

## What to hand over (data source: manual)

Nothing here is read automatically from any system — you type or paste this in plain language. For each agent archetype in your fleet, give:

1. **Name/role** — e.g. "customer-support agent," "finance-ops agent."
2. **What it's allowed to do, concretely** — not "handles support," but "reads tickets and drafts replies" or "can issue refunds up to $200" or "can merge PRs to the main branch."
3. **How reversible its actions are** — does a human review before anything actually happens, or does it act and the action sticks (money moves, code ships, an email goes out)?

Optional but it sharpens the draft:
- Expected call volume / concurrency per archetype.
- Any existing budget number (daily or monthly spend target) per archetype — if you have real numbers from your LLM provider's usage/billing dashboard, paste them instead of letting the draft guess.
- Which agent framework(s) you're using (CrewAI, LangGraph, AutoGen, Claude Code subagents, something else, or none yet).
- Any incident history ("it looped and sent 400 replies before anyone caught it").

## Instructions for the assistant

When given a description of a multi-agent fleet's archetypes, do the following:

**Step 1 — Classify each archetype on three axes**: action scope (what it can touch), reversibility (can a human undo it, or does it take effect immediately and permanently), and blast radius (how much damage one bad run could do).

**Step 2 — Assign a tier**, 1 through 4:
- **Tier 1 (Read/Advisory)**: only reads or drafts; nothing takes effect without a human sending or approving it.
- **Tier 2 (Reversible action)**: acts autonomously but the action is cheap to undo (tagging a ticket, posting an internal note, opening a draft PR).
- **Tier 3 (Costly/hard-to-reverse)**: acts autonomously and the action is expensive or slow to undo (sending a customer email, closing a ticket, merging to a non-protected branch).
- **Tier 4 (Financial/irreversible)**: moves money, merges to production, or does anything that can't practically be undone.

If a description doesn't give enough detail to place an archetype confidently, don't guess — list it separately under "Needs more detail" with the exact missing fact (e.g. "is the refund auto-sent, or queued for human approval?").

**Step 3 — Draft a guardrail profile per tier**, scaling strictness up with tier — don't give every archetype the same checklist:
- Tier 1: output filtering only (PII/toxicity check on drafts).
- Tier 2: output filtering + input validation on the action payload.
- Tier 3: output filtering + input validation + a human-approval gate above a stated threshold.
- Tier 4: all of Tier 3, plus mandatory human approval on every single invocation (no auto-approve threshold) and full action logging.

**Step 4 — Draft a token-bucket rate limit per archetype**: a burst capacity and a steady-state refill rate (calls per minute), scaled to whatever call-volume info was given. If no volume info was given, propose a clearly-labeled starting assumption rather than presenting a made-up number as fact. If the user mentioned a past incident (a loop, a duplicate action, a near-miss), visibly reference it in your reasoning and tighten the burst capacity and/or add a dedup/idempotency check accordingly — don't mention an incident and then ignore it.

**Step 4a — Flag structural gaps**: if the user's own description reveals a process/architecture gap (no staging environment, no human-review step by design, no per-archetype cost tracking), call it out explicitly as a separate flagged risk — these are things a config can't fix by itself, so don't bury them inside the guardrail checklist.

**Step 5 — Draft a financial spend cap per archetype**: a per-run cap and a per-day cap. Use a real number if the user gave one. If not, say explicitly that none was given and mark the figure as a placeholder needing sign-off — never present an invented number as if it came from data.

**Step 6 — Make isolation explicit**: each archetype's rate-limit bucket and spend cap must be independent — one archetype running hot can never borrow headroom from another's. State a fleet-wide aggregate cap as an *additional* ceiling on top of (not a replacement for, and not a shared pool across) the per-archetype caps. If some archetypes landed in "Needs more detail" and weren't tiered yet, say the aggregate cap covers only the ones that were tiered, and flag that it needs revisiting once the rest are.

**Step 7 — List every assumption** that needs a human's sign-off before anyone wires this into real enforcement.

## Output format

Produce, in this exact order:

1. A **tier table**: one row per archetype — Archetype | Tier | Why (the reversibility/blast-radius reasoning).
2. A **YAML config block per archetype**, in this shape:
   ```yaml
   archetype: finance-ops-refunds
   tier: 4
   guardrails:
     - output_filter: pii_and_toxicity
     - input_validation: action_payload
     - human_approval: always
     - logging: full
   rate_limit:
     burst: 5
     refill_per_minute: 1
   spend_cap:
     per_run_usd: 200
     per_day_usd: 2000
   ```
3. One line stating the **fleet-wide aggregate cap** (sum of per-archetype caps plus a stated buffer), noting it is additional to per-archetype isolation, not a substitute for it, and scoped only to archetypes actually tiered.
4. A **"Needs more detail"** list for any archetype that couldn't be confidently tiered.
5. A **"Flagged risks"** list for any structural/process gap the description revealed (no staging gate, no review step, no cost tracking, a past incident) that this draft can't fix by itself.
6. An **"Assumptions to confirm before enforcement"** list — every estimated number or guardrail choice, each one tagged `ASSUMPTION`.

## Hard rules (never break these)

- Never present an estimated spend cap or rate limit as if it were derived from real data — tag every estimate `ASSUMPTION`.
- Never tier an archetype on a vague description — ask for the missing fact instead of guessing.
- Never draft a shared or pooled bucket/cap across archetypes — isolation is the entire point; a pooled design defeats it.
- Never imply this draft is itself enforcement — it is a config draft that still needs to be reviewed and wired into real middleware (a framework hook, a provider usage-API check, or at minimum a human-run process).
- Never write a specific framework API call (e.g. a literal CrewAI or LangGraph hook function) as if it were verified working code unless the user confirmed that exact framework and version — otherwise phrase it as a general wiring note, not a code snippet to copy-paste blindly.

---
*Below this line, describe your agent fleet's archetypes and their risk profiles.*
