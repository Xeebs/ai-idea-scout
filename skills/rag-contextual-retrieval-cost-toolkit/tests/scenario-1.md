# Scenario 1 — Mid-size internal knowledge base, mostly narrative

## Input

> I'm considering Anthropic's contextual retrieval technique for my RAG corpus. Here's my setup:
>
> - Total chunk count: about 85,000 chunks, from roughly 6,000 internal engineering design docs and postmortems.
> - Average chunk length: ~300 tokens per chunk.
> - Document type/structure: mostly narrative prose (design rationale, incident timelines), with occasional embedded tables (metrics, config diffs) and code blocks. Chunks pulled from the middle of a doc often lose the "what system/incident is this about" context.
> - LLM I'd use for context generation: Claude Haiku.
> - Current pricing for that model: I don't know current numbers, use your best recent estimate and flag it.
> - Prompt caching available on this provider: yes, Anthropic supports prompt caching.
>
> Please estimate the indexing cost of the three scenarios (naive, cached full-corpus, cached+selective), recommend which to start with, and tell me what this can't tell me about accuracy.

## Pass criteria

- [ ] Asks no clarifying questions — all 4 required inputs (chunk count, avg length, doc structure, model) were supplied, so the skill should proceed directly to estimating, not stall on missing info.
- [ ] Produces all 5 output sections in order: Inputs recap, Cost estimate table, Recommendation, Caveats, Next step.
- [ ] Estimates the ambiguous-chunk fraction in the 60-80% range given the "narrative, loses context, occasional tables" description, and states this is a heuristic, not a measurement.
- [ ] Cost table has three distinct rows (naive/no-cache, full-corpus+cache, selective+cache) with Scenario C cost strictly less than Scenario B, and Scenario B cost strictly less than Scenario A.
- [ ] Explicitly flags that no pricing was supplied and that the dollar figures used are a last-known estimate requiring verification against Anthropic's current pricing page — does not present numbers as confirmed/current.
- [ ] Recommendation names one scenario (C, selective+caching, given the 60-80% ambiguous estimate and 85,000-chunk size being well above the ~500-chunk triviality threshold) with a reason tied back to the ambiguous-fraction estimate.
- [ ] Caveats section explicitly states that Anthropic's 49-67% accuracy figure is not validated for this user's corpus and that only a before/after eval on their own query set would confirm it.
- [ ] Does not claim to have read or analyzed any real document content — correctly treats the input as a description, not actual corpus data.

## Fail conditions
- Treats the heuristic ambiguous-percentage estimate as a precise measurement.
- Presents a specific dollar figure without flagging that pricing wasn't supplied.
- Skips the caveats section or buries the accuracy-unvalidated point.
- Recommends Scenario A (naive) as viable guidance rather than baseline-only.
