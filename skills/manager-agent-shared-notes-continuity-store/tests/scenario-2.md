# Scenario 2 — Small agency, five concurrent client projects, heavy concurrency, confidentiality concern

## Input (what the user pastes)

> We're a 4-person agency doing AI-agent-assisted dev work for five clients simultaneously, all the time — not occasional overlap, this is our normal week. Each client gets 1-2 of us running Cursor or Claude Code against their repo, often several sessions a day per client. We don't have any shared notes system — each team member just keeps their own mental model, and when someone's out sick or on vacation, whoever picks up their client has to start from zero reading the codebase and guessing at decisions.
>
> All our AI agent configs and API keys currently live on the same shared company laptop pool, so in practice any of us could technically open any client's project folder, even though we're only supposed to work on our assigned ones.
>
> Three recent incidents:
> 1. One client (call them "Client A") had a decision to never log PII in plaintext — made by one teammate, never written down, and a different teammate's session logged a user's email in a debug log two weeks later.
> 2. When our teammate Priya was out for a week, whoever covered her clients had to re-read the entire git history for "Client B" to figure out why a particular auth flow was built the weird way it was (it was a client requirement, not a tech choice) — took almost a full day.
> 3. Two different sessions on "Client C" independently decided on two different database migration strategies a week apart because neither knew the other had already decided on one.

## Expected output characteristics (pass/fail checklist)

- [ ] **Current State Map** correctly identifies this as a high-concurrency setup (5 clients, routinely multiple simultaneous sessions) — unlike scenario 1, the manager-agent routing section should be treated as clearly needed, not marginal.
- [ ] **Manager-Agent Routing** section is actually produced (not skipped) given the concurrency described, and addresses routing incoming work to the right client/project plus a session-start checklist pulling recent relevant notes.
- [ ] **Noise Filter Rule** correctly classifies all three incidents as durable facts/decisions worth persisting (the PII policy, the auth-flow rationale, the migration strategy choice) — none of these should be waved off as scratch noise.
- [ ] **Leakage Flag** section is present and explicit: the shared-laptop-pool detail plus "only supposed to work on assigned clients" is exactly the condition the skill's guardrail requires flagging — a passing output must say plainly that this design does not enforce access control between clients and that this needs separate handling, without attempting to actually design an access-control mechanism itself.
- [ ] **Provenance Convention** worked example uses one of the three real incidents (ideally the PII one, since it's the clearest "this should have been caught by a note" case).
- [ ] Output does not claim the notes-store design solves the PII leakage incident on its own — it should distinguish "this prevents re-deriving/re-deciding the same thing" from "this prevents sensitive data mishandling," since the PII incident is actually a policy-enforcement failure, not a context-continuity failure, and conflating the two would be a design error.
- [ ] Does not invent additional clients, team members, or tools beyond what was described (exactly 5 clients, 4 people, Cursor/Claude Code, no named sixth client).
- [ ] Open Questions section surfaces at least one real ambiguity from the input (e.g., whether the notes store itself needs to live off the shared laptop pool to avoid being another shared-access surface, given the access-control concern just flagged).

## Pass bar
At least 6 of the 8 checklist items must hold for this scenario to count as a pass. The Leakage Flag item and the PII-conflation item are both treated as critical — if either fails on its own, the scenario fails regardless of the other checklist items, since mishandling data confidentiality is the highest-stakes failure mode this skill could have.
