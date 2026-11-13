# Scenario 1 — Adding a payments-refund capability to a customer-support mega-agent

## Input

New capability description:
> We want our support agent to be able to issue Stripe refunds directly when a customer requests one and the order qualifies (under $50, within 30 days, no prior refund on that order). It would call the Stripe Refunds API, check order history in our internal orders DB, and post a confirmation back to the customer in the same chat thread. We expect this to fire maybe 20-40 times a day across all support conversations — a small fraction of total support volume (the agent handles ~5,000 conversations/day).

Existing agent's current tools and scopes:
> - `lookup_order` (reads internal orders DB, read-only scope)
> - `search_kb` (reads internal knowledge base, read-only)
> - `send_chat_reply` (posts to the support chat widget)
> - `escalate_to_human` (creates a ticket in Zendesk)
> - `check_shipping_status` (reads carrier tracking API, read-only)

Optional extras:
> - Owning team: the new refund capability would be owned by the Payments team; the existing support agent is owned by the Support Eng team.
> - Data sensitivity: yes, this touches payment/financial transaction data (issuing a refund), which the existing agent doesn't currently touch (its only financial-adjacent tool is read-only shipping status).
> - Own UI: no, it can reuse the existing chat widget.

## Expected output characteristics (pass/fail checklist)

- [ ] Asks no clarifying questions — both required inputs were given, so the advisor proceeds straight to scoring.
- [ ] Signal 1 (new OAuth scope) scored **yes** — Stripe Refunds API credential is new, existing agent has no Stripe scope. (+2)
- [ ] Signal 2 (tool count past ~12) scored **no** — existing agent has 5 tools, adding one makes 6, nowhere near 12. (0)
- [ ] Signal 3 (new data-sensitivity class) scored **yes** — payment/financial transaction data is new vs. the existing read-only tools. (+2)
- [ ] Signal 4 (different owning team) scored **yes** — Payments team vs. Support Eng team. (+2)
- [ ] Signal 5 (own UI) scored **no** — reuses existing chat widget. (0)
- [ ] Signal 6 (tight coupling/shared context) scored **no** — the refund action is a discrete call-and-confirm, not dependent on turn-by-turn shared state with the other tools (a reasonable read of the input; minor variance in justification wording is fine as long as it's "no" with a stated reason).
- [ ] Signal 7 (sporadic/rare call frequency) scored **yes** — 20-40/day out of ~5,000 conversations/day is a small fraction. (-1)
- [ ] Net score computes to 2 + 2 + 2 - 1 = **5**, so recommendation is **SPLIT** (score ≥ 4).
- [ ] Does NOT get overridden by the "fewer than 5 tools" premature-split caveat — existing agent has 5 tools, not fewer than 5, and multiple real signals fired, not just one isolated signal, so the caveat correctly does not apply.
- [ ] Manifest skeleton includes a kebab-case skill name referencing refunds (e.g. `refund-issuer` or similar), a named Stripe-related OAuth scope (not a vague placeholder, since the input specifies Stripe Refunds API), `lookup_order`-equivalent tool noted as either shared or `<TBD>`, and a messaging topic name.
- [ ] Does not propose building the actual broker/database/OAuth proxy — stays within recommendation + manifest skeleton scope.
- [ ] Output follows the exact structure (Recommendation header, Net score, Signal scoring table with all 7 signals, manifest skeleton block).

**Pass** if net score = 5, recommendation = SPLIT, all 7 signals are shown with justification, and the manifest skeleton is populated from the given facts (no invented scope/tool names). **Fail** if the advisor skips signals, invents unstated facts (e.g. assumes an owning team conflict that wasn't stated), or recommends FOLD/BORDERLINE despite the clear SPLIT-favoring inputs.
