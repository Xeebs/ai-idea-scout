---
name: team-shared-role-scoped-agent-pool
description: Turns a small team's fragmented per-employee AI agent setup (one seat per person) into a role-scoped agent pool design — a handful of agents, one per business function, each with its own memory and connector scope, handing work to each other instead of humans copy-pasting between chats. Use when a team lead or ops person is paying for N individual AI seats and wants a design for consolidating into shared role agents before building or configuring a runtime.
---

# Role Mesh Design Brief

## When to use this
Use this when someone running a small team (roughly 2–99 people) says something like: "everyone on my team has their own ChatGPT/Claude seat and we're all re-explaining the same context," or "two people gave a customer different answers because their agents don't share memory," or "we want to stop paying for one AI seat per employee and have a few shared agents instead." This is a one-shot planning exercise — it produces a design document, not a running system. It does not configure, provision, or connect to any live tool itself.

## Inputs
**Data source**: Connected — the design this skill produces names which of the team's *existing* per-tool connectors (CRM, accounting, support-desk APIs or MCP servers — e.g. Salesforce, HubSpot, QuickBooks, Xero, Zendesk) each role agent should read from; those connectors already exist maturely for mainstream SaaS today. For the design session itself, you provide a manual description (pasted text, not a live feed) of your team's current setup — this skill does not read your CRM/accounting/support tools directly, it only tells you which of your already-wired-up connectors each proposed role agent should use.

What to hand over:
1. **Team size and current AI setup** — how many people, which AI tool(s)/seats each person uses today.
2. **The functions/roles that actually exist** in the business (sales, finance, support, ops, delivery, etc.) — even an informal list.
3. **Known pain points**, ideally with a real example: duplicate or contradictory answers across people, a new hire with no access to prior context, a cross-role question nobody's agent could answer.
4. **Connectors/integrations already in place** — name the actual tools (e.g. "Salesforce via its MCP server," "QuickBooks," "Zendesk") and whether each is already live or just aspirational. If you don't know, say so — don't guess.

If any of 1–4 is missing, ask for it before producing a design. Do not invent team structure or connectors that weren't stated.

## Procedure
1. **Intake and gap-check.** Confirm team size, current per-person tool/seat list, stated roles, pain points, and named connectors. If a pain point was given without a concrete example, ask for one — vague complaints ("it's inefficient") don't map to a specific role or handoff.
2. **Cluster into roles, not people.** Group the team's current individual usage patterns into 3–6 functional roles based on what *data or decisions recur* across people, not org chart titles. Cap at 6 roles for teams under 20 people, 8 for larger teams — more than that defeats the point (the goal is fewer agents than people, not a 1:1 relabeling).
3. **Define each role's scope.** For every role, specify:
   - **Memory scope**: the specific facts/history this role agent owns (e.g., finance agent owns invoice and payment status; sales agent owns pipeline stage and deal notes).
   - **Tool/connector scope**: which *named* connector(s) feed it, and whether the user said it's already live or still needed. Never state a connector exists unless the user named it.
   - **Addressing**: who on the team is allowed to talk to this role agent (usually: anyone, but flag if a role should be restricted, e.g. finance for compliance reasons).
4. **Map handoffs.** For every pair of roles with a stated or implied recurring cross-role need, define a typed handoff: trigger event name, originating role, receiving role, payload fields (what data moves). Example: `deal.closed_won` — sales → finance — payload: {account, deal value, billing contact}.
5. **Flag ambiguous ownership.** Identify at least one case where role boundaries are genuinely fuzzy for this team (e.g., "who owns a customer that's both a renewal risk and a support escalation?") and assign an explicit human-arbitration fallback — never leave an ambiguous case unresolved in the design.
6. **Write a migration plan.** Phase the move from today's N per-person seats to the role pool: which 1–2 roles to pilot first (pick the ones with the clearest pain-point evidence from intake), what runs in parallel during the pilot, and a rollback trigger (what result would mean reverting to per-person seats).
7. **Define success metrics.** Produce 2–3 measurable metrics the team can actually baseline before switching: time for a team member to get a correct answer from the right role-agent on an off-their-desk question; count of duplicate/contradictory answers on the same factual question across different people's current agents; per-seat AI spend per employee before vs. after.
8. **Check for existing adjacent infrastructure.** If the user's named tools already include a multi-tenant/RBAC agent platform (e.g., CrewAI Enterprise, Microsoft 365 Copilot, OpenAI Workspace Agents), say so explicitly and recommend checking whether role-scoping can be configured there before building anything custom.

## Output format
A single markdown "Role Mesh Design Brief" with these sections, in this order:

1. **Role Roster** (table: Role | Memory Scope | Tool/Connector Scope (live or needed) | Who Can Address It)
2. **Handoff Map** (table: Trigger Event | From Role | To Role | Payload Fields)
3. **Ambiguous Ownership & Escalation** (table: Scenario | Default Owner | Human Fallback Trigger)
4. **Migration Plan** (Pilot scope: N roles, which ones, why → Parallel-run period → Rollback trigger)
5. **Success Metrics** (3 metrics, each with how to capture the baseline before switching)
6. **Existing Infra Check** (one line: either "no adjacent RBAC/tenancy platform named — custom build is the right call" or "you already have X — check its role/handoff features before building custom")

## Guardrails
- Never invent a connector, API, or tool the user didn't name. If a connector's maturity is unclear, write "verify with vendor," never assert it's ready.
- Never design more than 6 roles for a team under 20 people (8 for larger teams) — over-fragmentation defeats the consolidation this skill exists to produce.
- Never ship a design with zero ambiguous-ownership cases — real teams always have at least one fuzzy boundary; pretending otherwise produces a design that breaks on first contact with reality.
- Never recommend building a custom runtime without first checking for and naming adjacent RBAC/tenancy infrastructure the user already has.
- Never treat this as the runtime itself — this skill produces a design document only. Do not claim it connects to, provisions, or operates any live system.
- If team size or pain-point evidence is too thin to justify 3+ roles (e.g., a 3-person team), say so directly rather than forcing a role split that doesn't fit.
