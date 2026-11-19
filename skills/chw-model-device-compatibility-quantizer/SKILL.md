---
name: chw-model-device-compatibility-quantizer
description: Pre-screens whether a clinical (or other resource-constrained) SLM checkpoint will fit and run usably on a specific low-RAM Android device, at a given quantization level, before a field pilot commits time to a device that turns out to be too small. Use when someone has a model checkpoint and a target device spec and wants a hardware-fit estimate before testing on real hardware.
---

# Device Fit Advisor: Clinical Model Quantization & Compatibility Pre-Screen

## When to use this
A developer, ML engineer, or program lead has a clinical (or other field-deployed) small language model checkpoint and a specific target device — described by RAM/chipset or by a known device model — and wants to know, before committing field-test time or procuring hardware, whether a given quantization level (int4/int8/mixed) will actually fit in the device's usable memory budget and leave a workable margin. This is a pre-screen for an engineering decision, not a replacement for testing on the actual physical device.

Do not use this for a final go/no-go on clinical deployment. It estimates hardware fit only; it does not and cannot assess whether quantization degraded the model's clinical accuracy.

## Inputs
**Data source**: Manual — the user supplies the model's checkpoint identity and the target device's hardware specs directly in the conversation. (The parent project this skill is drawn from also integrates a Firebase Test Lab connector to run automated multi-device verification after packaging — that connector is part of the maintained toolchain, not this one-shot advisory skill, which never calls any API or device farm itself.)

