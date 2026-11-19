# GroundLine: A Crowd-Sourced Informal-Economy Grounding Layer for Extreme-Poverty AI Advisors

- **Status**: PUBLISHED (promoted cycle 151 — evidence density: GiveDirectly/Rwanda WhatsApp pilot and Gramhal/India Bolbhav Plus are 2 independent threads, different orgs/countries, both naming the same local-grounding/data-freshness gap)
- **Date**: 2026-11-18
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-18-applied-ai-for-underserved-domains.md · P1
- **Maturity verdict**: PARTIAL — GiveDirectly's Rwanda WhatsApp pilot and Gramhal's Bolbhav rebuild both named the same local-grounding/data-freshness failure and patched it ad hoc after the fact; no reusable "plug in your region's informal-economy data" layer exists (gh search and WebSearch found only formal-places-only grounding like Overture Maps, one paper-stage crop-specific MCP architecture, and a research proposal — not a shipped, swappable layer).
- **Format**: BOTH
- **Data Sources**: CONNECTED — a purpose-built regional data feed aggregated from (a) WhatsApp Business API submissions from a paid or volunteer network of local "price reporters" (vendors, agro-dealers, community health workers already in the program), and (b) Overture Maps/OpenStreetMap as a formal-business baseline layer that the informal-economy feed overlays and corrects. No existing API already covers informal-economy prices/service-status at this granularity — the WhatsApp Business API itself is a mature, widely-used platform (already the transport layer in the GiveDirectly and Gramhal deployments cited below); this project builds the missing aggregation/freshness layer on top of it, not the messaging channel itself.

## The Gap
GiveDirectly's own EA Forum write-up of its Rwanda pilot (832 recipients, 21,000 WhatsApp messages, Nov 2025–Apr 2026) states plainly: "the more rural the setting, the less useful the AI's answers about local markets, services, and conditions." India's Gramhal had to rebuild its chatbot into "Bolbhav Plus" after farmers complained market-price data was three days stale. Both teams solved it with a bespoke, one-off patch; neither shipped anything another deployment could reuse.

## The Project
A swappable grounding middleware that sits between a general-purpose LLM and any WhatsApp/SMS advisory bot serving extreme-poverty or smallholder populations. It ingests structured, timestamped reports from a lightweight local-reporter network (a simple WhatsApp form: "maize price at Kigali market today = X"), stores them with explicit freshness/decay metadata, and exposes a retrieval API the advisor's prompt pipeline calls before answering any hyperlocal question — falling back honestly to "I don't have current local data for that" rather than hallucinating a stale or generic answer. A companion module reconciles reports against the Overture Maps formal-business layer to catch contradictions (a shop reported "closed" that the map still lists as open).

## Tangible Impact
**Population**: The cash-transfer and agricultural-advisory populations already being handed general-purpose AI advisors as a program feature — GiveDirectly's Rwanda WhatsApp-AI pilot cohort (832 recipients, scaling inside an organization that has delivered cash to 2+ million people since 2009, per givedirectly.org) and smallholder farmers using chatbots like Gramhal's Bolbhav in India.
**Mechanism**: Instead of an advisor confidently answering a market-price or service-availability question from a model's stale or absent training data, it either returns a sourced, dated local figure or honestly abstains — closing the exact "degrades sharply on hyperlocal questions" failure both source programs documented.
**Measure**: Local-question answer accuracy against ground-truth price/service checks (target: match the field audit used by Gramhal's own evaluation); abstention rate on questions with no fresh local data (should rise, not fall, vs. the baseline bot); median data staleness at time of query (target: under 48 hours, down from Gramhal's reported 3 days).

## Why Now
Two independent, well-documented 2025–2026 deployments (GiveDirectly's Turn.io/Proto pilot, Gramhal's Bolbhav rebuild) just proved the failure mode and the duct-tape fix at real scale, and WhatsApp Business API + Overture Maps give a mature, already-adopted transport and baseline-data layer to build the missing freshness/aggregation piece on top of, with no new infrastructure invention required.

## Skill Angle
A companion skill takes a program's deployment plan (target region, population, existing channel) and drafts a concrete local-reporter recruitment and data-schema plan — which roles to recruit as reporters, what fields to collect, what cadence closes the specific staleness gap GiveDirectly and Gramhal both hit — before the team builds or wires up the grounding layer itself.

## MVP Sketch
One region (e.g., a single Rwandan district or Indian block), one data type (market prices for 5–10 staple goods), a WhatsApp-form intake bot for 10–20 volunteer reporters, a Postgres store with freshness decay, and a retrieval function the existing advisor's prompt calls. The single experiment: does grounded local-price accuracy beat the un-grounded baseline bot on a held-out set of real recipient questions, measured against field-verified prices.

## Risks & Open Questions
- Reporter-network incentive design (volunteer vs. paid) is unsolved and could collapse data quality if under-resourced — this is the same sustainability risk GiveDirectly and Gramhal each absorbed internally.
- Overlapping/conflicting reports from multiple local reporters need a reconciliation rule; a naive average could be worse than one trusted source.
- Risk this is "already solved internally" at GiveDirectly/Gramhal but just never open-sourced — worth a direct outreach check before building from scratch.
- Informal-economy data can itself be politically sensitive (price manipulation accusations); governance/dispute-handling needs design, not just engineering.
