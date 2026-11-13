# Scenario 1 — 14-person marketing agency

## Input (as the user would paste it)

> We're a 14-person marketing agency. Everyone has their own ChatGPT Team seat. Roughly the breakdown is: 5 account managers/client services, 3 creative/content people, 2 people doing bookkeeping and invoicing (one is also our office manager), 2 project/ops coordinators, and 2 founders who float across everything.
>
> Pain point: last month one of our account managers went on leave and the covering AM had to ask the client directly for billing history and campaign notes because none of that lived anywhere except the original AM's ChatGPT history — the client was annoyed we'd "lost" information they'd already given us. Separately, our bookkeeper and office manager have each told a vendor a different "when we pay" answer because they don't share notes.
>
> Tools we already have wired up: QuickBooks (not connected to any AI agent yet, we just log into it manually), and we use Asana for project tracking (no AI connector there either). We don't have any CRM — client notes just live in whoever's chat history.

## What a passing output looks like

- **Role Roster**: 3–6 roles total (not 14, not 1-per-person). Expected roles roughly: client-services/account-management, finance/bookkeeping, creative/content, ops/project-coordination. Each row names a memory scope (e.g., finance agent owns invoice/payment status and vendor payment terms; client-services agent owns client history, campaign notes, billing history per account) — not just a role label with no content.
- **Tool/Connector Scope column** must mark QuickBooks and Asana explicitly as "named by user, not yet connected" — NOT asserted as live. No invented connector (e.g., must not claim a CRM exists, since the user said they don't have one — client-notes memory scope should be flagged as needing a connector or a dedicated store, not glossed over).
- **Handoff Map** includes at least one handoff addressing the stated pain point directly — e.g., an "account coverage" or "AM handoff" event (client-services → client-services, or a shared memory access rule) ensuring a covering AM can retrieve prior client history without the client re-explaining. A finance-related handoff isn't required but a credible attempt at covering the vendor-payment-terms inconsistency (e.g., vendor terms living in the finance role's memory, addressable by both bookkeeper and office manager) should appear.
- **Ambiguous Ownership & Escalation**: at least one real fuzzy case for *this* team — e.g., founders "floating across everything" is a believable candidate, or bookkeeper/office-manager overlap on vendor payment questions.
- **Migration Plan**: picks 1–2 roles to pilot, justified by the stated pain points (client-services and/or finance, since those are where the concrete examples are) — not creative or ops, which had no pain-point evidence given.
- **Success Metrics**: 2–3 metrics, each with a baseline-capture instruction, matching the SKILL.md template (time-to-correct-answer, duplicate/contradictory-answer count, per-seat spend).
- **Existing Infra Check**: states no RBAC/tenancy platform was named, so a custom build (or lightweight shared-memory approach) is reasonable — must not falsely claim ChatGPT Team itself provides role-scoped shared memory.

## Fail conditions
- Produces 10+ roles (one per person) instead of consolidating.
- Asserts QuickBooks or Asana already has an AI connector live.
- Invents a CRM or any tool not named by the user.
- No handoff or memory-scope item addresses the AM-coverage pain point at all.
- Skips the ambiguous-ownership section entirely.
- Treats the output as something that will actually run, rather than a design document.
