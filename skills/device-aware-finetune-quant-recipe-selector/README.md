# Fit Tune Advisor

A paste-into-any-AI-chat-tool prompt that tells you which fine-tuning method (full fine-tune, LoRA, or QLoRA) and which quantization level to try first, given a specific GPU/cloud device and task — before you spend any GPU time finding out the hard way that your first guess OOMs or quietly tanks quality.

## When to use this

You have a target device in mind (a specific consumer GPU, a named cloud instance type, or an on-premise box) and a fine-tuning task for an open-weight model in roughly the 1B-13B parameter range (Llama/Qwen/Gemma-class models and similar). You have not started training yet. You want a starting-point recommendation instead of the usual trial-and-error loop: try full fine-tune, hit an out-of-memory error, try LoRA, hit an accuracy cliff at 4-bit quantization, try QLoRA at 8-bit, and finally land on something that works — several failed, multi-hour attempts later.

This is **not** for picking a base model, writing training code, debugging a run already in progress, or getting a scientifically validated recipe. It is a one-time advisory judgment based on known VRAM-footprint rules of thumb and published quantization-tradeoff patterns — a first guess worth validating on a small slice of your own data before you commit to a full run, not a measured result.

## What to hand over

**Data source note**: the device-profile side of this is something a connected tool (or an AI assistant with shell access) can read directly — `nvidia-smi`/`rocm-smi` for local GPU VRAM, or the Hugging Face Hub API for a model's parameter count — so if you're using this inside a tool that can run commands or hit URLs, let it fetch those instead of typing them in. If you're pasting this into a plain chat window with no tool access, type them in yourself. The task side is always something only you can supply — no connector can know your specific fine-tuning objective.

Give the assistant:

1. **Target device**: GPU model + VRAM (e.g., "RTX 4090, 24GB") or cloud instance type (e.g., "g5.2xlarge, 24GB A10G"), and whether it's a training-capable GPU or an inference-only edge target.
2. **Base model**: name and parameter count (e.g., "Qwen2.5-7B-Instruct, 7B params"). If you don't know the exact parameter count, give your best estimate from the model name.
3. **Task type**: is this classification, extraction, or generation/creative writing? This matters a lot — quantization hurts generation quality more than it hurts classification accuracy.
4. **Dataset**: how many rows you have, and 5-20 real example rows (not placeholders) so the assistant can sanity-check length and label distribution.

## The prompt

Paste this, filling in your own details:

```
Act as a fine-tuning method and quantization recipe advisor. I have NOT started training yet
and want a starting-point recommendation, not a final validated answer.

My setup:
- Device: <GPU model + VRAM, or cloud instance type>
- Base model: <name>, approx <N> billion parameters
- Task type: <classification / extraction / generation-or-creative>
- Dataset: <row count> rows. Example rows:
<paste 5-20 real example rows here>

Do the following:
1. Compute a usable VRAM budget as 80% of my total VRAM (reserve headroom for activations/batching).
2. Estimate the VRAM footprint of each candidate using these planning-estimate formulas
   (P = parameter count in billions):
   - Full fine-tune (fp16, Adam optimizer): ~16 * P GB
   - LoRA (fp16 base + adapter): ~2.2 * P GB
   - QLoRA 8-bit: ~1.3 * P GB
   - QLoRA 4-bit: ~0.7 * P GB
   Label these explicitly as rough planning estimates, not guarantees.
3. Filter to only the candidates whose estimate fits within my usable VRAM budget. If NONE fit
   even QLoRA 4-bit, tell me plainly instead of forcing a recommendation — and suggest a smaller
   model or a bigger device instead.
4. Rank the candidates that DO fit:
   - If my task is classification or extraction: prefer the most-quantized fitting option (more
     headroom, low quality risk from quantization for this task type).
   - If my task is generation or creative: prefer the LEAST-quantized fitting option (LoRA fp16
     over QLoRA 8-bit over QLoRA 4-bit) even if it leaves less headroom, since quantization hurts
     generation quality more. Only drop to a more-quantized option if nothing less-quantized fits.
   - Only prefer full fine-tune over LoRA if it fits AND my dataset has more than 5,000 rows;
     on smaller datasets LoRA/QLoRA avoid wasted compute and overfitting risk.
5. If my dataset is under ~200 rows, flag that explicitly as a red flag regardless of method
   choice — no method fixes too little data.
6. Give me ONE primary recommendation (method + quantization level) with your reasoning, plus
   ONE fallback for if the primary turns out to OOM in practice (these are planning estimates,
   not guarantees):
   - If a more-quantized option below the primary still fits, that's the fallback.
   - If the primary is already the most-quantized option (QLoRA 4-bit) with nothing left below
     it, say so and instead suggest reducing batch size, shortening sequence length, or using
     gradient accumulation — and note that if those don't help, the fix is a bigger device, not
     a different method.
7. Close with this caveat, stated plainly: this is a rule-of-thumb starting point from known
   VRAM-footprint patterns, not a measured result on my actual data — I should validate it with
   a short run on a small slice of my data before committing to a full multi-hour job.

Output as:
- A table of all 4 candidate footprints and whether each fits my device
- Primary recommendation + reasoning
- Fallback recommendation
- The validation caveat
```

## What you get back

A short table of the four method/quantization combinations with their estimated VRAM footprint and whether each fits your device, followed by one primary recommendation (with the reasoning behind it — task type, dataset size, headroom), one fallback option in case the primary runs out of memory, and a closing reminder that this is a starting guess to validate on a small slice of your data, not a final answer.

## Guardrails

- This never claims to have run any training — it's an estimate, always labeled as one.
- It never recommends a combination that its own VRAM-budget filter shows won't fit your device.
- It always asks for (or should be given) your task type — classification/extraction and generation/creative tasks get opposite quantization-preference logic, and skipping this question means guessing wrong half the time.
- It always includes a fallback option and the validation caveat — a recommendation with no fallback and no "go verify this on a small slice first" caveat is incomplete.
- If your dataset is tiny (under ~200 rows), it should say so instead of quietly giving you a confident-sounding answer anyway.
