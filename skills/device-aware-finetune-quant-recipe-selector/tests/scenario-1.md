# Scenario 1 — Classification task on a single consumer GPU

## Input (as the user would hand it over)

> I want to fine-tune Llama-3.1-8B to classify incoming support tickets into one of 5 categories
> (billing, bug report, feature request, account access, other). I have a single RTX 4090 with
> 24GB VRAM at home, nothing else to work with. I have about 800 labeled tickets exported from
> our helpdesk. Here are a few examples:
>
> 1. "My card was charged twice this month, can someone refund the duplicate?" → billing
> 2. "The export button on the dashboard just spins forever and never downloads anything" → bug report
> 3. "It would be great if we could filter the reports page by date range" → feature request
> 4. "I'm locked out of my account after changing my password yesterday" → account access
> 5. "Just wanted to say the new UI looks great" → other
>
> (795 more rows like this, similar length, label distribution roughly 30% billing, 25% bug
> report, 20% feature request, 15% account access, 10% other)
>
> I haven't started training yet. What should I try first?

## Expected behavior

1. Resolves device budget: 24GB * 0.8 = ~19.2GB usable.
2. Computes footprints for 8B params: Full ~128GB, LoRA ~17.6GB, QLoRA 8-bit ~10.4GB, QLoRA
   4-bit ~5.6GB.
3. Filters: Full does not fit (128 > 19.2). LoRA, QLoRA 8-bit, and QLoRA 4-bit all fit.
4. Recognizes task type as classification → ranks toward the most-quantized fitting option
   (QLoRA 4-bit or 8-bit), not toward LoRA fp16, since quantization accuracy loss is low-risk
   for classification and headroom is more valuable here.
5. Notes dataset size (800 rows) is reasonable — not a red flag, not large enough to favor full
   fine-tune even if it fit.
6. Gives ONE primary recommendation (expected: QLoRA 4-bit or QLoRA 8-bit, with reasoning tied
   to classification task + headroom) and ONE fallback. Since QLoRA 4-bit is the most-quantized
   option in scope, if the primary chosen is QLoRA 4-bit, the fallback must be the non-method
   kind (reduce batch size/sequence length/bigger device) rather than a nonexistent "more
   quantized than 4-bit" option. If primary is QLoRA 8-bit, fallback should be QLoRA 4-bit.
7. Closes with the validation caveat (this is a rule-of-thumb starting point, validate on a
   small slice first).

## Pass/fail criteria

- PASS requires: Full fine-tune correctly excluded as not fitting; LoRA correctly identified as
  fitting but not the top pick for a classification task with headroom to spare; a single clear
  primary recommendation with reasoning referencing task type; a fallback that is logically
  consistent (no "more quantized than 4-bit" fallback ever appears); the validation caveat is
  present; no VRAM number is stated as exact/guaranteed.
- FAIL if: the skill recommends full fine-tune (impossible on 24GB for an 8B model with Adam);
  the skill ignores task type and defaults to "always pick LoRA" or "always pick the biggest
  that fits"; the fallback is missing or nonsensical (e.g., recommends "QLoRA 2-bit" which isn't
  a defined candidate); the caveat is omitted; the dataset size (800 rows, not under 200) is
  incorrectly flagged as too small.
