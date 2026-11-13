---
name: asr-small-llm-quantization-survey-benchmark
description: Recommends a paired post-training-quantization method for an ASR model and a small LLM that must run together on one constrained device (phone, Raspberry Pi-class SBC, or GPU-less laptop), by pulling current primary-source quantization benchmarks and combining them against the device's real memory budget. Use when a developer is building an offline voice-input-plus-text-generation feature and needs to pick quantized formats for both models at once, not research each one separately.
---

# Edge Stack Quant Picker: Pairing an ASR Model and a Small LLM Under One Memory Budget

## When to use this
A developer is building an offline/local device feature that chains speech-to-text into text generation (dictation-and-rewrite, voice journaling, offline meeting notes, voice-driven assistants) on hardware with a fixed, limited RAM/compute budget — a phone, a Raspberry Pi-class SBC, or a laptop CPU with no discrete GPU — and says something like "I want to run Whisper-tiny and a 1B model together on a Pi 5, which quantization should I use for each?" They need a specific quant-method recommendation per model that fits both loaded simultaneously, not general quantization theory and not two separate unrelated research threads.

Do not use this for: picking the base models themselves (the user must already have a target ASR model and target LLM in mind, or at minimum a narrow shortlist), or for GPU-rich server deployment where memory isn't the binding constraint.

## Inputs
**Data source**: Connected — the recommendation is built from live-pulled primary sources (arXiv quantization benchmark papers, HuggingFace model cards/config files, and PTQ library docs such as GGUF/llama.cpp, GPTQ, AWQ, bitsandbytes, CTranslate2) fetched via web search at the time of the request; the only manual input is the user naming their target model pair and hardware tier.

Required, ask for whichever is missing before producing a recommendation:
1. **Target ASR model** — exact name/size (e.g. "Whisper-tiny", "Whisper-base.en", "Moonshine-tiny").
2. **Target LLM** — exact name/size (e.g. "Qwen2.5-0.5B-Instruct", "Llama-3.2-1B", "Gemma-2-2B-it").
3. **Hardware tier and its real RAM ceiling** — phone-class, SBC-class (name the board, e.g. "Raspberry Pi 5, 8GB"), or laptop-CPU-class (name total RAM). Do not guess this — a Pi 5 4GB and a Pi 5 8GB produce different recommendations, and this is the single most load-bearing input.
4. **Runtime/inference stack**, if known (e.g. `llama.cpp`/GGUF, `faster-whisper`/CTranslate2, plain `transformers`+`bitsandbytes`, ONNX Runtime). If unstated, ask — recommending GPTQ for a CPU-only `llama.cpp` deployment is a wasted answer.

Optional: a stated priority between transcription accuracy and generation quality if the two can't both be preserved at the available budget, and a target end-to-end latency if one exists.

