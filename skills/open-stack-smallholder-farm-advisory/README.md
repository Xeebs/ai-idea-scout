# Open-Stack Farm-Advisory Architecture Auditor

Paste this into any AI chat tool (Claude, ChatGPT, Gemini, etc.) when you're building or already running an AI chatbot that gives farmers crop/agronomic advice, and you want a straight answer on how dependent it is on proprietary vendors and what to swap first.

## What this is for

Agricultural cooperatives, extension offices, and NGOs increasingly build "low-bandwidth" farm-advisory chatbots (usually over WhatsApp or SMS) to get crop and weather advice to smallholder farmers. Most of these still run on a proprietary cloud AI vendor underneath — a paid-per-query model API, a vendor-hosted database, sometimes a vendor-licensed knowledge base. That works, but it means unpredictable recurring cost, data-residency exposure, and dependency on a vendor's pricing and terms the org can't control.

This tool is a one-time audit: you describe your current (or planned) architecture, and it tells you exactly which parts are already open, which are proprietary-locked, and in what order to replace them with real, named, currently-existing open alternatives — not a vague "go open-source" suggestion.

**Data source: Manual.** You describe your own architecture in plain language or by answering the checklist below. This tool does not connect to any live API, deployment, or vendor account — it only reasons from what you tell it. (The full open-stack *deployment* this audit points you toward — an actual self-hosted model serving real farmer queries over WhatsApp with live weather data — is a separate, bigger build, not something this prompt does for you.)

## What to give it

Before asking for the audit, answer these six questions as completely as you can. If you don't know one, say so — the tool will ask you directly rather than guess.

1. **Model/provider** — what AI model answers farmer questions, and how do you access it? (e.g., "GPT-4 via OpenAI's API", "Gemini via Google Vertex AI", "we're not live yet, just deciding", "Llama 3 self-hosted on our own server")
2. **Knowledge base / corpus** — where does the agronomic knowledge come from? (a vendor's proprietary documents, a licensed dataset, or an open corpus such as CGIAR/CIMMYT crop-advisory data or FAO's GIEWS)
3. **Weather/agronomic data** — if the bot factors in rainfall, temperature, or soil conditions, what feeds that? (a paid commercial weather API, a free one like NASA POWER or Open-Meteo, or none)
4. **Farmer channel** — how do messages arrive and get answered? (WhatsApp Business Cloud API, Twilio SMS, a custom mobile app, USSD)
5. **Hosting** — who runs the actual inference — a managed cloud AI service you pay per query/token, or a server your org or cooperative controls?
6. **Data storage** — where do farmer questions and any personal data get stored, and under whose terms of service?

## The prompt

Paste the block below into your AI tool, filling in your own answers to the six questions above.

```
You are auditing a farm-advisory chatbot's architecture for proprietary vendor dependency. Here is my setup:

1. Model/provider: <your answer>
2. Knowledge base/corpus: <your answer>
3. Weather/agronomic data: <your answer>
4. Farmer channel: <your answer>
5. Hosting: <your answer>
6. Data storage: <your answer>

For each of these six components, classify it as:
- OPEN (open-weight/open-license AND self-hosted or org-controlled, no per-query vendor bill)
- HYBRID (open license or free tier, but still vendor-hosted or vendor-dependent for availability)
- PROPRIETARY-LOCKED (closed-weight/closed-license, metered vendor API, no open equivalent wired in)

For every component scored HYBRID or PROPRIETARY-LOCKED, name one specific, currently-real open alternative (a named model, named corpus, named API — not a vague "use open source"). Use this as your default reference set unless my specifics call for something better-fitting:
- Model: Gemma 2/3 (2B-9B) or Llama 3.x (8B class), quantized, served via Ollama or vLLM.
- Corpus: CGIAR/CIMMYT crop-advisory corpora, FAO GIEWS open data.
- Weather: NASA POWER API or Open-Meteo.
- Hosting: a rented GPU box, a co-op-funded server, or hardware the org already owns.

Then give me:
1. An Architecture Summary table (Component | Current setup | Classification).
2. An Open-Stack Score out of 6, with a one-sentence read on what it means.
3. A Prioritized Swap Plan — ordered by (cost/lock-in reduction) divided by (effort), highest first. Each entry: current -> named open alternative -> effort (Low/Medium/High) -> what it specifically removes (cost, lock-in, data-residency exposure).
4. A Honesty Caveat if you recommend a model swap: open-weight models in the 2-9B range can lag proprietary frontier models on nuanced agronomic reasoning for ambiguous cases, so recommend validating on a held-out set of real farmer questions (30-50, ideally from our own query logs) and running both paths side by side for a transition period rather than a hard cutover.
5. A Suggested Validation Step: a concrete small experiment comparing current vs. proposed stack on real questions, before I commit to the swap.

Do not recommend replacing everything at once. Do not invent benchmark numbers or cost figures you can't ground in what's publicly known. If I haven't given you enough information on any of the six components, ask me directly instead of guessing.
```

## What you'll get back

A short report: a six-row table scoring your current stack, an overall open-stack score, a ranked to-do list of swaps (easiest/highest-impact first — usually the knowledge-base corpus and weather API are quick wins, while the model and hosting swap is the bigger lift), a plain warning about where open models might still fall short on quality, and a concrete way to test that before you commit.

## What this will not do

- It will not build, deploy, or host anything — it's a diagnosis and a plan, not the running system.
- It will not tell you your WhatsApp channel itself is the problem unless it's bundled into a vendor contract that also forces your model/hosting choice — the farmer-facing channel is usually fine as-is.
- It will not claim an open-weight model is just as good as a frontier proprietary model without telling you to test that claim yourself first.
- It will not recommend tearing out your whole stack in one step.
