---
name: local-gpu-quant-autoselect-launcher
description: Recommends the right quantization format (GGUF/AWQ/GPTQ/FP8) per component of a multi-model local pipeline (LLM + TTS + diffusion, etc.) that must jointly fit an 8-16GB consumer GPU's VRAM, and gives the exact commands to download and launch each component. Use when a user wants to run a local multimodal pipeline on a specific GPU and is choosing quant formats by trial and error.
---

# Local GPU Quant Autoselect & Launcher

## When to use this
The user names a specific consumer/laptop GPU (e.g. "RTX 4070 laptop, 8GB", "RTX 3060 12GB") and a set of two or more local model components they want running together — typically an LLM plus at least one of TTS, image diffusion, or embedding/vision model — and either asks which quantization format to use, reports an out-of-memory crash, or is manually trying GGUF/AWQ/GPTQ/FP8 variants one at a time. This skill is specifically for the **joint, cross-component** budgeting problem — picking one quant format for a single standalone model is a narrower, already well-covered task; this skill's value is in reasoning about several components sharing one VRAM budget at once.

## Inputs
**Data source**: Connected — reads model size/parameter-count and available quantized-variant metadata from the Hugging Face Hub API (`huggingface.co/api/models/<repo>`, public, no auth needed for the vast majority of repos) and detects local hardware directly via `nvidia-smi --query-gpu=memory.total,memory.free --format=csv` or `rocm-smi` when Claude is running with local shell access. The only manual input required from the user is naming which model(s) they want per pipeline stage and their GPU model/VRAM if shell access to the actual machine isn't available (e.g. the user is pasting into a plain chat tool from a different device, or describing a remote/cloud box).

Before starting, confirm you have (ask if missing):
1. **GPU**: model name and total VRAM (e.g. "RTX 4070 Laptop, 8GB"). If you have Bash/shell access to the actual target machine, run `nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader` yourself instead of asking.
2. **Pipeline components**: each model the user wants loaded, by name or Hugging Face repo ID (e.g. "Llama-3.1-8B-Instruct", "XTTS-v2", "SDXL base 1.0"). If a name is ambiguous (multiple repos match), ask which specific checkpoint.
3. **Concurrency**: do the components need to be loaded in VRAM **at the same time** (e.g. a live voice-chat pipeline: LLM generates text, TTS speaks it, both must be resident for low latency) or **sequentially** (e.g. a batch job: generate text, unload, then generate images)? This single question changes the budget math more than any other input — never assume either way.
4. **Context/usage assumptions**: rough context length for the LLM (default to 8K if unstated) and whether this is single-request or needs to serve concurrent requests (default to 1).

## Procedure
1. **Resolve each component to a concrete base model + parameter count.** Use the Hugging Face Hub API (`GET https://huggingface.co/api/models/<repo>`) to pull `config.json` fields (`num_parameters` or compute from hidden_size/layers if absent) for the base/original checkpoint the user named. If shell/web access isn't available, use well-known public parameter counts (e.g. Llama-3.1-8B = 8B params, SDXL base UNet ≈ 2.6B, XTTS-v2 ≈ 0.47B) and say you're using known reference figures rather than a live lookup.
2. **For each component, compute estimated VRAM footprint at each candidate quant level** using these rule-of-thumb bytes-per-parameter figures (weights only, before overhead):
   - FP16/BF16: ~2.0 bytes/param
   - FP8 / Int8 (AWQ/GPTQ 8-bit): ~1.05 bytes/param
   - GGUF Q5_K_M or AWQ/GPTQ 5-bit: ~0.65 bytes/param
   - GGUF Q4_K_M or AWQ/GPTQ 4-bit: ~0.55 bytes/param
   - GGUF Q3_K_M: ~0.45 bytes/param (flag quality risk — only offer this if nothing else fits)
   Add fixed overhead on top of weights: **+10-15% of weight size for runtime/framework overhead** (CUDA context, activations) per loaded engine, plus **KV cache** for LLMs, estimated as `2 * num_layers * hidden_size * context_length * bytes_per_kv_element` (use FP16 KV cache, 2 bytes/element, unless the user says otherwise) — this is the term people most often forget and the one that causes "it fit yesterday, OOMs today with a longer prompt."
