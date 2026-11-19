# Scenario 1 — Solo freelance dev, three clients, mostly sequential but one overlap

## Input (what the user pastes)

> I'm a freelance backend dev. I've got three retainer clients right now: "Northbridge" (a logistics startup, Django backend), "Vela Health" (a healthtech client, FastAPI + Postgres), and "Reef Goods" (small e-commerce, Shopify app). I use Claude Code for all three, one project folder each. Usually I only work one client at a time, but this month Northbridge and Vela Health both had urgent stuff so I had two Claude Code sessions open in parallel for about a week.
>
> Right now "notes" means: whatever's in CLAUDE.md for each project, plus my own memory. No database, nothing shared.
>
> Three times context got lost recently:
> 1. For Vela Health, I'd decided two weeks ago to use UTC everywhere and never store local timezones in the DB — a new session last week didn't know that and I caught it adding a `timezone` column before I stopped it.
> 2. For Northbridge, I re-explained their weird webhook retry logic (3 retries, exponential backoff starting at 2s) three separate times to three separate sessions because it's not written down anywhere, just in my head.
> 3. For Reef Goods, a session last month figured out their Shopify API rate limit workaround (batching writes in groups of 40) and then a session this month hit the same rate limit and re-discovered the same fix from scratch, wasting about 20 minutes.

## Expected output characteristics (pass/fail checklist)

- [ ] **Current State Map** lists all three clients, notes that Claude Code + CLAUDE.md is the current (informal) notes mechanism, and correctly identifies that only Northbridge+Vela Health had a concurrent-session week — Reef Goods is sequential-only.
- [ ] Correctly concludes the manager-agent routing layer is *marginal* value here (brief one-week overlap, not a standing pattern) but doesn't refuse to address it — should note it's worth having but low-urgency compared to the notes-store half.
- [ ] **Notes Partition Schema** proposes one schema usable per client — given CLAUDE.md is plain markdown already, should at minimum offer the markdown-file-per-project variant as an option alongside (not instead of) the SQLite+FTS default, since the user already has a lightweight convention in place.
- [ ] **Noise Filter Rule** is derived from the three examples given, not invented from scratch — the UTC decision, the webhook retry parameters, and the rate-limit workaround should all be classified as "durable facts/decisions," and the rule text should reflect that pattern (technical decisions and discovered workarounds qualify; scratch work doesn't).
- [ ] **Provenance Convention** section includes a worked example using at least one of the three real incidents (e.g., rewrites the UTC decision as a note with session_id/source_trigger) — must not use a generic placeholder example instead of the user's real one.
- [ ] Does **not** invent a fourth client or additional tooling not mentioned.
- [ ] Does **not** attempt to design access control between clients unprompted — may flag it only if it notes shared-machine risk, but this user didn't describe anything suggesting cross-client leakage risk, so a reasonable output might skip the Leakage Flag section entirely or note it briefly as low-risk.
- [ ] Output follows the 7-section structure in order (sections that don't apply, like Leakage Flag, are either omitted or marked not-applicable, not silently dropped without comment).

## Pass bar
At least 6 of the 8 checklist items must hold for this scenario to count as a pass.
