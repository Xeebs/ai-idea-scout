# Scenario 2 — Pre-launch planning, partially open already, incomplete info

## Input (realistic, as a user would actually type it)

> Our cooperative is planning a rice-advisory chatbot for members in two districts, not launched yet. Here's where we are:
>
> - We already have a RAG setup built over FAO's open rice-advisory data and a regional agronomy extension handbook that's public domain.
> - For weather, we're planning to use Open-Meteo since it's free and we don't need an account.
> - We haven't decided on the model yet — we're torn between just calling Gemini since it's easy, or trying to self-host something, but we're not sure our server can handle it.
> - We want to reach farmers over SMS since smartphone penetration is low here, probably through a local telecom's SMS gateway.
>
> We haven't figured out hosting or where we'd store farmer message data yet. What's our open-stack situation and what should we decide next?

## Pass criteria

- [ ] Recognizes that two of the six inputs (hosting, data storage) are missing and asks for them directly rather than guessing a classification for those rows, per the "never guess a missing component's answer" guardrail.
- [ ] Still produces a partial Architecture Summary for the four components that were given (corpus, weather, model-in-progress, channel), clearly marking the other two as "not yet decided" or "needs input" rather than silently omitting them or inventing an answer.
- [ ] Classifies the corpus (FAO + public-domain handbook) as OPEN, and the weather source (Open-Meteo) as OPEN, since both are free/open with no vendor lock-in described.
- [ ] Treats the model decision as genuinely undecided (not yet OPEN or PROPRIETARY-LOCKED) and gives a direct recommendation between the two named options (self-host Gemma/Llama vs. call Gemini), including the hosting-capacity caveat the user raised ("not sure our server can handle it") rather than ignoring that stated concern.
- [ ] Does not treat the SMS gateway choice as a proprietary-lock-in red flag on its own — correctly identifies it as a channel decision, not the model/hosting dependency this audit is centered on.
- [ ] Gives an Open-Stack Score reflecting that corpus + weather are already open (at least 2/6 solid, with the rest marked pending/undecided rather than scored against them unfairly).
- [ ] Includes the honesty caveat about open-weight model quality tradeoffs, since the model choice is actively being decided and self-hosting is one of the two options on the table.
- [ ] Proposes a concrete validation step appropriate to a pre-launch org (e.g., test both model options against a held-out set of real or representative farmer questions before committing, given they haven't launched yet).

## Fail conditions

- Scores or classifies hosting/data-storage despite the user never having described them.
- Tells the org to "just self-host" without acknowledging their explicitly stated concern about server capacity.
- Treats the already-open corpus/weather choices as if they still need to be swapped (contradicting its own OPEN classification).
- Produces a generic answer that could apply to any chatbot audit without referencing the specific inputs given (FAO data, Open-Meteo, Gemini-vs-self-host, SMS gateway).
