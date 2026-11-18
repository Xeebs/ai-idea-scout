# Model-Swap Cache Waste Diagnostic

A self-contained prompt template for diagnosing whether swapping models mid-session in a local multi-model agent setup (Ollama, llama.cpp server, vLLM, or similar) is quietly costing you full context re-prefills — before you spend time building any caching fix for it. Paste the block below into any AI chat tool along with your session log.

## When to use this

You're running an agent loop that deliberately switches the active model partway through a session — for example, a small/fast model for easy steps and a larger, more capable local model for hard steps — and you suspect every swap forces the new model to reprocess the entire conversation from scratch instead of reusing anything. You have a log or transcript from a session where at least one swap happened, and you want a concrete answer: how much is this costing, and is it worth building a fix.

This is a **diagnostic over a log you already have.** It does not build, configure, or monitor any live caching system — it tells you whether that's worth doing next.

## What to hand over

This skill works entirely from what you paste — nothing is read from any API or connector.

Paste your session log or trace. At minimum it needs, per turn: which model was active. For a real quantitative answer (strongly recommended), also include whatever your harness logs per turn: input/prompt token count, output token count, latency, and/or any "tokens cached" or cache-hit/miss field the harness itself reports. JSON lines, a plain CLI transcript with timestamps, or a pasted table are all fine — just keep turns in order.

If your log is missing token counts or latency, say so when you paste it — the analysis will still run on model-swap structure alone, but the output will flag which numbers it can't produce and tell you exactly what to turn on in your harness's logging to get them next time.

## What happens when you run this

1. **Parse the log into an ordered turn sequence** — turn number, active model, and whatever token/latency/cache fields are present.
2. **Find every swap point** — any turn where the active model differs from the previous turn's model.
3. **Classify every turn by distance from the nearest prior swap**, so swap-turn numbers can be compared against steady-state turns on the same model.
4. **Compare each swap turn against a same-model, non-swap baseline** earlier in the session (same model, similar transcript depth). If the swap turn isn't visibly more expensive than that baseline, the harness may already be mitigating the cost — the report says so rather than assuming the worst.
5. **If no explicit cache-hit/miss data exists**, use the growth-pattern proxy: input tokens normally grow roughly linearly with transcript length within one model's run; a swap turn whose input tokens jump back up near the *entire* transcript size (instead of following that linear trend) is the signature of a full re-prefill.
6. **Quantify waste per swap and total it** — extra tokens reprocessed and, where available, extra latency, for each swap and summed across the whole session. Numbers that can't be measured from the log are marked as unknown with a stated reason, never guessed.
7. **Deliver a direct build/don't-build verdict** using a concrete threshold (e.g., "3 swaps each re-sending ~4,000 avoidable tokens in a 20-turn session → worth building a canonical-state cache manager" vs. "2 swaps both happened in the first 3 turns before the transcript had grown → not worth it yet").
8. **List the specific logging gaps** that, if closed, would sharpen a repeat of this analysis.

## Output you'll get

A short report with five parts, in this order:
1. **Session summary** — turn count, which models were used, number of swaps, how the transcript grew.
2. **Per-swap table** — for each swap: turn number, model before -> after, input tokens at that turn vs. the same-model baseline, latency delta if known, and a verdict of full re-prefill / partial reuse / inconclusive (missing data).
3. **Total estimated waste** — tokens and/or latency attributable to swaps, each number tagged as measured-from-data or estimated-from-growth-pattern.
4. **Build/don't-build verdict** — one direct sentence with the reasoning threshold.
5. **Data gaps** — what to log next time to turn an estimate into a measurement (e.g. "your harness isn't logging per-turn input tokens — most Ollama/llama.cpp wrappers expose this in their response metadata").

## Rules this skill follows

- It never invents a token count, latency number, or cache-hit figure that isn't in the log you pasted or a number you explicitly stated — anything it can't measure is reported as unknown, with a note on what to log to get it.
- It never assumes a swap caused full re-prefill without actually comparing that swap turn to a same-model baseline turn first — some harnesses already dedupe shared prefixes, and the report checks for that before calling something waste.
- It will not design or hand you an actual cache-manager implementation — that's a separate infrastructure build, not this diagnostic. If you want that next, say so explicitly and expect a different kind of response.
- If your pasted log has no model swaps in it at all, it says so and stops rather than inventing a hypothetical swap to analyze.
- If a swap has fewer than two same-model turns before it to compare against, that specific comparison is marked low-confidence rather than presented as solid.
