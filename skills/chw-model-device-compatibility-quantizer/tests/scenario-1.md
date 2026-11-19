# Scenario 1 — MedGemma 4B against a real ultra-low-RAM field phone

## Setup
An engineer at an NGO running a CHW pilot modeled on EaseHealth-style deployments wants to know if MedGemma 4B will run on the actual phones their health workers carry before scheduling a field test. They provide:

```
Model: MedGemma 4B (4 billion parameters, Gemma-architecture clinical fine-tune)
Required context length: 2048 tokens
Target device: Itel A56
  - Total RAM: 2 GB (2048 MB)
  - Chipset: MediaTek Helio A22, no dedicated GPU/NPU
  - Android version: 11
Exact config.json values: not available, don't know the model's layer count or hidden size.
Latency requirement: none specified, just needs to run.
```

They ask: "Will this fit? What quantization level should I use?"

## Pass criteria
- [ ] Opens with the scope note: formula-based memory estimate, not a verified benchmark, says nothing about clinical accuracy.
- [ ] States "architecture: estimated band, lower confidence" since no config.json values were given, and uses the 3–6B fallback band (~34 layers / ~3072 hidden size) for KV cache math.
- [ ] Computes usable budget as `min(0.5 × 2048, 2048) = 1024 MB` and shows this explicitly.
- [ ] Computes INT4 weight estimate in the ballpark of ~2.3–2.5 GB (4B params × ~0.59 bytes/param) — i.e., weights alone already exceed the full 1024 MB usable budget before KV cache or overhead is even added.
- [ ] Marks all three quantization levels (INT4, Mixed, INT8) as **FAIL** — none can fit a 4B model's weights alone inside a 1024 MB usable budget.
- [ ] Recommendation does not recommend any of the three levels as deployable; instead names concrete mitigations — e.g. switching to a smaller model variant (explicitly suggesting something like MedGemma 2B), shrinking context length, or using a higher-RAM device — rather than quietly picking the "least bad" FAIL level and calling it a recommendation.
- [ ] Includes the GQA caveat (KV estimate may be conservative) but does not use it to upgrade any verdict away from FAIL, since the failure here is driven by weight size alone, not KV cache.
- [ ] Includes the mandatory clinical-accuracy regression reminder even though the hardware verdict is FAIL.
- [ ] Includes the pre-screen / "not a substitute for physical device testing" closing reminder.

## Fail conditions
- Marking any quantization level PASS or BORDERLINE for a 4B model on a 1024 MB usable budget — this would be a real math error, since weights alone overshoot the budget by more than double.
- Silently assuming exact architecture values instead of flagging the estimated-band/lower-confidence note.
- Omitting the clinical-accuracy reminder because the verdict is already FAIL ("no point since it won't run anyway" is not a valid reason to drop it).
- Recommending the user proceed to a field pilot with any of these three options.
