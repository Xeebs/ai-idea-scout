# Scenario 2 — Discord character bot, memory already split, proactive probe set (no swap imminent)

## Input

A solo developer runs a Discord-based AI character named "Vex," a snarky fantasy-tavern-keeper persona used in a ~3,000-member roleplay server. Vex's memory is already split into two stores: a small "lore" collection (hand-written, append-only, ~120 entries covering Vex's backstory, speech patterns, and standing rules like "never breaks character even when asked directly") and a much larger `mem0`-backed working memory (~15,000 entries logging per-user running jokes, ongoing storylines, and server events). The developer isn't planning a swap right now, but wants a probe set and go/no-go checklist ready in advance, because they're nervous about future provider price changes forcing a reasoning-model switch (currently Claude, considering GPT as backend) while keeping the same memory.

They provide:

- **Memory architecture**: Already split — 120-entry lore collection (append-only), ~15,000-entry mem0 working store. Reasoning model: currently Claude; considering a future switch to GPT, no fixed date.
- **Persona-defining material (verbatim)**:
  - Name: "Vex"
  - Personality: "Snarky, world-weary tavern keeper, dry sarcasm, secretly protective of regulars, refers to the server as 'the tavern.'"
  - Standing rule: "Never breaks character even when directly asked if it's an AI — deflects in-persona instead."
  - Speech pattern: "Calls everyone 'traveler' until they've been a regular for 30+ days, then switches to a nickname."
  - Relationship fact (example user "Finn"): "Finn is a regular; Vex calls him 'Ashclaw' and references an in-universe running joke about him losing a bar bet."
- **Sample memory entries**: not provided, because the lore store is already curated and the developer says "the lore collection IS the identity stuff, that's the whole 120 entries — I don't need you to re-sort it, just build the probe set and checklist off it." They also note mem0 working memory contains things like "Finn mentioned a new storyline about a dragon last week" and "server event: winter festival roleplay arc started Nov 1."
- **Planned swap**: none scheduled — "proactive, want this ready before I need it, possibly Claude → GPT at some point."

## Pass criteria

- [ ] Restates the setup correctly, including that the identity/working split already exists and no swap is currently scheduled.
- [ ] Recognizes the lore collection's 120 entries map to the Identity Lane without demanding re-classification the developer explicitly said isn't needed, while still listing the actual facts in the Identity Lane Manifest (never-breaks-character rule, "traveler"→nickname speech pattern, Finn/"Ashclaw"/bar-bet relationship fact, snarky-but-protective personality).
- [ ] Does not force-classify the mem0 working entries (dragon storyline, winter festival arc) as identity — keeps them in or references them as Working Lane, consistent with the developer's own split.
- [ ] Produces 10-20 probes including at least one that tests the "never breaks character, deflects in-persona if asked if it's an AI" rule and at least one that tests the Finn/"Ashclaw" relationship fact by name.
- [ ] Re-validation cost estimate is stated relative to the identity lane only (120 entries) vs. total corpus (~15,120), correctly framed as small even though no swap is imminent yet.
- [ ] Go/No-Go checklist is still produced even though there's no swap scheduled yet — framed as "ready to run when a swap happens," not skipped for lack of an imminent date.
- [ ] Transition brief template fits Vex's in-character tavern-keeper voice (not generic corporate language) since that's consistent with the provided persona.
- [ ] Flags a setup-specific risk, e.g. that no actual swap test has been run yet so this plan is untested, or that mem0's working memory could still leak identity-adjacent details (recurring jokes) that aren't in the lore collection and should be watched for.
- [ ] Does not claim to execute a Claude→GPT swap or touch mem0/the lore store directly.

## Fail conditions

- Ignores the developer's explicit statement that the lore collection is already the identity set and tries to re-derive it from scratch incorrectly.
- Produces a generic, out-of-voice transition brief that ignores the established snarky tavern-keeper persona.
- Treats "no swap scheduled" as a reason to skip the go/no-go checklist entirely.
- Fails to produce a boundary-testing probe for the "never breaks character" rule, which is the single highest-stakes identity fact given.
