# Scenario 2 — Retail order-status and returns voice bot, thin data

## Input

A small e-commerce team building a Pipecat-based voice bot for order status and returns pastes:

> Tools:
> - `get_order_status(order_id)` — "pretty fast, I think," no data.
> - `search_similar_products(description)` — lets a caller ask "do you have something like X" and searches the catalog. p50 1.1s, p95 3s.
> - `initiate_return(order_id, reason)` — creates a return label and refund request. p50 600ms, p95 1.2s.
>
> No tone preference given. No answer given about barge-in reliability — the team didn't mention it at all.

## Pass criteria

- `get_order_status` is marked `UNCLASSIFIED`/flagged for missing data rather than given an invented latency figure or a confident threshold decision — the skill must ask for or flag the missing number instead of guessing "pretty fast" into a specific ms value.
- `search_similar_products` is classified `search` and correctly flagged as needing filler (p50 1.1s > 700ms); given its worst-case (3s) is under 3x the 700ms threshold (2.1s), it should get a single filler line, not a full escalation ladder — the skill should not over-build a ladder for a borderline case.
- `initiate_return` is a judgment call right at the threshold (p50 600ms is under 700ms, but p95 1.2s is under 1.5s too) — correct output is "No filler needed" since neither figure crosses the stated default threshold; this checks the skill applies the OR rule correctly rather than flagging anything that looks vaguely slow.
- Since the team gave no tone preference, the output defaults to the stated default ("warm but professional, not chipper") rather than inventing an unjustified style, and says it's using the default.
- Since barge-in reliability was never addressed at all (not even "unknown"), the skill either explicitly asks the team to confirm it or treats it conservatively as unknown and applies the warning — it must not silently assume reliable barge-in with no basis.
- Open Flags section lists `get_order_status` as missing data.

## Fail conditions

- `get_order_status` gets a specific latency number invented on the team's behalf ("assuming ~500ms...") instead of being flagged.
- `initiate_return` is incorrectly flagged as needing filler despite being under both threshold figures.
- `search_similar_products` gets an unnecessary multi-step escalation ladder for a case that only barely crosses 3x threshold reasoning.
- The missing barge-in information is ignored entirely with no flag and no request for clarification.
