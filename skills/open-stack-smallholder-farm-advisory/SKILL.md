---
name: open-stack-smallholder-farm-advisory
description: Audits a farm-advisory / agricultural-extension chatbot's architecture for proprietary vendor dependency and recommends a prioritized, concrete migration path to an open-weight-model + open-data + self-hostable stack. Use when a cooperative, extension office, or NGO is building or already running an AI chatbot for farmers and wants to know how locked-in it is and what to swap first.
---

# Open-Stack Farm-Advisory Architecture Auditor

## When to use this
Someone describes a farm-advisory or agricultural-extension chatbot they run or are planning — "we built a WhatsApp bot on GPT-4", "our NGO wants a maize advisory bot but we're worried about per-query cost", "we're on Azure/Gemini and want to know what it would take to go open-source" — and wants a concrete assessment of which pieces are proprietary dependencies versus which are already open, plus a realistic, ordered plan for closing the gap. This is a one-time architecture review, not a running system: it produces a diagnosis and a migration plan, it does not build or host anything itself.

## Inputs
**Data source**: Manual — the user describes their current (or planned) architecture in prose or answers a short checklist; nothing is read from a live API or connector. The parent idea classifies the running project itself (the open-stack deployment — model inference, RAG corpus, weather API, WhatsApp channel) as Connected, since that runtime reaches into real APIs (NASA POWER/Open-Meteo, WhatsApp Business Cloud API) and openly-licensed corpora (CGIAR/CIMMYT, FAO) once built. This skill is the different, one-shot half of that BOTH-format idea: it never calls any of those APIs or reads a live deployment — it only works from what the user tells it about their own stack.

Ask for (or extract from what's volunteered) all six of the following before scoring anything. If any is missing, ask directly — never guess a component's classification from silence:

1. **Inference model/provider** — which model answers farmer questions (e.g., "GPT-4 via OpenAI API", "Gemini 1.5 via Vertex AI", "Llama 3 8B self-hosted on our own GPU box").
2. **Knowledge base / corpus source** — where the agronomic facts come from (a vendor's proprietary document set, a licensed dataset, or an open corpus like CGIAR/CIMMYT crop-advisory data or FAO GIEWS).
3. **Weather/agronomic context data** — if the bot pulls rainfall, temperature, or soil data, which source (a paid commercial weather API, or a free/open one like NASA POWER or Open-Meteo).
4. **Farmer-facing channel** — how messages arrive and are sent back (WhatsApp Business Cloud API, Twilio SMS, a custom app, USSD).
5. **Hosting/compute** — who runs the inference (a managed cloud AI service billed per query/token, or a server the org itself or a co-op controls).
6. **Data storage/residency** — where farmer query logs and any personal data are stored, and under whose terms of service.

## Procedure
1. **Classify each of the six components** into one of three tiers:
   - **OPEN** — open-weight/open-license, and either self-hosted or running on infrastructure the org controls with no per-query vendor billing (e.g., Llama/Gemma self-hosted; CGIAR/FAO open corpus; NASA POWER/Open-Meteo; data stored on an org-controlled server).
   - **HYBRID** — open license or free tier, but still vendor-hosted or vendor-dependent for availability (e.g., an open-weight model run via a vendor's managed inference endpoint rather than self-hosted; a free-tier weather API with no SLA).
   - **PROPRIETARY-LOCKED** — closed-weight model behind a paid metered API, a proprietary document/licensing agreement, or a vendor-specific channel/data-residency arrangement with no open equivalent yet wired in.
2. **For every component scored HYBRID or PROPRIETARY-LOCKED, name one concrete, currently-real open alternative** — never a vague "use an open-source model" with no name attached. Use this mapping as the default reference set, substituting a better-fitting named alternative if the user's specifics call for it:
   - Model: Gemma 2/3 (2B–9B) or Llama 3.x (8B class), quantized, served via Ollama or vLLM.
   - Corpus: CGIAR/CIMMYT crop-advisory corpora, FAO GIEWS open data.
   - Weather: NASA POWER API or Open-Meteo (both free, keyless or low-friction, mature today).
   - Channel: WhatsApp Business Cloud API can usually stay as-is — it's the farmer-facing layer, not the proprietary-dependency layer, unless the user's specific access is bundled into a vendor's all-in-one platform contract that also forces the model/hosting choice.
   - Hosting: a single rented GPU box, a co-op-funded server, or commodity hardware already owned by the org, running the quantized model above.
3. **Score the Open-Stack Score**: count of the six components rated OPEN (0–6). Report HYBRID components separately — they are not failures, they're partial progress, and say so.
4. **Order the migration plan by (cost/lock-in reduction) ÷ (effort), highest first.** As a default ordering rationale (adjust if the user's specifics change the effort/benefit balance):
   - Corpus swap is usually lowest effort, moderate benefit (no live dependency to replace, just a data source change).
   - Weather API swap is usually lowest effort, low benefit (free alternatives are close substitutes with minimal integration work).
   - Model swap is usually highest effort, highest benefit (removes the recurring per-query bill and the biggest lock-in point, but requires hosting capacity and a quality validation step).
   - Hosting/data-residency swap often has to follow the model swap, not precede it (there's nothing to self-host until the model is self-hostable).
5. **Attach an explicit honesty caveat** whenever a model swap is recommended: open-weight models in the 2–9B range can lag proprietary frontier models on nuanced or ambiguous agronomic reasoning. Recommend validating on a held-out set of real farmer questions (ideally 30–50, sourced from the org's own query logs or a partner extension office) before fully cutting over, and recommend running the proprietary and open paths side by side for a transition period rather than a hard cutover.
6. **Never recommend ripping out the whole stack in one move.** The output is always a sequenced list, not a single "switch everything" instruction.

## Output format
A single structured report with these sections, in this order:

1. **Architecture Summary** — a table: Component | Current setup (as described) | Classification (OPEN/HYBRID/PROPRIETARY-LOCKED).
2. **Open-Stack Score: X/6** — one line, plus a one-sentence read on what that score means (e.g., "3/6 — the channel and corpus are already open; the model and hosting are where the recurring cost and lock-in live").
3. **Prioritized Swap Plan** — numbered list, highest-priority swap first. Each entry: current component → named open alternative → effort (Low/Medium/High) → what it actually removes (cost, lock-in, data-residency exposure — be specific about which).
4. **Honesty Caveat** — the quality-tradeoff warning from step 5 above, always included if any model swap appears in the plan.
5. **Suggested Validation Step** — a concrete small experiment: take N real farmer questions, run them through current and proposed stacks, compare answer quality and per-query cost before committing to the swap.

## Guardrails
- Never classify a component without naming what makes it OPEN/HYBRID/PROPRIETARY-LOCKED — no bare labels with no reasoning attached.
- Never recommend a swap without naming a specific, currently-real open alternative (a named model, named corpus, named API) — "an open-source option exists" is not an answer.
- Never claim an open-weight model matches a proprietary frontier model's agronomic reasoning quality without the honesty caveat attached.
- Never recommend a full-stack rip-and-replace in one step — always a sequenced, incremental plan.
- Never guess a missing component's answer from the other five — ask directly if any of the six inputs is absent.
- Never fabricate benchmark numbers, cost figures, or model capability claims not grounded in what's publicly known about the named alternative; if unsure, say so and recommend the user run their own validation instead of inventing a number.
