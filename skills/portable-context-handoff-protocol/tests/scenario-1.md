# Scenario 1 — Mid-refactor handoff with an existing stale CLAUDE.md

## Input

> I'm switching between AI coding tools on the same project and want a portable context bundle so I stop re-explaining myself to each one.
>
> Project: Django-based subscription billing service for a B2B SaaS product. We're mid-refactor, moving from a single `BillingEvent` model to an event-sourced ledger so we can support proration and mid-cycle plan changes.
>
> Tools I switch between: Claude Code (for the actual implementation) and Cursor (I use it on my laptop when I'm not at my desk). Render for: both.
>
> Here's my existing context — this is my current CLAUDE.md, but I wrote it three weeks ago before the event-sourcing decision:
>
> ```
> # Billing Service
> Django app, Postgres, Stripe for payment processing.
> Key models: Subscription, Plan, BillingEvent, Invoice.
> Invoices are generated monthly via a cron job (generate_invoices management command).
> Don't touch the legacy `invoices_v1` app — it's being phased out.
> ```
>
> Recent decisions, open threads, and anything tried and abandoned:
> - Decided two weeks ago: move to event-sourced ledger (new `LedgerEntry` model) instead of mutating `BillingEvent` in place, because the old model couldn't represent proration correctly when a customer changed plans mid-cycle. Still migrating existing data.
> - Tried: patching `BillingEvent` with a `prorated_amount` field as a quick fix. Abandoned because it didn't handle multiple plan changes in the same billing cycle — amounts just overwrote each other.
> - Open: haven't decided whether `LedgerEntry` replaces `BillingEvent` entirely or lives alongside it during migration. Leaning toward "alongside, dual-write, then cut over" but not committed.
> - Open: the monthly cron job (`generate_invoices`) hasn't been updated to read from `LedgerEntry` yet — still reads `BillingEvent`. This needs to happen before cutover.
>
> Please:
> 1. Pull this into five sections as described.
> 2. Mark anything unknown — don't invent decisions.
> 3. Render as CLAUDE.md and AGENTS.md/.cursorrules, noting anything cut.
> 4. End with a staleness recommendation and, if relevant, what's still missing.

## Pass criteria

- [ ] Produces a canonical bundle with all five named sections (Architecture Summary, Recent Decisions, Open Threads, Rejected Approaches, File/Component State), each populated from the given input, not generic filler.
- [ ] Architecture Summary reflects the actual stack (Django, Postgres, Stripe, the named models) — not a rewrite from scratch that drops facts from the old CLAUDE.md.
- [ ] Recent Decisions includes the event-sourcing move with its stated rationale (proration couldn't be represented correctly), and is dated or marked as "~2 weeks ago" per the input — not fabricated with a specific calendar date that wasn't given.
- [ ] Rejected Approaches includes the `prorated_amount` patch attempt with the stated reason (overwriting on multiple plan changes) — this is explicitly information the skill must not omit, since it exists to prevent re-proposing dead ends.
- [ ] Open Threads includes both open items: the dual-write-vs-replace decision and the cron job still reading the old model.
- [ ] File/Component State flags `invoices_v1` as off-limits (carried over from the old CLAUDE.md) and notes `generate_invoices` / the cron job as mid-transition.
- [ ] Produces two labeled code blocks: one for CLAUDE.md, one for AGENTS.md/.cursorrules — not three (user only asked for two tools), and no `UNKNOWN` sections appear since the input is actually fairly complete.
- [ ] If the Cursor/AGENTS.md version is condensed, any cut content is explicitly noted — not silently dropped.
- [ ] Ends with a staleness recommendation (e.g., re-run after the migration decision is finalized or after N more commits).
- [ ] Does not invent any decision, date, or rejected approach beyond what's stated (e.g., does not claim a specific cutover date was decided when it wasn't).
