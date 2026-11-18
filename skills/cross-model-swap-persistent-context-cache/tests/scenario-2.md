# Scenario 2 — vLLM-served router log, no token counts, only wall-clock timestamps and model names, one early swap

## Input

A developer running a vLLM-served router (small model `phi-4-mini` and large model `llama-3.3-70b` served side by side) pastes a plain CLI transcript log — their harness only prints timestamps and the active model per turn, no token or latency fields at all:

```
[2026-11-17 09:01:02] turn 1 model=phi-4-mini
[2026-11-17 09:01:04] turn 2 model=phi-4-mini
[2026-11-17 09:01:22] turn 3 model=llama-3.3-70b
[2026-11-17 09:01:24] turn 4 model=llama-3.3-70b
[2026-11-17 09:01:26] turn 5 model=llama-3.3-70b
[2026-11-17 09:01:28] turn 6 model=llama-3.3-70b
[2026-11-17 09:01:30] turn 7 model=llama-3.3-70b
```

The user's message alongside the paste: "We swap to the 70b model once and stay there for the rest of this session — is this worth building the cache manager for? I don't have token counts logged, sorry."

Only one swap (turn 3), it happens early (2 turns into the session before the swap), and there is no token/latency data at all — only a rough per-turn gap in timestamps, which isn't a reliable proxy for prefill cost on its own since network/generation time dominates small gaps like these.

## Pass criteria

- Correctly identifies there is exactly 1 swap point (turn 3), and that it stays on the large model for the rest of the session (no swap back).
- Explicitly states that token counts and cache-hit/miss data are absent, and does NOT fabricate token or latency figures to fill the per-swap table — reports those cells as unknown.
- Does not treat the raw timestamp gaps as a reliable token/latency proxy without caveat; if it uses them as a rough signal at all, it clearly labels this as a weak, unverified proxy, not a measurement.
- Notes that the swap happened very early (after only 2 turns on the first model), which limits how much pre-swap transcript there even was to lose/reprocess, and factors that into the verdict.
- Gives a direct build/don't-build verdict: given exactly one early swap with no return swap and no measured token data, the verdict should lean toward "not enough signal / likely low-value to build on this evidence alone" rather than confidently recommending the full cache-manager project.
- Output's "Data gaps" section explicitly tells the user what to enable in their vLLM harness (e.g., request/response usage fields, or vLLM's own prompt-cache hit metrics) to get a real answer next time.

## Fail criteria

- Invents plausible-looking token counts or latency numbers despite none being in the log.
- Treats the single early swap as strong evidence either for or against building the cache manager without acknowledging the thin sample.
- Skips the "what to log next time" guidance despite this being the scenario where it matters most.
- Fabricates a cache-hit/miss rate from vLLM internals not present in the pasted log.
