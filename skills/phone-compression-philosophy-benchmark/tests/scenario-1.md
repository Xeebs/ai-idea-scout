# Scenario 1 — Tool-calling shopping assistant on a budget Android Go phone

## Input

```
Target task: Tool-calling for a shopping assistant app — the model needs to
parse a user's natural-language request ("find me running shoes under $80
in size 10") and call one of 6 fixed JSON-schema tools (search_products,
filter_by_price, filter_by_size, add_to_cart, get_cart, checkout) with
correctly-typed arguments. No vision, no free-form chat beyond tool-call
formatting.

Phone tier: 2GB RAM Android Go devices (our main target market in Southeast
Asia and sub-Saharan Africa per our analytics), no dedicated NPU, mid-range
MediaTek chips, Android 13.

Constraints:
- Cold-start latency under 2 seconds on this hardware
- Tool-call argument accuracy must stay above 90% (we've measured our current
  cloud-based baseline at 96%, we can tolerate some drop but not much — this
  is a checkout flow, wrong arguments cause real cart errors)
- Total model file size under 1.5GB (device storage is tight and the app
  already ships other assets)

Leaderboard data I have: none, skip.
```

## Pass criteria

- [ ] Asks no further clarifying questions (task, phone tier, and all three constraints are already fully specified) — proceeds straight to research/recommendation.
- [ ] Produces a primary recommendation naming a specific compression philosophy (ternary-native or compress-from-large) and a specific named model, not a generic "use a small quantized model" non-answer.
- [ ] Every numeric claim (accuracy %, latency, file size) in the Evidence table is tagged either `[VENDOR-REPORTED]` or `[INDEPENDENTLY VERIFIED]` — no bare, untagged numbers.
- [ ] Explicitly flags that tool-calling is a task type reported to degrade more under aggressive low-bit/ternary compression than math/code tasks, and weighs this against the 90% accuracy floor.
- [ ] Does NOT raise the input-handling-bottleneck caveat as a primary concern (this task has no vision/audio/heavy preprocessing component) — if it's mentioned at all it should be brief/dismissed as low-relevance, not treated as the main risk.
- [ ] Assigns a confidence level (HIGH/MEDIUM/LOW) with a one-line justification tied to whether independent data exists for tool-calling on 2GB-RAM-class hardware specifically.
- [ ] Includes a "verify before you ship" checklist with at least one item specific to this scenario (e.g. "run your actual 6-tool schema through the candidate model on a real MediaTek Android Go device, not an emulator, and measure argument-accuracy on your own test set, not a generic benchmark").
- [ ] Does not claim access to a live, continuously updated independent leaderboard — states plainly it is in manual research-fallback mode since no leaderboard data was supplied.

## Fail criteria (any of these = skill failed this scenario)

- Recommends a model/philosophy without naming it specifically.
- Presents a vendor's self-reported number as fact without the `[VENDOR-REPORTED]` tag.
- Silently invents a benchmark number for this exact task/hardware pairing that wasn't found via search.
- Fails to mention the tool-calling degradation risk at all.
