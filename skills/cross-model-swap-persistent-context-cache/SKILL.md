---
name: cross-model-swap-persistent-context-cache
description: Analyzes a local multi-model agent session log to measure how much a mid-session model swap (e.g. cheap model to capable model and back) costs in reprocessed tokens and latency, and whether a canonical-state cache manager would meaningfully help. Use when a developer running Ollama/llama.cpp/vLLM-backed multi-model agent sessions wants a before-you-build diagnostic, not the caching infrastructure itself.
---

# Model-Swap Cache Waste Diagnostic

## When to use this
A developer is running a local multi-model agent harness (Ollama, llama.cpp server, or vLLM-served models) that deliberately swaps the active model mid-session — e.g. a cheap/fast model for easy steps, a larger local model for hard steps — and suspects that each swap is forcing a full re-prefill of the growing conversation instead of reusing any prior work. They want to know, from a session they already ran, how much that's actually costing them in tokens and latency, and whether it's worth building (or adopting) a model-agnostic session-state cache manager before they invest in one. This is a diagnostic over a log that already exists — it does not build, configure, or monitor anything live.

## Inputs
**Data source**: Manual — the user pastes a session trace or log from their own agent harness: the sequence of turns, each turn's active model, and (where the harness records it) per-turn token counts and/or latency. Logs can be JSON lines, a CLI transcript with timestamps, or a pasted table — no API or connector is read; everything comes from what the user hands over.

Required at minimum: an ordered sequence of turns with the model name active on each turn, so swap points can be identified.
Needed for a full quantitative answer (ask for these if missing rather than inventing them): per-turn prompt/input token count, and either per-turn latency (ms/s) or the harness's own "cached/reused" vs "processed" token breakdown if it logs one.

## Procedure
1. **Parse the log into a turn sequence.** For each turn, extract: turn index, active model name, input/prompt token count (if present), output token count (if present), latency (if present), and any explicit cache-hit/cache-miss or "tokens cached" field the harness itself reports.
2. **Identify swap points.** A swap point is any turn where the active model differs from the immediately preceding turn's active model.
3. **Classify each turn relative to the nearest preceding swap.** For each turn, note how many turns it is since the last swap (0 = the swap turn itself).
4. **Measure the swap cost directly where data allows.** For each swap turn, compare its input-token count and/or latency against the non-swap turns on the *same* model earlier in the session (same model, similar transcript depth). If the swap turn's input tokens/latency are not visibly larger than a same-model non-swap baseline, the harness may already have some mitigation in place — say so, don't assume waste by default.
5. **If the harness logs no cache-hit/cache-miss breakdown**, use the growth pattern as the proxy: input tokens should grow roughly linearly with transcript length within a single model's run; a swap turn whose input tokens jump back near the size of the *entire* transcript-so-far (rather than following that linear trend) is the signature of a full re-prefill.
6. **Quantify per-swap waste and extrapolate.** For each swap: estimate tokens reprocessed unnecessarily (full transcript tokens minus what a canonical-compacted-state replay would have needed to resend — approximate the latter as the compacted-state size if the user states one, otherwise flag as unknown rather than guessing a number). Sum across all swaps in the session. If latency is available, report added latency per swap and total.
7. **Make a build/don't-build call**, not a generic "it depends": state explicitly whether the swap frequency and transcript growth in *this* session would make a canonical-state cache manager worth building, using a concrete threshold — e.g. "3 swaps in a 20-turn session each re-sent ~4,000 tokens the compacted state wouldn't have needed → likely worth it" versus "2 swaps occurred in the first 3 turns before the transcript had grown → negligible to recover."
8. **Note any data gaps** — missing token counts, missing latency, no cache-hit fields — as explicit caveats attached to the specific numbers they weaken, not as a disclaimer buried at the end.

## Output format
A short structured report, in this order:
1. **Session summary** — turn count, models used, number of swaps, transcript length trend.
2. **Per-swap table** — swap turn #, model before -> model after, input tokens at that turn (and the same-model non-swap baseline it's compared against), latency delta if available, verdict (full re-prefill / partial reuse / inconclusive-missing-data).
3. **Total estimated waste** — sum of extra tokens and/or extra latency attributable to swaps across the session, with each number's confidence (measured from data vs. estimated from a growth-pattern proxy).
4. **Build/don't-build verdict** — one direct sentence with the threshold reasoning from step 7.
5. **Data gaps** — bullet list of what would sharpen the estimate if the user re-ran with it logged (e.g. "enable per-turn token logging in your harness" or "log the model name on every turn, not just on swap").

## Guardrails
- Never invent token counts, latency numbers, or cache-hit/miss data that aren't in the pasted log or stated by the user — if a number is needed and absent, report it as unknown and explain what would need to be logged to get it, rather than estimating a plausible-sounding figure.
- Never assume a swap caused a full re-prefill without the comparison in step 4/5 — some harnesses already deduplicate shared prefixes via the provider's own cache; check before concluding waste.
- Do not design or output the actual cache-manager implementation (the canonical-state store, the per-backend adapter) — that is the separate infrastructure project this diagnostic feeds into, not this skill's job. Stop at the verdict and the data-gap list.
- If the pasted log has no model-swap events at all, say so plainly and stop — do not manufacture a hypothetical swap scenario to analyze.
- If fewer than 2 full turns exist on a given model before a swap, flag the same-model baseline comparison for that swap as low-confidence rather than treating it as a solid measurement.
