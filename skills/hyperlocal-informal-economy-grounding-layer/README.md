# Hyperlocal Grounding Plan for AI Advisory Bots

Paste the prompt below into any AI chat tool (Claude, ChatGPT, Copilot, etc.) when you're running — or about to launch — a WhatsApp/SMS AI advisor for an extreme-poverty, cash-transfer, or smallholder-farmer population, and that advisor keeps giving stale, wrong, or hallucinated answers to hyperlocal questions ("what's maize selling for at the market today," "is the agro-dealer open," "has the clinic run out of a vaccine"). This is the exact failure GiveDirectly's Rwanda WhatsApp-AI pilot and India's Gramhal (Bolbhav chatbot) both hit after launch and had to patch ad hoc. This skill produces the plan — reporter recruitment, data schema, freshness rules, and the integration hook — that a dev team then builds against. It does not write code and it does not invent real price or service data.

## What this is built on (data sources)

This plan assumes two things are **already mature and don't need to be built**:
- **WhatsApp Business API** (or your stated SMS/chat channel) — the transport layer. Already the platform GiveDirectly's Turn.io/Proto pilot and Gramhal's Bolbhav run on.
- **Overture Maps / OpenStreetMap** — a public, mature formal-business baseline layer, used only to cross-check reporter claims about business/service status, not as the primary data source.

What does **not** exist anywhere as a ready-made feed: live informal-economy prices and service-status data at village/market granularity. That's the gap this plan closes — by designing the human reporter network and schema to collect it, not by connecting to something that already provides it.

## What you need to hand over

Paste or describe, directly in your message to the AI:

1. **Target region and population** — e.g., "a single district in Eastern Province, Rwanda; roughly 800 cash-transfer recipients."
2. **Existing channel** — WhatsApp Business API, Turn.io, Twilio SMS, etc., and whether it's live today or still being built.
3. **The specific hyperlocal question categories the bot gets wrong (or is expected to)** — 2–5 concrete examples. E.g., "maize and bean prices at the district market," "whether the nearest agro-dealer is open and stocked."
4. **Any existing human network the program already touches** — field officers, community health workers, vendor partners, local government contacts. Say explicitly if there's none yet.
5. **(Optional) Current question volume/cadence** — how often hyperlocal questions come up, if the bot is already live. Helps size the reporter network.

## The prompt

```
You are designing a local-reporter grounding plan for a WhatsApp/SMS AI
advisor serving [POPULATION] in [REGION]. The advisor currently gives
stale, wrong, or hallucinated answers on these hyperlocal question
categories: [LIST 2-5 EXAMPLES]. Our existing channel is [CHANNEL],
and our existing human network we could tap for reporters is [NETWORK,
or "none yet"].

Produce a plan with exactly these sections, in this order:

1. FAILURE MODE — restate the specific failure in 1-2 sentences.

2. REPORTER NETWORK DESIGN — propose a reporter count and role mix sized
   to the region (reason from coverage per physical market/service
   point, not per capita). Prefer recruiting from our existing network
   over a brand-new channel unless none exists. Present volunteer vs.
   paid-stipend vs. in-kind incentive as named options with tradeoffs,
   and recommend one, flagging it explicitly as a sustainability risk.

3. DATA SCHEMA — for each question category, specify: the fields a
   reporter submits, a freshness-decay window (how long before data
   is flagged stale — tighter for availability than for prices), and
   a reconciliation rule for conflicting reports from different
   reporters (default to most-recent-timestamp-wins or flag-for-review
   — never silently average).

4. INTAKE FLOW FOR [MY STATED CHANNEL] — write the literal 3-5 message
   sequence a reporter sees to submit one report, plus a reminder
   cadence. Adapt the flow to the channel I actually stated above: if
   it's WhatsApp Business API, structured form-style prompts are fine;
   if it's plain SMS or another basic-phone channel, shrink this to
   fixed-keyword short replies (e.g. "reply PRICE MAIZE 450") with no
   multi-field forms, buttons, or read receipts assumed.

5. ADVISOR INTEGRATION HOOK — describe exactly where in the advisor's
   answer pipeline the retrieval call happens, and write the literal
   fallback sentence the advisor uses when no report exists inside the
   freshness window (it must honestly say it lacks current local data
   rather than answering from general knowledge).

6. FORMAL-LAYER RECONCILIATION — only if a question category involves
   business/service status: how a contradiction between a fresh
   reporter claim and the formal map baseline (e.g. Overture Maps/OSM)
   gets flagged rather than silently resolved.

7. PILOT VALIDATION PLAN — one region, the specific items/services
   named above, a reporter count from section 2, a 2-4 week minimum
   duration, and the single comparison: grounded vs. ungrounded answer
   accuracy against field-verified ground truth.

8. TOP RISKS — 2-3 risks specific to the inputs given (not generic),
   including reporter attrition/incentive sustainability and any
   single-point-of-failure implied by the network size. If I said I
   have no existing field network, name the slower recruitment
   timeline as a risk rather than assuming a network already exists.

Rules: never invent an actual price or service-status value anywhere
in the plan. Never recommend building new messaging infrastructure —
assume the stated channel is mature. Never recommend averaging
conflicting reports as the default reconciliation rule. If my question
categories above are too vague to design a schema against, ask me for
2-3 concrete example questions before producing the plan.
```

## What you get back

A single markdown plan with the eight sections above, sized to a pilot (one region, 5–10 goods/services, 10–20 reporters) unless your inputs explicitly justify more. It is a design document for your dev/field team to build against — it does not connect to WhatsApp or Overture Maps itself, and it never fabricates the actual local data values.

## What this will not do

- It will not give you real current prices or service statuses — only the plan to start collecting them.
- It will not write the retrieval code or database schema migrations — it specifies the fields and rules; your dev team implements them.
- It will not solve reporter-incentive sustainability for you — it names the tradeoff and risk explicitly because this is unsolved even in the real deployments (GiveDirectly, Gramhal) this plan is modeled on.
