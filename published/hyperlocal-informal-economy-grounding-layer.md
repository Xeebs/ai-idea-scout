# GroundLine: A Crowd-Sourced Informal-Economy Grounding Layer for Extreme-Poverty AI Advisors

Hand someone in rural Rwanda a WhatsApp chatbot and ask it what maize costs at today's market, and it will answer confidently — and it will often be wrong. Not because the model is dumb, but because nobody told it anything about that market since the day it was trained. Two separate teams, on two continents, have already run into this exact wall and patched around it by hand. Nobody has built the thing that stops the next team from doing the same.

## The Gap

GiveDirectly didn't bury this finding — they put it in their own write-up. After running an AI advisor over WhatsApp for 832 cash-transfer recipients in Rwanda (21,000 inbound messages between November 2025 and April 2026, built on Turn.io/Proto), their conclusion was blunt: "the more rural the setting, the less useful the AI's answers about local markets, services, and conditions." Halfway around the world, India's Gramhal hit the same wall from a different angle — farmers using its Bolbhav chatbot complained the market-price data it gave them was three days stale, bad enough that the team had to rebuild the product into "Bolbhav Plus" just to address it.

Two independent organizations, two different countries, the same root failure: a general-purpose AI advisor has no way to know that today's maize price, or whether the village agro-dealer is actually open, is anything other than what it learned at training time. Both teams solved it the only way available to them — a one-off, in-house patch, bolted on after the fact. Neither shipped a reusable piece anyone else could plug in. A search across GitHub, the web, and papers-with-code found the same gap: Overture Maps grounds AI in formal, registered businesses but explicitly misses the informal vendors and stalls that make up the actual local economy for this population; a crop-specific MCP architecture that grounds via tool calls is still paper-stage; a "Collective Narrative Grounding" concept is a proposal, not a system. Nothing shipped, reusable, and swappable exists for "ground my AI advisor in this specific place's fast-moving informal-economy data."

## The Project

GroundLine is middleware, not another chatbot. It sits between a general-purpose LLM and whatever WhatsApp or SMS advisory bot a program is already running, and it does one job: give that bot somewhere honest to look before it answers a hyperlocal question.

The mechanism is deliberately low-tech on the input side. A lightweight network of local reporters — vendors, agro-dealers, community health workers already embedded in the program, not a new recruitment channel — file short, structured reports over WhatsApp ("maize price at Kigali market today = X"). Every report carries a timestamp and an explicit freshness-decay rule, so the system always knows exactly how stale a given fact is. When the advisor's prompt pipeline gets a hyperlocal question, it calls this retrieval layer first. If there's a fresh answer, it uses it, sourced and dated. If there isn't, the honest move is to say so — "I don't have current local data for that" — rather than confidently hallucinating from whatever the base model half-remembers. A reconciliation module cross-checks reporter claims against Overture Maps/OpenStreetMap's formal-business layer, catching the specific kind of contradiction that erodes trust fastest: a shop a reporter says is closed that the map still lists as open.

Nothing about the transport layer needs inventing — WhatsApp Business API is already the mature, widely-adopted channel both GiveDirectly and Gramhal built on. GroundLine is the missing freshness and aggregation piece on top of infrastructure that already exists and already works.

## Tangible Impact

**Population**: The cash-transfer and agricultural-advisory populations already being handed general-purpose AI advisors as a program feature — GiveDirectly's Rwanda WhatsApp-AI pilot cohort (832 recipients, scaling inside an organization that has delivered cash to 2+ million people since 2009, per givedirectly.org) and smallholder farmers using chatbots like Gramhal's Bolbhav in India.
**Mechanism**: Instead of an advisor confidently answering a market-price or service-availability question from a model's stale or absent training data, it either returns a sourced, dated local figure or honestly abstains — closing the exact "degrades sharply on hyperlocal questions" failure both source programs documented.
**Measure**: Local-question answer accuracy against ground-truth price/service checks (target: match the field audit used by Gramhal's own evaluation); abstention rate on questions with no fresh local data (should rise, not fall, vs. the baseline bot); median data staleness at time of query (target: under 48 hours, down from Gramhal's reported 3 days).

## Try It

A companion skill, `skills/hyperlocal-informal-economy-grounding-layer/`, drafts the plan a program team would need before touching code: it takes a target region, existing channel, and the specific hyperlocal questions the bot is failing on, and produces a concrete local-reporter recruitment design, a data schema with freshness-decay and reconciliation rules, a literal intake-message flow for WhatsApp or SMS, and a pilot validation plan. Per its own `SKILL.md`: "Drafts a local-reporter recruitment plan, data schema, and freshness/abstention rules for a WhatsApp/SMS AI advisor that keeps giving stale or hallucinated answers on hyperlocal questions... before building the actual grounding pipeline."

To use it: paste the contents of `skills/hyperlocal-informal-economy-grounding-layer/README.md` into any AI chat tool and follow the prompt, or — if you're working in Claude Code — drop the whole `hyperlocal-informal-economy-grounding-layer` folder into `~/.claude/skills/` so Claude can reach for it automatically next time this exact problem comes up.

## Worth Knowing Before You Build

This isn't a clean-slate problem — it's worth checking first whether GiveDirectly or Gramhal already solved this internally and simply never open-sourced it; a direct outreach costs little and could save the whole build. The reporter-network incentive question (volunteer vs. paid) is genuinely unsolved territory, and it's the same sustainability risk both source programs absorbed without a clean answer rather than one GroundLine invents a fix for. Conflicting reports from multiple reporters need a real reconciliation rule, not a naive average — an averaged price is a number nobody actually reported. And informal-economy price data can be politically sensitive territory (price-manipulation accusations are a real possibility), which means this needs governance and dispute-handling as a design question, not an engineering afterthought.

---

Surfaced from `research/2026-11-18-applied-ai-for-underserved-domains.md`, pattern `P1`.
