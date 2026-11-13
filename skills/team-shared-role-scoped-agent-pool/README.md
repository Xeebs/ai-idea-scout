# Role Mesh Design Brief

A paste-into-any-AI-chat-tool prompt that takes a small team's fragmented, one-AI-seat-per-employee setup and designs a shared, role-scoped agent pool to replace it: a small set of agents — one per business function — each with its own memory and connector scope, handing work to each other instead of humans copy-pasting context between separate chat windows.

## When to use this

Use this when you're running or advising a small team (roughly 2–99 people) and any of these are true:
- Everyone has their own AI chat seat and keeps re-explaining the same institutional context.
- Two people's agents have given a customer, client, or each other contradictory answers because neither agent shares the other's memory.
- You're paying for N individual AI subscriptions and suspect you could consolidate into a handful of shared agents.
- You want a design for this *before* building or buying a runtime — this produces the design, not the running system.

This is a one-shot planning exercise. It does not connect to your CRM, accounting system, or support desk — it tells you, on paper, which of your *already-existing* connections each proposed role agent should use.

## What you need to provide

**Data source for this exercise: Manual.** You paste a plain description — this tool does not read any of your live systems. But the design it produces is meant to plug into **Connected** data: your team's existing CRM, accounting, and support-desk APIs or MCP connectors (e.g. Salesforce, HubSpot, QuickBooks, Xero, Zendesk) — these already exist and are mature for mainstream SaaS tools today, so the design will name which one feeds which role rather than assuming anything new needs to be built on that front.

Give the assistant, in plain text:

1. **Team size and current AI setup** — how many people, and which AI tool(s)/seats each person (or role) currently uses.
2. **The actual functions in your business** — even informally: e.g. "sales, bookkeeping, customer support, delivery/ops."
3. **A real pain-point example** — not "it's inefficient" but something concrete: "our new account manager had to ask the client's whole history again because it only lived in the old AM's chat," or "a support rep told a customer refunds take 3 days and another rep said 7."
4. **The tools/connectors you already have wired up** — name them (e.g. "Salesforce, connected via its MCP server," "QuickBooks, not yet connected to any agent," "Zendesk"). Say clearly which are live today vs. aspirational. If you don't know, say so.

If you leave any of these out, the assistant should ask before producing a design — a design built on guesses about your team isn't usable.

## The procedure to follow

1. **Confirm the intake.** Make sure team size, current tools, stated roles, and at least one concrete pain-point example are in hand. Ask for anything missing, especially a real example if the pain point given is vague.
2. **Cluster into 3–6 roles** (up to 8 for teams over ~50 people) based on what data or decisions recur across people — not a 1:1 relabeling of job titles. Fewer agents than people is the whole point; don't exceed the cap.
3. **For each role, specify three things**: what it remembers (memory scope — the specific facts/history it owns), what it connects to (tool/connector scope — only connectors the user actually named, marked live or needed), and who on the team can address it.
4. **Map the handoffs.** For every pair of roles with a recurring cross-role need, write a typed handoff: an event name, the role that triggers it, the role that receives it, and what data moves in the payload. Example: `deal.closed_won` from Sales to Finance, carrying account name, deal value, and billing contact.
5. **Call out at least one ambiguous ownership case** specific to this team (a scenario where it's genuinely unclear which role owns something) and give it an explicit human-fallback rule. A design with zero fuzzy edges is a design that hasn't been thought through.
6. **Write a migration plan.** Pick 1–2 roles to pilot first — the ones with the clearest pain-point evidence — define what keeps running in parallel during the pilot, and state a rollback trigger (what outcome means reverting to per-person seats).
7. **Define 2–3 measurable success metrics**, each with a note on how to capture the "before" baseline: time to get a correct answer from the right role-agent on a question outside your own usual work; count of duplicate/contradictory answers on the same factual question today; per-seat AI spend per employee before vs. after.
8. **Check for existing infrastructure.** If the connectors or tools named already include a multi-tenant/RBAC agent platform (CrewAI Enterprise, Microsoft 365 Copilot, OpenAI Workspace Agents, etc.), say so and suggest checking whether that platform can already do role-scoping before building anything custom.

## Output you should get back

A single document, "Role Mesh Design Brief," with these sections in order:

1. **Role Roster** — table of Role / Memory Scope / Tool & Connector Scope (live or needed) / Who Can Address It
2. **Handoff Map** — table of Trigger Event / From Role / To Role / Payload Fields
3. **Ambiguous Ownership & Escalation** — table of Scenario / Default Owner / Human Fallback Trigger
4. **Migration Plan** — pilot scope and why, parallel-run period, rollback trigger
5. **Success Metrics** — 3 metrics with baseline-capture instructions
6. **Existing Infra Check** — one line stating whether you already have adjacent RBAC/tenancy infrastructure worth checking first

## Guardrails — what this should never do

- Never invent a connector or tool you didn't name. Unclear maturity gets marked "verify with vendor," never asserted as ready.
- Never produce more than 6 roles for a team under 20 people (8 for larger teams).
- Never hand back a design with no ambiguous-ownership case — every real team has at least one fuzzy boundary.
- Never skip the existing-infrastructure check if you named a platform that already does RBAC/tenancy.
- Never present this as a working system — it's a design document, nothing here connects to or operates any live tool.
- If your team is too small or the pain-point evidence too thin to justify 3+ real roles, the assistant should say so rather than forcing an artificial split.
