# Edge Stack Quant Picker — Pairing an ASR Model and a Small LLM Under One Memory Budget

Paste this whole file into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your answers to the four questions below. No prior context about any other project or repo is needed — this prompt is fully self-contained.

## What this does

If you're building an offline device feature that chains speech-to-text into text generation — dictation-and-rewrite, voice journaling, an offline meeting-note assistant — you usually need to quantize *two* models (an ASR model and a small LLM) to fit together on one device's memory budget. Researching ASR quantization and LLM quantization separately, and then guessing how they interact once both are loaded at once, is slow and error-prone. This prompt has the assistant pull current public benchmark data for each model family, estimate what the two quantized models actually cost together in memory, and return one specific quant-method recommendation per model — with every number labeled as either a cited source or an estimate, and an honest flag that no public source has benchmarked this exact pairing loaded together (so there's always one concrete on-device check you still need to run before shipping).

## When to use it

Use this when you already have a target ASR model and a target small LLM in mind (or a short list) and need to pick quantized formats for both that fit together on a specific piece of hardware — a phone, a Raspberry Pi-class board, or a GPU-less laptop. This is not for choosing which base models to use in the first place, and it's not for GPU-server deployments where memory isn't the real constraint.

## What to hand over

Give the assistant:
1. **Your target ASR model** — exact name and size (e.g. "Whisper-tiny", "Whisper-base.en", "Moonshine-tiny").
2. **Your target LLM** — exact name and size (e.g. "Qwen2.5-0.5B-Instruct", "Llama-3.2-1B", "Gemma-2-2B-it").
3. **Your hardware tier and its actual RAM** — be specific (e.g. "Raspberry Pi 5, 8GB", "iPhone 14, assume ~2GB app budget", "laptop, Intel CPU only, 16GB RAM"). This is the single most important number — don't let the assistant guess it.
4. **Your runtime/inference stack**, if you know it (e.g. `llama.cpp`/GGUF, `faster-whisper`, plain Hugging Face `transformers` + `bitsandbytes`, ONNX Runtime). If you're not sure yet, say so and ask the assistant to recommend a stack-neutral option, or pick a stack first.

Optional: whether transcription accuracy or generation quality matters more if both can't be fully preserved, and any target end-to-end latency.

## Instructions for the assistant (paste this part in full)

You are helping a developer pick a post-training-quantization (PTQ) method for an ASR model and a small LLM that must run together on one memory-constrained device. Follow these steps exactly:

1. **Confirm scope.** If the ASR model, LLM, or hardware RAM figure is missing or vague, ask for it before doing anything else. Do not assume a model identity or a RAM number.
2. **Set a memory budget.** Take the stated hardware's total RAM, subtract a reasonable OS/app overhead (state this as an assumption, e.g. "reserving ~1.5-2GB for OS + app on an 8GB device"), and treat the rest as the combined ceiling both quantized models plus runtime overhead (KV-cache, audio buffers) must fit under.
3. **Research the ASR model's quantization options.** Search for current, real benchmark data on this model or its closest sibling size — in particular Qualcomm's Edge-ASR benchmark (arXiv 2507.07877, which tested 8 PTQ methods across Whisper/Moonshine variants) and any dedicated Whisper PTQ comparison (e.g. arXiv 2511.08093, comparing dynamic int8/Quanto, static quantization, nf4, and int3 on Whisper-small). Record the exact method names and WER deltas reported — do not invent numbers.
4. **Research the LLM's quantization options.** Check the model's own Hugging Face model card (which usually lists GGUF/GPTQ/AWQ variants with reported perplexity or benchmark deltas) and any public PTQ comparison at that parameter size. Record exact method names and perplexity/eval deltas reported.
5. **Filter by runtime compatibility.** Drop any quant method that doesn't actually run on the user's stated stack — e.g. don't recommend GPTQ or AWQ for a CPU-only `llama.cpp` deployment; don't recommend a GGUF-only format for a plain `transformers` + `bitsandbytes` pipeline.
6. **Estimate combined memory for 2-3 surviving pairs.** For each (ASR method, LLM method) pair: parameter count × bits-per-weight ÷ 8 for each model, add a stated overhead assumption (roughly 10-20% for activations/buffers), sum both. Compare the total against the budget from step 2.
7. **Rank the pairs that fit the budget** using the cited accuracy deltas from steps 3-4 — not guesses. If the user said accuracy matters more on one side (e.g. transcription errors compound into bad LLM input), weight toward preserving that side's accuracy and say so.
8. **State the honest caveat.** No public benchmark currently measures this exact ASR+LLM pair loaded together on this exact hardware — say plainly that this recommendation is a synthesis of separately-measured components plus a memory estimate, not a verified joint result. Name the one concrete validation step: load both quantized models simultaneously on the actual target hardware and measure peak resident memory plus end-to-end latency on a real audio-plus-text sample.
9. **Double-check your own answer** before sending it: every WER/perplexity/memory number is tagged either `[cited: source]` or `[estimated]`; the recommended methods actually run on the stated stack; the RAM figure used matches exactly what the user gave you.

## Expected output format

Return a single response with these sections, in order:

1. **Inputs recap** — one line confirming the ASR model, LLM, hardware tier + RAM, and runtime stack you're answering for.
2. **Memory budget** — the RAM ceiling you used and the overhead assumption, clearly labeled as a rule-of-thumb.
3. **Recommended pairing** — a table: Model | Recommended quant method | Bit-width | Source for the accuracy delta | Estimated memory.
4. **Expected tradeoffs** — WER delta for the ASR pick, quality/perplexity delta for the LLM pick, combined estimated memory vs. your budget, each tagged `[cited: source]` or `[estimated]`.
5. **Confidence and validation step** — one paragraph stating this is a synthesis, not a jointly-benchmarked result, plus the exact on-device check to run before shipping.
6. **Sources** — a bulleted list of every paper, model card, or doc you actually consulted, with links.

## What this will not do

- It will not guess your hardware's RAM or your target model names — it will ask if either is missing.
- It will not hand you a number without saying whether it's a cited figure or an estimate.
- It will not recommend a quantization format your stated runtime can't actually run.
- It will not claim your exact model pairing has been benchmarked together anywhere — because, as of this writing, no public source has done that. It will tell you the one real-world check that replaces guessing.
