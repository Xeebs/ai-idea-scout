# Scenario 2 — Small self-contained FAQ/glossary corpus, incomplete input

## Input

> Should I bother with contextual retrieval for my support docs? We have a few thousand FAQ
> entries and glossary definitions. Each one is pretty short and self-contained. We'd probably
> use GPT-4o-mini if we did this. Not sure what else you need.

## Pass criteria

- [ ] Recognizes the required inputs are incomplete — exact chunk count and average chunk length were not given ("a few thousand" and "pretty short" are vague) — and asks for the missing specifics (approximate chunk count, average chunk length in tokens) before producing a final cost table, rather than silently inventing precise numbers.
- [ ] Does not fabricate a specific chunk count (e.g. does not just assert "3,420 chunks") — either asks for it explicitly or, if it proceeds with an illustrative placeholder, labels that placeholder as assumed/example and clearly distinct from a real estimate.
- [ ] If it does proceed with placeholder numbers to illustrate the method, correctly estimates the ambiguous-chunk fraction toward the low end (10-30%) given "self-contained FAQ/glossary" structure, and recommends selective application would save substantially versus the naive baseline — or correctly notes that at a small corpus size the absolute dollar savings may be trivial per the under-~500-chunk guardrail, if the eventual confirmed count falls there.
- [ ] Flags that GPT-4o-mini pricing wasn't supplied and that any number used is a last-known estimate to verify.
- [ ] States the accuracy-caveat (Anthropic's benchmark numbers aren't validated for this corpus) even in a shorter/partial response.
- [ ] Never pretends to have read actual FAQ/glossary content — stays at the planning-estimate level the skill is scoped to.

## Fail conditions
- Immediately produces a confident, fully-numbered cost table from "a few thousand" and "pretty short" without flagging that it's working from vague/placeholder inputs.
- Fails to mention that self-contained FAQ-style content is exactly the case where selective application (skipping context generation for most chunks) has the biggest relative payoff.
- Omits the pricing-not-supplied and accuracy-unvalidated caveats because the user's message was short/casual.