3. **Check for an existing pre-quantized artifact before recommending a from-scratch conversion.** Search Hugging Face Hub for community quantized repos of the exact checkpoint (common publishers: `bartowski`, `unsloth`, `TheBloke`, `casperhansen`, model-author's own `-GGUF`/`-AWQ` repos). Only recommend running AutoRound/llama.cpp conversion yourself if no suitable pre-quantized artifact exists at the needed quant level.
4. **Allocate the VRAM budget across components according to the concurrency answer from Inputs step 3:**
   - **Concurrent**: sum every component's footprint (weights + overhead + KV cache where applicable) and require the sum to fit within **85% of free VRAM** (15% headroom reserved for OS/display/other processes — consumer laptops in particular often have 0.5-1.5GB already claimed by the display).
   - **Sequential**: only the single largest component's footprint needs to fit within the 85% budget at any one time; note that unloading/reloading between stages adds latency the user should expect.
5. **Pick the highest-quality quant format per component that satisfies the budget constraint**, preferring in this order when multiple formats fit equally: pre-quantized AWQ/GPTQ (better accuracy retention at same bit-width) > GGUF (best tooling/portability on consumer hardware) > FP8 (only if the GPU architecture actually supports native FP8 — most consumer 8-16GB cards below Hopper/Blackwell-class do not get a real speed benefit from it, flag this).
6. **If nothing fits even at the lowest acceptable quant level**, say so explicitly and offer concrete fallbacks: drop one component, swap it for a smaller model in the same family, reduce context length, or split components across sequential stages instead of concurrent — never silently round down to "it'll probably be fine."
7. **Emit the exact launch command** for whichever tool matches the chosen format: `ollama run <model>:<tag>` or `./llama-cli -m <file>.gguf --n-gpu-layers -1` for GGUF; `vllm serve <repo> --quantization awq` (or `gptq`/`fp8`) for AWQ/GPTQ/FP8 via vLLM; the component's own standard loader invocation (e.g. `diffusers` pipeline call with `torch_dtype` set) for diffusion/TTS components without a CLI convention. Use the real flag names for whichever version context you're given; say explicitly if you're inferring flags from general knowledge rather than having checked current docs.

## Output format
A single response with:
1. **Assumptions used** (GPU + VRAM, concurrency mode, context length) — one line each, so the user can immediately spot if you misread something.
2. A **per-component table**: Component | Candidate checkpoint/repo | Recommended quant format | Estimated VRAM (weights+overhead, and KV cache if applicable) | Source artifact (existing repo ID, or "convert yourself") | Launch command.
3. **Budget check line**: total estimated VRAM vs. free VRAM vs. the 85% threshold, stated as numbers, not just "should fit."
4. **Risk flags**: anything estimated rather than measured, any component within 10% of the threshold, and a one-line reminder that real usage can vary ±15-20% from the estimate — recommend the user run with a short test prompt/short generation first before a long session.

## Guardrails
- Never state a configuration "will fit" without showing the arithmetic (sum of per-component estimates vs. budget) — the user needs to be able to check your math, not just trust a verdict.
- Never invent a pre-quantized artifact repo ID that you have not actually confirmed exists (via the Hub API or stated prior knowledge) — if unsure, say "verify this repo exists on Hugging Face Hub" rather than presenting a guessed repo name as fact.
- Never skip the concurrency question (Inputs step 3) — budgeting a concurrent voice-pipeline the same way as a sequential batch job is the single most common way this recommendation goes wrong, and it is the one input the idea this skill is based on explicitly flags as the gap existing single-model tools miss.
- Never claim a live `nvidia-smi` reading when you don't actually have shell access to the user's machine — ask them to paste the output, or ask for GPU model/VRAM directly, and say which one you're doing.
- Never recommend FP8 on a GPU architecture that doesn't have native FP8 support (pre-Ada/Hopper-class) just because it has the smallest footprint on paper — note that it will run via emulation/upcast with no real speed benefit and usually recommend AWQ/GGUF instead on that hardware.
- If the user's ask is really "pick a quant for one single model" with no second component, say this skill's main value (cross-component budgeting) doesn't apply and give a shorter single-model answer rather than padding it with pipeline framing it doesn't need.
