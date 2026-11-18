# Scenario 2 — Generation task on a memory-constrained cloud instance

## Input (as the user would hand it over)

> I'm fine-tuning Qwen2.5-1.5B to continue short fantasy story openings in a specific narrative
> voice I've been developing. I'm renting a g4dn.xlarge instance for this — it's a T4 GPU with
> 16GB VRAM, and it's the cheapest instance type I can get approved for. I have about 3,000
> examples of story-opening-plus-continuation pairs I wrote myself over the last year. Example:
>
> Opening: "The lighthouse keeper hadn't seen a ship in eleven years."
> Continuation: "Which was precisely why he kept the lamp burning every night regardless, because
> the one night he didn't would be the night one finally came, and he'd rather be a fool every
> other night than wrong on that one."
>
> (2,999 more pairs, similar style and length — second-person-adjacent literary voice, medium
> sentence complexity)
>
> Haven't started training. What should I try?

## Expected behavior

1. Resolves device budget: 16GB * 0.8 = ~12.8GB usable.
2. Computes footprints for 1.5B params: Full ~24GB, LoRA ~3.3GB, QLoRA 8-bit ~1.95GB, QLoRA
   4-bit ~1.05GB.
3. Filters: Full does not fit (24 > 12.8). LoRA, QLoRA 8-bit, and QLoRA 4-bit all fit, each with
   large headroom relative to the 12.8GB budget.
4. Recognizes task type as generation/creative → ranks toward the LEAST-quantized fitting
   option (LoRA fp16) rather than the most-quantized, since quantization hurts generation/style
   quality more and plenty of headroom exists to afford the less-quantized choice.
5. Notes dataset size (3,000 rows) is decent but not large enough (not >5,000) to push toward
   full fine-tune even hypothetically.
6. Gives ONE primary recommendation (expected: LoRA fp16, reasoning tied to generation task
   quality sensitivity + comfortable headroom) and ONE fallback (expected: QLoRA 8-bit, the next
   rung down, since LoRA is not the most-quantized option in scope here).
7. Closes with the validation caveat.

## Pass/fail criteria

- PASS requires: Full fine-tune correctly excluded; LoRA fp16 (not QLoRA) selected as primary
  specifically because the task is generation/creative and headroom allows it — this must be the
  opposite ranking direction from Scenario 1's classification task, demonstrating the task-type
  branch in the procedure actually changes the outcome; fallback is QLoRA 8-bit (a real rung
  down, not a non-method fallback, since LoRA isn't the most-quantized option); dataset size
  correctly treated as sufficient, not flagged as too small; validation caveat present.
- FAIL if: the skill picks QLoRA (any bit-width) as primary for a generation task when LoRA fp16
  comfortably fits with headroom to spare; the skill gives the same recommendation pattern as
  Scenario 1 (showing task type isn't actually affecting the logic); the fallback direction is
  reversed or missing; VRAM numbers are stated as exact/certain rather than estimates.