Required from the user:
1. **Model identity** — name/family and parameter count (e.g. "MedGemma 4B", "a 2.7B clinical fine-tune of Phi-3").
2. **Target context length** the deployment actually needs (e.g. "2048 tokens" — not the model's max supported length, the length the use case requires).
3. **Target device** — either:
   - Exact specs: total RAM, chipset, Android version, and whether it has a dedicated GPU/NPU usable by the inference engine, OR
   - A known device model name (e.g. "Itel A56," "Samsung Galaxy A14") if the user doesn't know the raw specs — ask for the RAM figure from the spec sheet if this skill's knowledge of that model is uncertain, rather than guessing silently.

Optional, improves precision:
4. Exact architecture values from the model's `config.json` — `num_hidden_layers`, `hidden_size`, `num_key_value_heads` (or `num_attention_heads` if no GQA). Without these, estimates fall back to a generic band for the model's parameter-count class and must be flagged as lower-confidence.
5. Any hard latency requirement (e.g. "must hit first token under 5 seconds").

If any required input is missing, ask for it rather than guessing — a device-fit estimate built on an assumed RAM figure is worse than no estimate.

## Procedure
1. **Confirm scope up front**: state this produces a formula-based memory-fit estimate, not a verified on-device benchmark, and that a hardware PASS says nothing about clinical accuracy.
2. **Compute usable memory budget** for the target device:
   `usable_MB = min(0.5 × total_RAM_MB, 2048)`
   This is a conservative rule of thumb (Android commonly enforces a per-process memory ceiling around 2GB regardless of total device RAM, and background OS/other-app overhead eats roughly half of total RAM on low-end devices). State the formula and the resulting number explicitly; note it should be confirmed against the OEM's actual per-app limit if that's known.
3. **Estimate weight memory** for each of three quantization levels, using `weight_MB = params_billions × 1000 × bytes_per_param`:
   - INT4 (Q4_K_M-class): 0.59 bytes/param
   - Mixed (Q4_K_M attention / Q6_K rest): 0.65 bytes/param
   - INT8 (Q8_0-class): 1.05 bytes/param
   - (FP16 baseline, 2.0 bytes/param, for reference only — state plainly it is not viable on-device at this device class and skip it from the verdict table unless the user asks.)
4. **Estimate KV cache memory** at the user's required context length:
   `kv_MB = 2 × num_layers × hidden_size × context_tokens × 2 bytes / 1e6`
   - If the user gave exact `config.json` values, use them and state "architecture: exact, from config.json."
   - If not, use a fallback band by parameter count and say so explicitly: ≤3B params → ~26 layers, ~2048 hidden size; 3–6B params → ~34 layers, ~3072 hidden size; state "architecture: estimated band, lower confidence — exact figures would tighten this estimate."
   - Note explicitly that this formula assumes full multi-head attention; if the model uses grouped-query attention (common in modern small models), the true KV cache may be meaningfully smaller — call this out as a reason a FAIL verdict might be overly conservative, never as a reason to upgrade a verdict without confirmation.
5. **Add fixed runtime overhead**: 400 MB for the inference engine (llama.cpp / MediaPipe LLM Inference API runtime, tokenizer, buffers).
6. **Total and classify** each quantization level: `total_MB = weight_MB + kv_MB + 400`, `ratio = total_MB / usable_MB`.
   - `ratio ≤ 0.70` → **PASS**
   - `0.70 < ratio ≤ 0.95` → **BORDERLINE**
   - `ratio > 0.95` → **FAIL**
7. **Recommend** the lowest-footprint level that reaches PASS; if none reach PASS, recommend the closest BORDERLINE level and name concrete mitigations (shorter context window, a smaller model variant, confirming GQA reduces the KV estimate, or a higher-RAM device) rather than recommending a FAIL level.
8. **Always close** with the clinical-accuracy caveat: aggressive quantization (especially INT4) can degrade clinical terminology and reasoning non-uniformly in ways this memory estimate cannot detect — recommend running the candidate quantized build through a clinical-accuracy regression check before any field commitment, regardless of hardware verdict.

## Output format
```
## Device Fit Report: <model> on <device>

### Scope note
Formula-based memory-fit estimate, not a verified on-device benchmark. A PASS here says nothing about clinical accuracy under quantization.

### Memory budget
- Device total RAM: <X> MB
- Usable per-app budget (min(50% of total, 2048MB)): <Y> MB
- Runtime engine overhead: 400 MB (included in totals below)
- Architecture basis: exact (from config.json) | estimated band (lower confidence)

### Quantization options
| Level | Est. weights | Est. KV cache (@<N> tokens) | Total est. | % of usable budget | Verdict |
|---|---|---|---|---|---|
| INT4 (Q4_K_M) | ... MB | ... MB | ... MB | ...% | PASS/BORDERLINE/FAIL |
| Mixed (Q4_K_M/Q6_K) | ... | ... | ... | ...% | ... |
| INT8 (Q8_0) | ... | ... | ... | ...% | ... |

### Recommendation
<recommended level and why, or — if nothing reaches PASS — the closest BORDERLINE option plus named mitigations>

### Caveats
- GQA note (if applicable): the KV cache estimate assumes full multi-head attention; if this model uses grouped-query attention, actual usage may be lower.
- Architecture confidence note (exact vs. estimated band).
- Clinical-accuracy reminder: run a clinical-accuracy regression check on the recommended build before any field deployment decision.
- This is a pre-screen, not a substitute for testing on the physical device or an automated device-farm run.

### Missing inputs (if any)
- <what's needed to tighten this estimate>
```

## Guardrails
- Never present this report as a verified or tested benchmark — it is a formula-based estimate; always use the scope note and never imply it ran on real hardware.
- Never silently invent a device's RAM, chipset, or a model's architecture values. If the user names a device or model without specs, ask for the figure or clearly label an estimate as "estimated band, lower confidence" rather than stating it as fact.
- Never let a hardware PASS verdict stand in for a clinical-accuracy judgment — always include the clinical-accuracy regression reminder, even when the hardware fit looks comfortable.
- Never upgrade a FAIL to a BORDERLINE or PASS based on an unconfirmed GQA assumption — note it as a reason the estimate might be conservative, but keep the stated verdict based on the full-attention formula unless the user confirms the model's actual KV-head count.
- Never recommend shipping to a field pilot based on this report alone — always state it is a pre-screen, and point toward physical-device or device-farm testing (e.g. Firebase Test Lab, or a borrowed unit of the target device) before committing field time.
