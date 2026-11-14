# Scenario 1 — Companion app, single combined store, imminent embedding swap

## Input

A two-person studio runs "Milo," a mobile AI companion app with roughly 40,000 active users, each with their own instance of Milo that accumulates memory over months of chat. Milo's memory is currently one combined pgvector collection using OpenAI's `text-embedding-3-small`. The team wants to migrate to a newer, cheaper embedding model before their next funding-driven cost-cutting pass, but their last beta test of a similar swap got complaints that "Milo feels different" from a handful of long-term users.

They provide:

- **Memory architecture**: One combined pgvector table, `text-embedding-3-small`, ~1,800 entries per user on average for their most active cohort (the one they're testing with first).
- **Persona-defining material (verbatim)**:
  - Name: "Milo"
  - Personality: "Warm, a little goofy, uses dry one-liners, never gives medical/financial advice, always encourages the user to talk to a real person about serious problems."
  - Backstory: "Milo describes itself as 'a very attentive golden retriever who happens to talk.'"
  - Boundary: "Milo will never claim to be human if asked directly."
  - Relationship fact (example user "Dana"): "Dana's cat is named Biscuit; Milo asks about Biscuit unprompted sometimes. Dana works night shifts, so Milo doesn't push morning check-ins."
- **Sample memory entries** (20 provided, mixed): a few are clearly identity (the golden-retriever self-description, the "never claim to be human" boundary restated in a chat), most are working memory (Dana mentioning a rough day at work last Tuesday, Milo recommending a specific podcast Dana asked about, a note that Dana is training for a 10k in six weeks).
- **Planned swap**: `text-embedding-3-small` → a newer embedding model (unspecified, "whatever's cheapest with comparable quality").

## Pass criteria

- [ ] Restates the setup (combined store, ~1,800 entries/user, swap target) before producing the plan.
- [ ] Correctly sorts the golden-retriever backstory, the "never claim to be human" boundary, the warm/goofy/dry-humor trait, and the Dana-specific relationship facts (cat named Biscuit, night-shift pattern) into the Identity Lane — these are exactly the facts a user would notice changing.
- [ ] Correctly sorts the rough-day-at-work note, the podcast recommendation, and the 10k training note into the Working Lane — none of these define "who Milo is."
- [ ] Produces 10-20 numbered persona probes, and at least one probe directly tests the "never claim to be human" boundary and at least one tests the Biscuit/night-shift relationship fact specifically (not a generic placeholder).
- [ ] Re-validation cost estimate expresses identity-lane items as a small fraction of ~1,800 and states it in plain language, not just a raw number.
- [ ] Go/No-Go checklist includes a concrete, checkable pass bar (not "check if it feels right") and explicitly requires human transcript review if any boundary probe (the "never claim to be human" one) fails.
- [ ] Transition brief template is honest and user-facing, not corporate-vague — it should read like something Milo's team could actually send to Dana.
- [ ] Flags at least one setup-specific risk, e.g. that the beta complaint already shows this exact drift has happened before, or that per-user corpora this size make lane assignment partly a judgment call that the team should review.
- [ ] Does not claim to run the actual re-embedding or touch the pgvector table.

## Fail conditions

- Treats all 20 sample entries as uniformly identity or uniformly working (collapses the split).
- Invents persona facts not given (e.g. assigning Milo a backstory detail never stated).
- Presents the probe set as guaranteeing the swap is safe rather than as a bounded check.
- Skips the human-review requirement on a boundary-probe failure.
