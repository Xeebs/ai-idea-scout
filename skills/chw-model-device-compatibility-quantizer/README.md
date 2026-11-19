# Device Fit Advisor: Clinical Model Quantization & Compatibility Pre-Screen

A portable prompt that estimates whether a clinical (or any resource-constrained) small language model checkpoint will actually fit and run usably on a specific low-RAM Android device, before anyone spends field-test time or buys hardware to find out the hard way.

This is for anyone shipping an AI model to field devices with uncertain or low RAM — community-health-worker apps, offline clinical assistants, or any mobile deployment where "will this even run on that phone" is an open question before the pilot starts. It works in any chat tool; no special setup, SDK, or device-farm account required.

**What this is not**: a verified on-device benchmark, or a clinical-accuracy test. It only estimates whether the numbers add up to fit in memory. Hardware fit and clinical accuracy are separate questions — this tool answers the first one, not the second.

## How to use it

Paste the prompt block below into any AI chat tool, then give it:
1. **Model identity** — name/family and parameter count (e.g. "MedGemma 4B," or "a 2.7B clinical fine-tune of Phi-3").
2. **Target context length** your use case actually needs (not the model's max — the length you'll really use, e.g. "2048 tokens").
3. **Target device** — either exact specs (total RAM, chipset, Android version, GPU/NPU presence) or a device model name if you don't know the raw specs.
4. *(Optional, improves accuracy)* The model's exact `num_hidden_layers`, `hidden_size`, and `num_key_value_heads` from its `config.json`, if you have them.
5. *(Optional)* Any hard latency requirement.

If you leave something required out, a good response asks you for it rather than guessing a RAM figure or architecture spec.

---

### The prompt

> You are producing a memory-fit pre-screen for running a quantized language model checkpoint on a specific low-RAM Android device. This is a formula-based estimate, not a verified benchmark, and it says nothing about clinical accuracy — state that up front, every time.
>
> Given the model's parameter count, the required context length, and the target device's total RAM (ask for any of these if missing — never guess a device's RAM or a model's architecture silently):
>
> 1. **Usable memory budget**: `usable_MB = min(0.5 × total_RAM_MB, 2048)`. Show this number and the formula. (Rationale: Android commonly enforces a per-process ceiling around 2GB regardless of total RAM, and OS/other-app overhead eats roughly half of total RAM on low-end devices.)
>
> 2. **Weight memory** per quantization level, `weight_MB = params_billions × 1000 × bytes_per_param`:
>    - INT4 (Q4_K_M-class): 0.59 bytes/param
>    - Mixed (Q4_K_M attention / Q6_K rest): 0.65 bytes/param
>    - INT8 (Q8_0-class): 1.05 bytes/param
>    - (FP16, 2.0 bytes/param, for reference only — state it's not viable on-device at this class and otherwise skip it.)
>
> 3. **KV cache memory** at the required context length: `kv_MB = 2 × num_layers × hidden_size × context_tokens × 2 bytes / 1e6`. If exact `config.json` values are given, use them and say "architecture: exact." If not, use a fallback band and say "architecture: estimated band, lower confidence": ≤3B params → ~26 layers / ~2048 hidden size; 3–6B params → ~34 layers / ~3072 hidden size. Note that this formula assumes full multi-head attention — if the model uses grouped-query attention (common in modern small models), real usage may be lower; call this out as a reason a FAIL might be conservative, never as grounds to upgrade the verdict without confirmation.
>
> 4. **Runtime overhead**: add a fixed 400 MB (inference engine, tokenizer, buffers).
>
> 5. **Total and classify** each level: `total_MB = weight_MB + kv_MB + 400`, `ratio = total_MB / usable_MB`. ratio ≤ 0.70 → **PASS**; 0.70–0.95 → **BORDERLINE**; > 0.95 → **FAIL**.
>
> 6. **Recommend** the lowest-footprint level that reaches PASS. If none do, recommend the closest BORDERLINE level plus concrete mitigations (shorter context window, a smaller model variant, confirming grouped-query attention reduces the KV estimate, or a higher-RAM device) — never recommend a FAIL level as-is.
>
> 7. **Always close** with: this is a pre-screen, not a verified benchmark or a substitute for testing the physical device; and a hardware PASS says nothing about clinical accuracy under quantization — recommend a clinical-accuracy regression check on the recommended build before any field commitment, regardless of the hardware verdict.
>
> Output exactly this format:
> ```
> ## Device Fit Report: <model> on <device>
>
> ### Scope note
> Formula-based memory-fit estimate, not a verified on-device benchmark. A PASS here says nothing about clinical accuracy under quantization.
>
> ### Memory budget
> - Device total RAM: <X> MB
> - Usable per-app budget: <Y> MB
> - Runtime engine overhead: 400 MB (included in totals below)
> - Architecture basis: exact | estimated band (lower confidence)
>
> ### Quantization options
> | Level | Est. weights | Est. KV cache (@<N> tokens) | Total est. | % of usable budget | Verdict |
> |---|---|---|---|---|---|
> | INT4 (Q4_K_M) | | | | | |
> | Mixed (Q4_K_M/Q6_K) | | | | | |
> | INT8 (Q8_0) | | | | | |
>
> ### Recommendation
> <level and why, or closest BORDERLINE plus named mitigations>
>
> ### Caveats
> - GQA note if applicable
> - Architecture confidence note
> - Clinical-accuracy reminder (always include)
> - Pre-screen reminder: not a substitute for a physical-device or device-farm test (always include)
>
> ### Missing inputs (if any)
> - ...
> ```
>
> Never invent a device's RAM/chipset or a model's architecture figures — ask, or clearly label an estimate as a lower-confidence band. Never upgrade a stated verdict based on an unconfirmed GQA assumption. Never let a comfortable hardware number imply the model's clinical output quality is fine at that quantization level — the accuracy reminder is mandatory on every report, pass or fail.
>
> Here is what I have:
> [paste model identity + param count, required context length, and target device specs or model name — plus config.json architecture values if you have them]

## Why this exists

Multiple independent pilots deploying clinical SLMs to community health workers on real field phones — Crane AI's EaseHealth in Uganda (268 health workers), PRANAM/ApnaVaidya, AfyaPack, MAM-AI, and a BioCAS edge-hardware study — each separately hit the same wall: they found out their device was too small for the model *during or after* the field test, not before it. Generic quantization guides exist, but nothing public walks through "will this specific clinical checkpoint fit on this specific low-RAM Android phone" before committing field time to find out. This prompt is that pre-screen, usable today with no device farm or SDK.

Full project context, evidence, and a sketch of the maintained version of this idea (which adds an automated device-farm test runner via Firebase Test Lab and a published compatibility matrix across many model-device pairs) — see [`ideas/chw-model-device-compatibility-quantizer.md`](../../ideas/chw-model-device-compatibility-quantizer.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
