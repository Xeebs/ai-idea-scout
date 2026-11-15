# Phone Compression Philosophy Advisor

A paste-anywhere prompt template for choosing between a **ternary-native** on-device model (trained ternary from scratch, e.g. PrismML's Bonsai/Ternary Bonsai family) and a **compress-from-large** model (a large model shrunk via conventional quantization or distillation, e.g. a 2-bit or Q4 quant of a 27B+ base) for a phone deployment — without taking either vendor's self-reported benchmark numbers at face value.

## When to use this

You're building an on-device AI feature for a budget or mid-range phone and you're stuck choosing between two competing compression philosophies, each backed only by its own vendor's favorable numbers. You want a recommendation that clearly separates "the vendor claims this" from "this was actually independently checked" — and that doesn't assume your latency problem is even caused by the model, if your task involves vision or audio preprocessing.

## What this is NOT

This is not a live connection to a continuously-updated, independently-run benchmark leaderboard. That project (an independent head-to-head harness comparing these two philosophies on real budget-tier hardware) does not exist as a running public service yet. Until it does, this prompt runs in **manual research-fallback mode**: it uses whatever web search capability your AI tool has to pull current vendor-reported numbers, and it is explicit and loud about the fact that those numbers are unverified. If you happen to have an exported table from such a project (CSV or markdown), paste it in and the prompt will prefer it over the fallback search.

## What to hand over

Before using this, have ready:

1. **Your target task** — be specific. "Tool-calling for a shopping assistant", "vision-grounded QA on product photos", "on-device sentiment classification", "general chat/reasoning" are all different enough that the right model differs.
2. **Your phone tier** — RAM (e.g. "2GB RAM Android Go device"), whether it has a dedicated NPU, OS, and chip family if you know it.
3. **Your constraints** — at least one of: a max acceptable latency (cold-start and/or steady-state tokens/sec), a minimum acceptable accuracy relative to an FP16 baseline, or a max on-disk model size/storage budget.
4. **Optional**: a pasted leaderboard export, if you have access to one.

If you're missing any of 1–3, the assistant should ask you for it rather than guessing — don't let it skip this.

## The prompt

Paste this into any AI chat tool that has web search available, filling in the bracketed parts:

```
You are helping me choose between a ternary-native on-device model (trained
ternary from scratch, e.g. PrismML's Bonsai/Ternary Bonsai family) and a
compress-from-large model (a large model shrunk via conventional quantization
or distillation, e.g. a 2-bit or Q4 quant of a 27B+ base) for the following
phone deployment:

Target task: [DESCRIBE YOUR TASK]
Phone tier: [RAM, NPU presence/absence, OS, chip family if known]
Constraints: [latency target, accuracy floor, and/or max model size]
Leaderboard data I have (optional, paste or skip): [PASTE OR LEAVE BLANK]

Follow this procedure:

1. Confirm you have everything you need from the task/phone tier/constraints
   above. If anything critical is missing, ask me before continuing.
2. If I pasted leaderboard data, search it for rows matching my task and a
   comparable hardware tier and prefer those as verified evidence.
3. If I did not paste leaderboard data, search the web for current
   ternary-native and compress-from-large models that plausibly fit my task
   and RAM/storage budget. For each one, record the model name, claimed
   accuracy on a relevant benchmark, claimed latency/memory figures, and the
   source. Tag every figure [VENDOR-REPORTED] unless the source explicitly
   says it's an independent third-party reproduction — if it does, name that
   source so I can check it myself.
4. Apply this known risk pattern regardless of source: aggressive low-bit and
   ternary models have been reported to degrade more on tool-calling and
   vision tasks than on math/code tasks, and some low-bit builds show no real
   speedup over a standard Q4 build on certain hardware. If my task is
   tool-calling or vision, flag this explicitly even if the vendor's numbers
   look good.
5. If my task involves vision, audio, or heavy pre/post-processing, tell me
   plainly that end-to-end latency may be dominated by preprocessing/
   tokenization rather than model inference, and that switching compression
   philosophy won't fix a preprocessing bottleneck. Recommend I profile my
   own request lifecycle (input-handling time vs. forward-pass time) before
   swapping models.
6. Give me one primary recommendation (philosophy + specific model) and one
   fallback alternative, matched to my stated constraints, with every number
   tagged [VENDOR-REPORTED] or [INDEPENDENTLY VERIFIED].
7. Assign a confidence level: HIGH only if independently verified data covers
   my exact task+hardware pairing, MEDIUM if vendor data is directly on-task
   but unverified, LOW if you had to extrapolate from an adjacent benchmark.
8. End with a short checklist of exactly what I should verify myself on my
   actual device before shipping.

Format your answer as:

## Recommendation
Primary: <philosophy> — <specific model>
Fallback: <philosophy> — <specific model>
Confidence: HIGH | MEDIUM | LOW — <why>

## Why this fits my constraints
- (task fit)
- (phone tier / RAM / NPU fit)
- (latency or accuracy fit)

## Evidence
| Model | Claimed metric | Value | Source | Status |
|---|---|---|---|---|

## Capability risk flags
- (tool-calling/vision degradation, if relevant)
- (input-handling-bottleneck note, if relevant)

## Verify before you ship
- (specific thing to benchmark yourself, on your actual device)

Never present a vendor-reported number as independently verified. Never
invent a benchmark number — if you can't find one for my exact pairing, say
so and lower the confidence level instead. Never skip asking for missing
inputs.
```

## Guardrails (built into the prompt above, repeated here for clarity)

- Vendor-reported and independently-verified numbers are never blended or left untagged.
- No fabricated benchmark figures — gaps in available data lower the confidence level instead of being papered over.
- A vision/audio task latency complaint always gets the input-handling-bottleneck caveat before any model-swap recommendation.
- Missing task, phone tier, or constraint information is grounds to stop and ask, not to assume.
- This prompt never claims a live connection to an independent, continuously-updated leaderboard unless you've actually pasted one in.
