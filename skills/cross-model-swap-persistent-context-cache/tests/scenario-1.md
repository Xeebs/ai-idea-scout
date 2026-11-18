# Scenario 1 — Ollama terminal agent, full token/latency logging, clear re-prefill signature

## Input

A developer pastes a JSON-lines log from a custom Ollama-backed terminal agent loop (modeled on the kind of harness the source Hermes PR targets). The agent uses `qwen2.5:7b` for routine steps and swaps to `qwen2.5:32b` for two harder steps, then swaps back. 14 turns total.

```jsonl
{"turn":1,"model":"qwen2.5:7b","input_tokens":420,"output_tokens":180,"latency_ms":900}
{"turn":2,"model":"qwen2.5:7b","input_tokens":640,"output_tokens":150,"latency_ms":1050}
{"turn":3,"model":"qwen2.5:7b","input_tokens":830,"output_tokens":200,"latency_ms":1200}
{"turn":4,"model":"qwen2.5:7b","input_tokens":1080,"output_tokens":190,"latency_ms":1400}
{"turn":5,"model":"qwen2.5:32b","input_tokens":5200,"output_tokens":300,"latency_ms":6800}
{"turn":6,"model":"qwen2.5:32b","input_tokens":5600,"output_tokens":260,"latency_ms":5100}
{"turn":7,"model":"qwen2.5:7b","input_tokens":6100,"output_tokens":210,"latency_ms":4200}
{"turn":8,"model":"qwen2.5:7b","input_tokens":1900,"output_tokens":175,"latency_ms":1350}
{"turn":9,"model":"qwen2.5:7b","input_tokens":2150,"output_tokens":190,"latency_ms":1500}
{"turn":10,"model":"qwen2.5:7b","input_tokens":2400,"output_tokens":165,"latency_ms":1550}
{"turn":11,"model":"qwen2.5:32b","input_tokens":7800,"output_tokens":340,"latency_ms":9100}
{"turn":12,"model":"qwen2.5:32b","input_tokens":8200,"output_tokens":310,"latency_ms":7000}
{"turn":13,"model":"qwen2.5:7b","input_tokens":8700,"output_tokens":220,"latency_ms":5800}
{"turn":14,"model":"qwen2.5:7b","input_tokens":2950,"output_tokens":200,"latency_ms":1700}
```

Note the pattern: turns 1-4 on 7b grow linearly (~420 to 1080). Turn 5 swaps to 32b and input tokens jump to 5200 — far above the linear trend, consistent with a full re-prefill plus padding/system overhead rather than reuse. Turn 7 swaps back to 7b and input tokens are 6100 (the full transcript), then turn 8 drops back to 1900 — note turn 8 is actually *lower* than turn 7, meaning this harness is doing some kind of truncation/compaction on swap-back, not a clean baseline continuation. This is intentionally slightly messy, like a real log.

## Pass criteria

- Correctly identifies all 4 swap points: turn 5 (7b→32b), turn 7 (32b→7b), turn 11 (7b→32b), turn 13 (32b→7b).
- Flags turns 5, 11 as showing a token jump inconsistent with linear growth on the prior baseline (full re-prefill signature) with reasonable confidence.
- Notices turn 8's drop relative to turn 7 and calls out that this suggests the harness is already doing some compaction/truncation on swap-back, rather than ignoring it or treating turn 7 as a clean baseline for turn 8.
- Produces a per-swap table covering all 4 swaps with input tokens, latency, and a verdict per swap (not just an aggregate number).
- Gives a concrete total estimated extra tokens/latency figure attributable to swaps, clearly labeled as measured-from-data (since this log has full token+latency fields) rather than estimated-from-proxy.
- Delivers an explicit build/don't-build verdict with a stated threshold (e.g., total reprocessed tokens and swap frequency relative to transcript length), not a hedge like "it depends."
- Does NOT invent a cache-hit/miss field that isn't in the log.
- Does NOT produce an actual cache-manager design/implementation — stays within diagnostic scope.

## Fail criteria

- Misses or miscounts the swap points.
- Treats turn 8 as a clean linear-growth baseline without noting the anomaly vs turn 7.
- Gives a vague "could go either way" verdict instead of a concrete threshold-based call.
- Fabricates a latency or token number not present in the log.