## Procedure
1. **Confirm scope.** If any of inputs 1–3 is missing or vague ("a small LLM", "a Raspberry Pi" with no RAM stated), ask before estimating anything. Never substitute an assumed model or RAM figure.
2. **Establish the memory budget.** Take the hardware tier's total RAM, subtract a realistic OS/app overhead (as a stated assumption, e.g. "~1.5-2GB reserved for OS + app on an 8GB Pi 5" — label this a rule-of-thumb, not a cited number), and treat the remainder as the combined ceiling both quantized models plus KV-cache/audio-buffer overhead must fit under.
3. **Pull current primary-source quantization data for the ASR model's family** via web search — anchor on Qualcomm's Edge-ASR benchmark (arXiv 2507.07877, 8 PTQ methods across Whisper/Moonshine variants) and any Whisper-specific PTQ comparison (e.g. arXiv 2511.08093 comparing dynamic int8/Quanto, static quant, nf4, int3 on Whisper-small) that covers the named model or its closest sibling size. Record WER deltas and the bit-width/method name exactly as reported.
4. **Pull current primary-source quantization data for the LLM's family** via web search — the model's own HuggingFace card (which usually lists GGUF/GPTQ/AWQ quantized variants with reported perplexity or benchmark deltas) plus any public comparison of PTQ methods at that parameter class. Record perplexity/eval deltas and bit-width/method name exactly as reported.
5. **Map each candidate method to the stated runtime stack** (step 4 of Inputs) — e.g. GGUF `Q4_K_M`/`Q5_K_M`/`Q8_0` for a `llama.cpp` stack, CTranslate2 int8 for `faster-whisper`, bitsandbytes NF4/INT8 for a plain `transformers` runtime, GPTQ/AWQ only if the stack actually supports them (mostly GPU-oriented). Discard any method incompatible with the stated stack even if its benchmark numbers look best.
6. **Estimate combined memory footprint** for 2–3 surviving (ASR-method, LLM-method) pairs: parameter count × bits-per-weight ÷ 8, plus a stated runtime-overhead assumption (typically 10-20% for activations/buffers), summed across both models. Compare each pair's total against the budget from step 2.
7. **Rank the pairs that fit the budget** by expected combined accuracy retention using the cited deltas from steps 3–4, not invented numbers. If the use case states a priority (e.g. transcription accuracy matters more because errors compound into bad generation input), weight the ranking accordingly and say so explicitly.
8. **Flag the synthesis gap honestly.** No public primary source benchmarks this ASR+LLM pairing loaded together on this exact hardware (this is the documented gap the skill exists to cover) — state plainly that the recommendation is a synthesis of separately-measured components plus a memory-budget estimate, not a verified joint measurement, and name the one validation step that would confirm it (load both quantized models simultaneously on the actual target hardware and measure peak resident memory + end-to-end latency on a representative audio+text sample).
9. **Self-check before answering**: every WER/perplexity number traces to a named source from steps 3-4; every memory figure is marked either "cited" or "estimated"; the recommended methods are compatible with the stated runtime stack; the hardware RAM ceiling used matches exactly what the user stated.

## Output format
A single markdown response, in this order:
1. **Inputs recap** (one line): confirmed ASR model, LLM, hardware tier + RAM, runtime stack.
2. **Memory budget**: the RAM ceiling used and the overhead assumption, labeled as a rule-of-thumb.
3. **Recommended pairing** (table): columns `Model | Recommended quant method | Bit-width | Source for the accuracy delta | Estimated memory`.
4. **Expected tradeoffs**: WER delta for the ASR choice, perplexity/quality delta for the LLM choice, combined estimated memory vs. budget, each tagged `[cited: <source>]` or `[estimated]`.
5. **Confidence and validation step**: one paragraph stating this is a synthesis (per step 8), not a jointly-benchmarked result, plus the exact on-device measurement the user should run before shipping.
6. **Sources**: a bulleted list of every paper/model-card/doc actually consulted, with links.

## Guardrails
- Never state a WER, perplexity, latency, or memory number without tagging it `[cited: <source>]` or `[estimated]` — an untagged number reads as a verified joint benchmark when none exists.
- Never recommend a quantization method incompatible with the user's stated runtime stack (e.g. GPTQ/AWQ for a CPU-only `llama.cpp` target, or a GGUF-only quant for a pure `transformers`+`bitsandbytes` pipeline) even if its isolated benchmark numbers are the best available.
- Never guess the hardware RAM ceiling or the target model identities — ask and stop if either is missing or vague; this skill's entire value is being hardware-and-model-specific, and a generic answer defeats the point.
- Never claim this exact ASR+LLM pairing has been benchmarked loaded together anywhere — as of this skill's writing no public primary source does that; always surface the "synthesis, not verified joint measurement" caveat and the concrete validation step.
- Never silently sum each model's standalone reported memory footprint as the final answer without adding a stated runtime-overhead buffer — real combined memory on-device is reliably higher than the sum of two isolated numbers.
