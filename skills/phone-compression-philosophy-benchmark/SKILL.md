---
name: phone-compression-philosophy-benchmark
description: Recommends a specific on-device model (ternary-native vs. compress-from-large) and compression philosophy for a developer's target task, phone tier, and latency/accuracy constraints — every number tagged vendor-reported or independently verified, never blended. Use when a developer is choosing between a ternary model (e.g. PrismML's releases) and a conventionally quantized/distilled large model for a budget or mid-range phone deployment.
---

# Phone Compression Philosophy Advisor

## When to use this
A developer is about to pick a model for an on-device phone feature (classification, tool-calling, vision QA, general reasoning, chat) and is stuck choosing between two competing philosophies: a **ternary-native** model (trained ternary from scratch, e.g. PrismML's Bonsai/Ternary Bonsai family) and a **compress-from-large** model (a large model shrunk via conventional quantization/distillation, e.g. a 2-bit or Q4 quant of a 27B+ base). They know their target task and phone tier but are relying on each vendor's own self-reported benchmark numbers to decide, with no independent reproduction to check against. Trigger phrases: "ternary vs quantized for my phone app", "which compressed model should I use on a budget Android", "ternary Bonsai vs Q4 quant for [task]".

## Inputs
**Data source**: Connected — ideally reads the "Honest Compare" project's own published, independently-reproduced leaderboard and latency-breakdown dataset (a re-runnable benchmark harness comparing ternary-native vs. compress-from-large models on matched real hardware). That connector does not exist yet as a running service as of this writing — the companion project described in this idea is still at MVP stage. Until it is published, this skill runs in **manual research-fallback mode**: the developer manually supplies (a) their target task, phone tier, and constraints, and the skill uses live web search to pull each vendor's own self-reported numbers, explicitly tagging every figure `[VENDOR-REPORTED]` since no independent reproduction exists yet. If/when the developer has access to an exported Honest Compare leaderboard table (CSV or markdown), they can paste it and the skill will prefer it over the fallback search, tagging those figures `[INDEPENDENTLY VERIFIED]`.

Required from the developer:
1. **Target task** — e.g. "tool-calling for a shopping assistant", "vision-grounded QA on product photos", "on-device sentiment classification", "general chat/reasoning".
2. **Phone tier** — RAM (e.g. "2GB Android Go device"), presence/absence of an NPU, OS, and chip family if known.
3. **Constraints** — at minimum one of: max acceptable latency (cold-start and/or steady-state tokens/sec), minimum acceptable accuracy relative to an FP16 baseline, or a max on-disk model size/storage budget.
4. **Optional**: a pasted/linked Honest Compare leaderboard export, if one exists by the time this is used.

If any of 1–3 is missing, ask for it before producing a recommendation — do not guess silently.

## Procedure
1. Confirm all three required inputs are present (task, phone tier, constraints). If not, ask targeted follow-up questions and stop.
2. Check whether the developer supplied leaderboard data (input 4). If yes, search it for rows matching the task type and a comparable hardware tier; prefer these rows as `[INDEPENDENTLY VERIFIED]` evidence.
3. If no leaderboard data was supplied, run a web search for current ternary-native and compress-from-large model options that plausibly fit the task and the phone tier's RAM/storage budget (e.g. search for the task name plus "on-device model" plus "ternary" / "quantized"). For each candidate pulled from the search, record: model name, claimed accuracy on a relevant benchmark, claimed latency/memory figures, and the source. Tag every one of these `[VENDOR-REPORTED]` unless the source explicitly states it is an independent third-party reproduction — if a source claims independence, name that source so the developer can verify it themselves.
4. Apply known capability risk patterns regardless of source: ternary and aggressive low-bit models have been reported to degrade more on tool-calling and vision-grounded tasks than on math/code tasks, and some low-bit builds show no real speedup over a standard Q4 build on certain hardware. If the target task is tool-calling or vision, flag this risk explicitly even if the vendor's own numbers look favorable.
5. Flag the input-handling-bottleneck risk: if the target task involves vision, audio, or heavy pre/post-processing, state plainly that end-to-end latency may be dominated by tokenization/image-preprocessing rather than model inference, and that swapping compression philosophy will not fix a preprocessing bottleneck. Recommend the developer profile their own request lifecycle (input-handling time vs. forward-pass time) before committing to a model swap.
6. Produce one primary recommendation (philosophy + specific model) and one fallback alternative, each matched against the stated constraints, with every numeric claim tagged `[VENDOR-REPORTED]` or `[INDEPENDENTLY VERIFIED]`.
7. Assign a confidence level — `HIGH` only if independently verified data covers this exact task+hardware pairing, `MEDIUM` if vendor data is directly on-task but unverified, `LOW` if the developer's exact task/phone tier required extrapolating from an adjacent benchmark.
8. Close with a short "verify yourself before shipping" checklist specific to the gaps found.

## Output format
```
## Recommendation
Primary: <compression philosophy> — <specific model name/version>
Fallback: <compression philosophy> — <specific model name/version>
Confidence: HIGH | MEDIUM | LOW — <one line why>

## Why this fits your constraints
- <task fit reasoning>
- <phone tier / RAM / NPU reasoning>
- <latency or accuracy constraint reasoning>

## Evidence
| Model | Claimed metric | Value | Source | Status |
|---|---|---|---|---|
| ... | ... | ... | ... | [VENDOR-REPORTED] or [INDEPENDENTLY VERIFIED] |

## Capability risk flags
- <tool-calling/vision degradation note if applicable>
- <input-handling-bottleneck note if applicable>

## Verify before you ship
- <specific thing the developer should benchmark themselves on their actual device>
- <specific thing, e.g. "re-run your own task suite on the exact phone model, not an emulator">
```

## Guardrails
- Never present a `[VENDOR-REPORTED]` number as if it were independently verified — the entire point of this skill is to preserve that distinction the vendors themselves blur.
- Never fabricate a benchmark number. If search turns up nothing for the exact task/hardware pairing, say so and lower the confidence level rather than inventing or silently extrapolating a figure.
- Never recommend a model swap to fix a latency complaint on a vision/audio/multimodal task without first raising the input-handling-bottleneck possibility.
- Never skip asking for missing required inputs (task, phone tier, at least one constraint) — a recommendation built on assumed constraints is worse than no recommendation.
- Never claim access to a live, continuously-updated Honest Compare leaderboard unless the developer has actually supplied an export of it — until that project ships, say plainly that this is running in manual research-fallback mode.
