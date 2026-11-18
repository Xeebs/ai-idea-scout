---
name: hyperlocal-informal-economy-grounding-layer
description: Drafts a local-reporter recruitment plan, data schema, and freshness/abstention rules for a WhatsApp/SMS AI advisor that keeps giving stale or hallucinated answers on hyperlocal questions (market prices, service availability, local conditions) for an extreme-poverty or smallholder population. Use when a program team has an AI advisory bot live or in design and needs to close the "degrades sharply on hyperlocal questions" gap before building the actual grounding pipeline.
---

# Hyperlocal Grounding Plan for AI Advisory Bots

## When to use this
A team running (or about to launch) a WhatsApp/SMS AI advisor for cash-transfer recipients, smallholder farmers, or a similar extreme-poverty population notices — or anticipates — the advisor giving wrong, stale, or hallucinated answers to hyperlocal questions: "what's maize selling for at the Kigali market today," "is the agro-dealer in my village open," "has the health post run out of vaccines." This is the exact failure GiveDirectly's Rwanda pilot and Gramhal's Bolbhav chatbot both hit and patched ad hoc. Reach for this skill at the design or retrofit stage, before anyone writes code for a data pipeline — it produces the recruitment, schema, and integration plan a dev team then builds against.

## Inputs
**Data source**: Connected — this plan is designed around two already-mature, named connectors: the WhatsApp Business API (the transport layer already used by GiveDirectly's Turn.io/Proto pilot and Gramhal's Bolbhav) and Overture Maps / OpenStreetMap (a mature, public formal-business baseline layer). Neither needs to be built — they're assumed live. The informal-economy price/service-status data itself does **not** exist as a connector anywhere; this skill's output is the plan for collecting it, not a connection to an existing feed.

What the user hands over manually (paste or describe in the prompt):
1. **Target region and population** — e.g., "a single district in Eastern Province, Rwanda; ~800 cash-transfer recipients."
2. **Existing channel** — WhatsApp Business API, Turn.io, Twilio SMS, etc., and whether it's already live or still being built.
3. **The specific hyperlocal question categories the bot is failing (or expected to fail) on** — e.g., "maize and bean prices at the district market," "whether the nearest agro-dealer is open and stocked." List 2–5 concrete examples if the bot is already live; use target examples if pre-launch.
4. **Any existing human network the program already touches** — field officers, community health workers, vendor partners, local government contacts — who could plausibly become reporters. If none, say so explicitly.
5. **Current question volume/cadence** if known (messages/week, how often hyperlocal questions come up) — helps size the reporter network; optional but improves the plan.

## Procedure
1. **Restate the failure mode concretely.** Before designing anything, name the exact category of question the bot gets wrong and why (stale data, no data, formal-only baseline contradicting ground truth). If the user's input is vague, ask for 2–3 real or example failing questions before proceeding — a plan built on a vague failure mode is useless.
2. **Size the reporter network.** Using the target region/population size, propose a reporter count and role mix (e.g., "2–3 reporters per market/trading center, drawn from existing vendor partners or community health workers already in the program, not a brand-new recruitment channel unless none exists"). State the reasoning (coverage per physical market/service point, not per capita).
3. **Design the incentive structure as an explicit choice, not a default.** Present volunteer vs. small paid stipend vs. in-kind (e.g., program-eligibility credit) as named options with the tradeoff (volunteer = cheaper, higher attrition risk; paid = costs money, more reliable cadence). Recommend one given the inputs, and flag it as the single highest sustainability risk per the parent program's own experience.
4. **Draft the data schema.** For each question category from step 1, specify: the fields a reporter submits (e.g., `item`, `price`, `unit`, `location`, `reporter_id`, `timestamp`), the freshness-decay rule (e.g., "price data flagged stale after 48 hours; service-status data after 24 hours — tighter because availability changes faster than prices"), and the reconciliation rule when two reporters disagree (default: most-recent-timestamp wins for single-source fields; flag-for-review, don't average, when the delta exceeds a threshold — averaging silently can produce a number nobody actually reported).
5. **Specify the intake form for the user's stated channel.** Write the literal sequence of messages/prompts a reporter would see to submit a report (3–5 turns max — reporters are busy, this must be fast), and the reminder cadence (e.g., a daily prompt at a fixed time, not push-only). If the stated channel is WhatsApp Business API, you may use rich-form-style structured prompts. If it's plain SMS (no WhatsApp/smartphone access), the flow must shrink to fit SMS constraints — short fixed-keyword replies (e.g., "reply PRICE MAIZE 450"), no multi-field forms, no assumption of read receipts or buttons. Never default to WhatsApp-style flows when the user has stated SMS or another plain-text channel.
6. **Specify the integration hook.** Describe exactly where in the advisor's existing prompt pipeline the retrieval call happens (before generating any answer touching a hyperlocal category), and the literal abstention rule: if no report exists inside the freshness window for the asked item/location, the advisor must say so explicitly rather than falling back to general knowledge — write the actual fallback sentence template.
7. **Name the Overture Maps/OSM reconciliation step**, if the question category involves business/service status: the plan should flag contradictions between a fresh reporter claim and the formal map layer ("map says open, last report says closed 2 days ago") rather than silently picking one.
8. **Write the pilot validation plan.** One region, the specific goods/services from step 1, reporter count from step 2, and the single comparison: grounded vs. ungrounded answer accuracy against field-verified ground truth, run for 2–4 weeks minimum (long enough to catch a stale-data cycle).
9. **Surface the 2–3 biggest open risks** from the user's specific inputs (not generic risks) — reporter attrition, data governance/sensitivity of price data, and anything the user's own description suggests (e.g., single point of failure if only one reporter covers a market).

## Output format
A single markdown plan with these sections, in this order:
1. **Failure Mode** (1–2 sentences, concrete)
2. **Reporter Network Design** (count, roles, sourcing, incentive recommendation + tradeoff)
3. **Data Schema** (one subsection per question category: fields, freshness-decay window, reconciliation rule)
4. **Intake Flow for [stated channel]** (literal message sequence, adapted to WhatsApp/SMS/other as stated + reminder cadence)
5. **Advisor Integration Hook** (where the retrieval call sits in the pipeline + literal abstention fallback sentence)
6. **Formal-Layer Reconciliation** (only if applicable — Overture/OSM contradiction handling)
7. **Pilot Validation Plan** (region, scope, duration, success metric)
8. **Top Risks** (2–3 bullets, specific to this input, not generic)

## Guardrails
- Never fabricate an actual price, service status, or any ground-truth data point — this skill designs the collection system; it never substitutes for the data itself.
- Never recommend building new messaging infrastructure — WhatsApp Business API (or the user's stated existing channel) is already mature; the plan only adds the reporter/schema/freshness layer on top.
- Never omit the abstention rule — a plan that doesn't force the advisor to say "I don't have current data for that" when freshness fails has reproduced the exact hallucination failure this skill exists to close.
- Never recommend averaging conflicting reports as a default reconciliation rule — flag-for-review or most-recent-wins; a silent average can produce a number no reporter actually gave.
- Never treat reporter incentive design as solved by a one-line "pay them" — name the tradeoff explicitly, since this is the risk both source deployments (GiveDirectly, Gramhal) absorbed without a clean answer.
- Never scale the pilot plan beyond one region/5–10 items/10–20 reporters unless the user's inputs explicitly justify a larger scope — this is a pilot design aid, not a national rollout plan.
