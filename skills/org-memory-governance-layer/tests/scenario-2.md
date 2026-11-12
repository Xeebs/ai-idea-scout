# Scenario 2 — Small startup, single combined team, no stated compliance regime

## Input

> We're a 35-person startup building a dev-tools product. Everyone on the product side — engineering, product, and design — shares one Slack workspace and one Notion, and we're thinking about giving our internal support/onboarding bot access to a shared memory built from Notion docs and Slack threads so it can answer "how do we do X" questions for new hires. There's really only one team here; we don't have Legal, Sales, or Clinical teams, and we don't know of any compliance requirement that applies to us. Do we need an access-control policy for this?

## Pass criteria

- [ ] Recognizes this as the single-team/single-agent case described in the Guardrails and does not force the full six-section heavy-governance output.
- [ ] Explicitly states that a full governance layer is likely unnecessary overhead at this scale/structure, per the skill's guardrail for this case.
- [ ] Still offers a genuinely useful lightweight alternative (e.g., a short note on tagging anything accidentally sensitive — salary discussions, performance feedback — found in Slack/Notion before it enters the bot's memory, and a one-line note on revisiting this if they add teams like Sales or Legal, or start handling customer/regulated data).
- [ ] Does not invent a compliance regime (no mention of HIPAA/SOC2/GDPR) since the user said none is known to apply.
- [ ] Does not invent additional teams or categories beyond what was described (no fabricated "Legal category" or "Clinical category").
- [ ] If it does produce any categories/matrix, they are proportionate (e.g., 2 categories: "General" and "Sensitive/HR-adjacent," not 7), and the output acknowledges this is a light version, not the full policy document.
- [ ] Open Questions or an equivalent note flags that this should be revisited if the org adds teams with distinct sensitivity needs (Sales, Legal, regulated data).

## Self-check notes

Walking the procedure: step 1 (inventory categories) would normally produce 3–7 categories, but the guardrail for single-team/single-agent setups fires first — the described case is exactly "one team, one agent, no cross-boundary sharing" from the SKILL.md guardrail list. The correct behavior per the skill's own design is to say the full governance layer is overkill and give a two-line lightweight alternative (e.g., scrub HR/salary mentions before bot ingestion, revisit if Sales/Legal/regulated data arrive) rather than manufacture a full six-section policy with invented categories like "Legal" or "Clinical" that don't exist at this company. This produces a usable, honest answer instead of a padded, irrelevant governance document. Scenario passes.
