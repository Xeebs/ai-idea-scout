---
name: device-aware-finetune-quant-recipe-selector
description: Recommends a starting fine-tuning method (full / LoRA / QLoRA) and quantization level for a given target device and task, before any training run starts. Use when someone has a GPU/instance in mind and a fine-tuning task but hasn't picked a method yet and wants to avoid discovering an OOM or accuracy cliff the hard way.
---

# Fit Tune Advisor

## When to use this
Someone has a specific target device in mind (a consumer GPU, a named cloud instance type, or an on-premise box) and a fine-tuning task for an open-weight model (roughly 1B-13B parameter class — Llama/Qwen/Gemma-style), has not started any training run yet, and wants a starting-point recommendation for which method (full fine-tune, LoRA, or QLoRA) and which quantization level to try first — instead of guessing, hitting an out-of-memory error or an accuracy cliff, and iterating by trial and error.

Do not use this for: picking a base model, writing training code, debugging an in-progress training run, or producing a final validated recipe — this is a one-time advisory judgment based on known VRAM-footprint rules of thumb and quantization-tradeoff patterns, not a measured result. It does not run any training. If the user wants a measured, probe-validated recommendation (short comparative training runs on their own data), tell them that's a separate, heavier workflow this skill does not perform, and this advisory should be treated as a first guess to validate, not a final answer.

## Inputs
**Data source**: Connected (device profile) + Manual (task/dataset). The device side is Connected and needs no new setup: if running in an environment with shell access (e.g., Claude Code) and the device is local, run `nvidia-smi --query-gpu=name,memory.total --format=csv` or `rocm-smi --showmeminfo vram` directly instead of asking the user to report numbers, and look up the target base model's parameter count and config via the public Hugging Face Hub API (`https://huggingface.co/api/models/<org>/<model>`) instead of asking the user to supply it. Fall back to the user's own stated GPU model/VRAM and model name when no shell/network access exists. The task side is always Manual — there is no connector that can infer a team's specific fine-tuning objective, so the user must state the task type and supply a few real example rows.

Required from the user (or obtained directly, per above, when tool access allows):
1. Target device: GPU model name + VRAM (e.g., "RTX 4090, 24GB") or cloud instance type (e.g., "g5.2xlarge"), and whether it's training-capable or inference-only.
2. Base model: name/HF ID and parameter count (e.g., "Qwen2.5-7B-Instruct").
3. Task type: classification, extraction, or generation/creative (this changes the quantization-tolerance verdict below) — ask explicitly if not stated, never guess it from the model name alone.
4. Dataset size (row count) and a handful (5-20) of real example rows — not a toy placeholder; real data shape matters for sanity-checking context length and label distribution.

## Procedure
1. **Resolve device VRAM budget.** Get the device's total VRAM. Apply an 80% usable-budget rule (reserve 20% headroom for activations/batch-size slack the estimates below don't fully capture) — call this `budget_gb`.
2. **Estimate footprint per candidate method**, using parameter count `P` (in billions):
   - Full fine-tune (fp16/bf16, Adam optimizer): `~16 * P` GB (weights + gradients + optimizer states).
   - LoRA (fp16 base + small adapter): `~2.2 * P` GB.
   - QLoRA 8-bit: `~1.3 * P` GB.
   - QLoRA 4-bit: `~0.7 * P` GB.
   These are planning estimates, not guarantees — state them as such in the output, not as precise numbers.
3. **Filter to candidates that fit** `budget_gb` with estimate ≤ `budget_gb`. If none fit even QLoRA 4-bit, say so plainly and recommend either a smaller base model or a bigger/cloud device — do not force a recommendation that will OOM.
4. **Rank fitting candidates by task-type tolerance:**
   - Classification or extraction tasks: quantization accuracy loss is typically small; prefer the candidate with the most VRAM headroom (usually the most quantized fitting option) since quality risk is low and headroom buys room for longer context/larger batches.
   - Generation/creative tasks: quantization accuracy loss is more noticeable, especially at 4-bit; prefer the least-quantized candidate that fits (LoRA fp16 over QLoRA 8-bit over QLoRA 4-bit) even if it leaves less headroom, unless only a 4-bit option fits at all.
   - Full fine-tune, when it fits, is offered as an option but not auto-preferred over LoRA unless the dataset is large (>5,000 rows) — on small datasets LoRA/QLoRA avoid wasting compute and reduce overfitting risk, which outweighs full fine-tune's small quality edge.
5. **Flag dataset-size mismatches.** Datasets under ~200 rows are a red flag regardless of method choice — note this explicitly and recommend either gathering more data or treating any result as unreliable, since no method choice fixes too little data.
6. **State the primary recommendation plus one fallback** for if the primary OOMs in practice despite fitting the estimate (these are planning estimates, not guarantees — real overhead from context length/batch size can exceed them):
   - If a more-quantized fitting candidate exists below the primary, the fallback is that next rung down (e.g., primary LoRA fp16 → fallback QLoRA 8-bit).
   - If the primary is already the most-quantized candidate in scope (QLoRA 4-bit) with no rung left below it, say so explicitly and give a non-method fallback instead: reduce batch size, shorten sequence length/context window, or use gradient accumulation to shrink the footprint further — and note that if none of those help, the task needs a bigger device, not a different method.
   Never give a recommendation with no documented fallback of one of these two kinds.
7. **Always close with the validation caveat**: this is a rule-of-thumb starting point from known VRAM-footprint patterns and published quantization-tolerance observations, not a measured result on the user's actual data; recommend validating with a short run on a small data slice before committing to a full multi-hour/multi-epoch job.

## Output format
```
# Fit Tune Advisory — <model name> on <device>

**Device budget**: <VRAM>GB total, ~<budget_gb>GB usable (80% rule)
**Model**: <name>, ~<P>B parameters
**Task type**: <classification|extraction|generation> — <one-line why this matters for quantization tolerance>
**Dataset**: <row count> rows <flag if <200 rows>

## Candidate footprints
| Method | Est. VRAM | Fits device? |
|---|---|---|
| Full fine-tune | ~<X>GB | yes/no |
| LoRA (fp16) | ~<X>GB | yes/no |
| QLoRA 8-bit | ~<X>GB | yes/no |
| QLoRA 4-bit | ~<X>GB | yes/no |

## Recommendation
**Primary**: <method + quantization> — <reasoning: why this one given task type, headroom, dataset size>
**Fallback if primary OOMs**: <next rung down>

## Caveat
This is a rule-of-thumb starting point, not a measured result. Validate with a short training run on a small slice of your own data (a few hundred steps) before committing to a full run.
```

## Guardrails
- Never state a VRAM estimate as exact — always frame the formulas in Step 2 as planning estimates, and say so in the output.
- Never recommend a combination that your own Step 3 filter shows doesn't fit the device budget.
- Never skip asking for task type (classification/extraction vs. generation) — it directly changes the ranking logic in Step 4 and guessing it from the model name alone is not justified.
- Never present this as a validated recipe or claim it ran any training — it is an advisory judgment only; always include the validation caveat in the output.
- Never fabricate a device's VRAM or a model's parameter count — if shell/network access isn't available and the user hasn't stated it, ask rather than guessing.
- If the dataset is under ~200 rows, flag it explicitly rather than silently producing a confident-sounding recommendation.
