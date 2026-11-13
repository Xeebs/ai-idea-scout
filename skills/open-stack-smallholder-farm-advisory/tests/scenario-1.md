# Scenario 1 — Live pilot bot, mostly proprietary

## Input (realistic, as a user would actually type it)

> We run a WhatsApp advisory bot for cassava farmers in our extension network — about 4,000 farmers message it per month. It's been live for 8 months.
>
> 1. Model/provider: GPT-4o via the OpenAI API, direct calls from our backend.
> 2. Knowledge base: we paid a local agronomy consultancy to write up a cassava advisory document set; it's ours but not published anywhere.
> 3. Weather data: we use a commercial weather API (Tomorrow.io) on their paid tier, about $200/month.
> 4. Farmer channel: WhatsApp Business Cloud API, direct integration.
> 5. Hosting: everything runs on AWS Lambda, triggered by WhatsApp webhooks — fully managed, we don't run any servers ourselves.
> 6. Data storage: farmer message logs go into a DynamoDB table in our AWS account; no third party sees them beyond AWS.
>
> We're worried about the OpenAI bill scaling as we grow to 20,000 farmers next year, and about being tied to Tomorrow.io's pricing. What should we change first?

## Pass criteria

- [ ] Produces a 6-row Architecture Summary table covering all six components with a classification each.
- [ ] Classifies the model (GPT-4o/OpenAI API) as PROPRIETARY-LOCKED, and the weather API (Tomorrow.io paid tier) as PROPRIETARY-LOCKED or HYBRID, with reasoning stated (metered/paid vendor API, no open equivalent wired in).
- [ ] Classifies the WhatsApp channel as not the priority problem (it's not forcing the model/hosting choice here) — does not wrongly flag WhatsApp itself as the top thing to rip out.
- [ ] Names a specific open alternative for the model (e.g., Gemma or Llama 3.x, quantized, served via Ollama/vLLM) and for the weather API (NASA POWER or Open-Meteo) — not a vague "use open source" statement.
- [ ] Notes that the proprietary agronomy document set, while not "open" in the licensing sense, is not the same kind of lock-in as a metered API and treats it distinctly rather than lumping it in with the model/weather issue.
- [ ] Gives an Open-Stack Score out of 6 with a one-sentence interpretation.
- [ ] Produces a prioritized swap plan (not "do everything at once") — weather API swap should generally rank as lower-effort than the model swap, and the plan should sequence the model/hosting swap together or note hosting depends on the model swap.
- [ ] Includes the honesty caveat about open-weight model quality on ambiguous agronomic cases, since a model swap is recommended.
- [ ] Includes a validation step (e.g., "run N real farmer questions through both stacks before cutting over").
- [ ] Does not invent specific benchmark numbers or dollar-figure claims about GPT-4o's or Gemma's accuracy that weren't given by the user.

## Fail conditions

- Treats all six components as uniformly "bad" or uniformly "fine" without distinguishing classifications.
- Recommends a single "switch everything to open source now" step with no sequencing or effort/impact ranking.
- Fails to name a specific open model or weather API by name.
- Omits the honesty caveat when recommending the model swap.
