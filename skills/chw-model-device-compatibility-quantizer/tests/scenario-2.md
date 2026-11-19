# Scenario 2 — Smaller clinical SLM against a mid-range device, with exact architecture given

## Setup
A developer has a smaller clinical fine-tune and a more capable (but still budget) device, and this time supplies exact architecture values. They provide:

```
Model: a 2B-parameter clinical fine-tune of Gemma, internally called "ClinicalGemma-2B"
config.json values: num_hidden_layers = 26, hidden_size = 2048, num_key_value_heads = 4
  (num_attention_heads = 8, so this model uses grouped-query attention)
Required context length: 1024 tokens
Target device: Samsung Galaxy A14
  - Total RAM: 4 GB (4096 MB)
  - Chipset: Exynos 850, no dedicated NPU
  - Android version: 13
Latency requirement: first token under 5 seconds preferred, not hard-blocking.
```

They ask: "Which quantization level should I ship, and how much margin do I actually have?"

## Pass criteria
- [ ] Opens with the scope note.
- [ ] States "architecture: exact, from config.json" since num_hidden_layers/hidden_size were given — does not fall back to the estimated band.
- [ ] Computes usable budget as `min(0.5 × 4096, 2048) = 2048 MB` and shows this explicitly.
- [ ] Computes KV cache using the full-attention formula (2 × 26 × 2048 × 1024 × 2 / 1e6 ≈ 218 MB) and explicitly flags that because num_key_value_heads (4) is less than num_attention_heads (8), i.e. this model uses GQA, the true KV cache is likely smaller than this conservative estimate — named explicitly as a reason the computed verdict might be conservative, not used to silently shrink the number or upgrade the verdict without saying so.
- [ ] INT4 total estimate lands in the ballpark of ~1.75–1.85 GB (weights ~1.18 GB + KV ~0.22 GB + 0.4 GB overhead), landing at roughly 85–90% of the 2048 MB usable budget → classified **BORDERLINE**, not PASS and not FAIL.
- [ ] INT8 total estimate lands clearly above the 95% FAIL threshold (weights alone ~2.1 GB already exceeds the 2048 MB usable budget before KV/overhead) → classified **FAIL**.
- [ ] Recommendation names INT4 as the only viable option, states the margin is tight (BORDERLINE, not comfortable), and suggests at least one concrete way to improve the margin (e.g. confirming the GQA-adjusted KV cache is actually smaller, or trimming context length below 1024 if the use case allows).
- [ ] Includes the mandatory clinical-accuracy regression reminder, explicitly tied to the fact that INT4 is the only viable path and it's borderline, not comfortably passing.
- [ ] Includes the pre-screen / physical-device-testing closing reminder.

## Fail conditions
- Classifying INT4 as a comfortable PASS (ratio ≤ 0.70) — the actual ratio here is materially above that threshold.
- Classifying INT8 as BORDERLINE or PASS — weights alone already exceed the usable budget.
- Silently using the GQA fact to just report a lower KV number without surfacing that this is an inference/caveat, not a given exact figure the formula directly used.
- Treating "architecture: exact" as license to skip the clinical-accuracy reminder — accuracy risk from quantization is independent of whether the architecture figures are exact or estimated.
