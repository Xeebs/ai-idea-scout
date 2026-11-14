# Scenario 1 — Concurrent voice+vision assistant, budget does NOT fit

## Input (as the user would actually type it)

> I have a gaming laptop with an RTX 4070 Laptop GPU, 8GB VRAM. `nvidia-smi` shows 7040MB free right now (something's already using a bit of it for the display). I want to build a local voice assistant: Llama-3.1-8B-Instruct for the brain, XTTS-v2 for speaking the replies out loud in real time, and SDXL base 1.0 so it can also generate an illustration on request while the conversation keeps going. All three need to stay loaded and ready at the same time — if I have to unload/reload between a reply and an image, the voice assistant stops feeling real-time. Figure ~6K context for the conversations. What quant format should I use for each, and will this actually fit?

## What a correct response does

1. States the assumptions back clearly: GPU = RTX 4070 Laptop, free VRAM = 7040MB (user-supplied, not a live read since the skill has no shell access to this specific machine), concurrency = **concurrent** (all three resident simultaneously), context = 6K.
2. Produces a per-component table covering Llama-3.1-8B-Instruct, XTTS-v2, and SDXL base 1.0, each with a candidate quant format and an estimated VRAM number (weights + ~10-15% overhead, plus KV cache estimate for the LLM).
3. Sums the three estimates and compares against 85% of 7040MB (≈5984MB) — even at the most aggressive quant levels offered (GGUF Q4_K_M for the LLM, int8/fp16 for TTS and diffusion since those don't quantize via the same GGUF/AWQ path as LLMs), the total should come out well over budget, and the response must say so explicitly with the actual numbers shown, not just assert a verdict.
4. Because it doesn't fit, offers concrete fallback options rather than hand-waving: e.g. move SDXL to sequential/on-demand loading (unload LLM/TTS briefly only when an image is actually requested, accepting a short pause only for that path), drop to a smaller LLM (e.g. an 8B → smaller distillation) or shorter context, or note that 8GB concurrent three-way is genuinely tight and sequential image generation is the realistic answer for this hardware.
5. Gives launch commands only for the components/format combination it's actually recommending (not commands for a combination it just said doesn't fit).
6. Flags that quant estimates are approximate (±15-20%) and that pre-quantized artifact repo names should be verified on Hugging Face Hub rather than presented as guaranteed to exist.

## Pass criteria

- [ ] Restates GPU, VRAM, concurrency mode, and context length as explicit assumptions before giving numbers.
- [ ] Produces a table with a quant format and VRAM estimate per component (not a vague paragraph).
- [ ] Shows the summed total vs. the 85%-of-free-VRAM threshold as actual numbers.
- [ ] Correctly concludes this concurrent 3-way setup does not fit on 8GB and says so plainly, rather than asserting it "should be fine."
- [ ] Offers at least one concrete, actionable fallback (sequential image stage, smaller model, shorter context) instead of just stopping at "it doesn't fit."
- [ ] Does not invent a specific pre-quantized Hugging Face repo name as a guaranteed fact without caveating that it should be verified.

## Fail conditions

- Claims the full concurrent setup fits on 8GB without flagging the tightness/overage.
- Skips showing the arithmetic and just gives a format recommendation with no VRAM numbers.
- Treats the pipeline as sequential despite the user explicitly saying all three must stay loaded simultaneously.
