# Local GPU Quant Autoselect & Launcher

Paste this into any AI chat tool (ChatGPT, Claude, Gemini, a local model, etc.) when you're trying to run **more than one local AI model together** (for example a text LLM plus a voice/TTS model plus an image diffusion model) on a consumer or laptop GPU with 8-16GB of VRAM, and you want to stop guessing quantization formats by trial and error.

## When to use this

Use this when you can say something like: "I have an RTX 4070 Laptop with 8GB VRAM. I want to run Llama-3.1-8B-Instruct, XTTS-v2, and SDXL base together for a local voice assistant that can also generate images. What quantization format should I use for each, and what's the fit?"

This is specifically for the case where **two or more models have to share one GPU's memory**. If you only have one model and just want a quant recommendation for it, that's a simpler, already-common question — this prompt's real value is the joint budgeting math across components, so use a lighter prompt for single-model questions.

## What to hand over

Before running this, have ready (or be ready to answer when asked):

1. **Your GPU and VRAM**: e.g. "RTX 4070 Laptop, 8GB" or "RTX 3060, 12GB". If you can run a command on the actual machine, run this and paste the output instead of guessing:
   ```
   nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
   ```
   (AMD cards: `rocm-smi --showmeminfo vram`)
2. **Every model you want running**, named as specifically as you can (e.g. "Llama-3.1-8B-Instruct" not just "a Llama model", "XTTS-v2", "SDXL base 1.0").
3. **Whether the models need to be loaded at the same time or one after another.** Example: a live voice assistant needs the LLM and TTS both resident simultaneously for low latency — that's concurrent. A batch job that writes a story then separately generates an illustration for it can load one, finish, unload, then load the next — that's sequential. This one detail changes the entire budget calculation, so always be explicit about it.
4. (Optional) Your expected context length / prompt length for the LLM, and whether you need to serve more than one request at a time. Default assumption if you don't say: 8K context, single request.

## What it does

Given the above, the assistant will:

1. Identify the real parameter count of each model you named (via public model info if it can look things up, or well-known reference figures otherwise).
2. Estimate the VRAM footprint of each model at each realistic quantization level, using these rule-of-thumb weight sizes (before overhead):
   - FP16/BF16 — about 2.0 bytes per parameter
   - FP8 / 8-bit AWQ/GPTQ — about 1.05 bytes per parameter
   - 5-bit (GGUF Q5_K_M or AWQ/GPTQ 5-bit) — about 0.65 bytes per parameter
   - 4-bit (GGUF Q4_K_M or AWQ/GPTQ 4-bit) — about 0.55 bytes per parameter
   - 3-bit (GGUF Q3_K_M) — about 0.45 bytes per parameter, only as a last resort since quality drops noticeably
   It then adds roughly 10-15% on top for runtime/framework overhead per loaded model, plus a KV-cache estimate for any LLM component (this is the term people most often forget, and the reason a setup that fit yesterday suddenly OOMs with a longer prompt today).
3. Checks whether a ready-made pre-quantized version of your exact model already exists at the needed quant level (common publishers to look for: bartowski, unsloth, TheBloke, casperhansen, or the model author's own GGUF/AWQ repo) before suggesting you convert anything yourself.
4. Adds up the footprints according to whether you said concurrent or sequential, and requires the total to fit within about 85% of your free VRAM (reserving headroom for your OS/display, which on a laptop can already be using 0.5-1.5GB).
5. Picks the best quant format per model that fits, preferring pre-quantized AWQ/GPTQ for accuracy, then GGUF for portability, and only recommending FP8 if your specific GPU architecture actually benefits from native FP8 support (most 8-16GB consumer cards today do not).
6. If nothing fits, it says so plainly and gives you real alternatives — drop a component, swap in a smaller model, shorten your context, or switch that stage from concurrent to sequential — rather than quietly pretending a too-tight fit will be fine.
7. Gives you the exact command to actually launch each component once the format's picked (Ollama/llama.cpp invocation for GGUF, a vLLM `--quantization` flag for AWQ/GPTQ/FP8, or the standard loader call for components without a dedicated CLI).

## What you get back

A short report with:
- The assumptions it used (your GPU/VRAM, concurrent-vs-sequential, context length) stated up front so you can catch a misread immediately.
- A table: component, model/checkpoint, recommended quant format, estimated VRAM (including KV cache where relevant), where to get the artifact (an existing repo, or "convert it yourself"), and the launch command.
- A budget check showing the actual numbers — total estimated VRAM vs. your free VRAM vs. the 85% safety threshold — not just a verdict.
- Flags on anything that's an estimate rather than a measurement, and a reminder that real usage can be 15-20% off the estimate, so test with a short prompt/short generation before trusting a long session.

## What it will not do

- It will not tell you a setup "will fit" without showing you the arithmetic behind that claim.
- It will not invent a pre-quantized model repo that it hasn't actually confirmed exists — if it's not sure, it will tell you to verify on Hugging Face Hub rather than presenting a guess as fact.
- It will not skip asking whether your pipeline is concurrent or sequential — that's the single detail that most often breaks a naive single-model recommendation when applied to a multi-model pipeline.
- It will not claim to have read your actual GPU's live memory if it doesn't have real access to your machine — it will ask you to paste `nvidia-smi` output or state your GPU/VRAM directly.
- It will not recommend FP8 just because the math looks smallest on paper if your GPU's architecture doesn't actually support native FP8 — it will flag that you'd be running an emulated/upcast path with no real benefit.
