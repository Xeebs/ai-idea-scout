# Scenario 1: Offline voice-journaling app on a Raspberry Pi 5

## Input

A solo developer building an offline voice-journaling app provides:

1. **Target ASR model**: Whisper-base.en
2. **Target LLM**: Qwen2.5-0.5B-Instruct (used to clean up and lightly rewrite the raw transcript into journal-ready prose)
3. **Hardware tier**: Raspberry Pi 5, 8GB RAM model, no attached accelerator
4. **Runtime stack**: `llama.cpp`/GGUF for the LLM; `faster-whisper` (CTranslate2) for the ASR model — both chosen because they're the two most common CPU-friendly runtimes on a Pi
5. **Priority stated**: transcription accuracy matters more than writing polish, since a bad transcript poisons everything downstream.

## Pass criteria

- [ ] The response confirms all four inputs in a one-line recap before giving a recommendation (does not silently assume anything).
- [ ] A memory budget is stated using the 8GB figure, with a clearly labeled OS/app overhead assumption (not treated as fact).
- [ ] The recommended ASR quant method is compatible with CTranslate2/`faster-whisper` (e.g. an int8 or int8_float16 CTranslate2 quantization), not a GGUF-only or GPU-only method.
- [ ] The recommended LLM quant method is a GGUF variant compatible with `llama.cpp` (e.g. Q4_K_M, Q5_K_M, Q8_0), not GPTQ/AWQ (which are GPU-oriented and not the stated stack).
- [ ] At least one real cited source appears (e.g. Qualcomm's Edge-ASR benchmark arXiv 2507.07877, or the Whisper-small PTQ comparison arXiv 2511.08093, or the Qwen2.5-0.5B Hugging Face model card's reported quant variants) with a WER or perplexity delta attached to it.
- [ ] Every numeric claim is tagged `[cited: ...]` or `[estimated]` — no bare unlabeled number.
- [ ] The response explicitly states that this exact ASR+LLM pairing has not been jointly benchmarked anywhere, and names the concrete on-device validation step (load both quantized models together on an actual Pi 5, measure peak RAM + end-to-end latency on a real voice sample).
- [ ] Because the user flagged transcription accuracy as the priority, the response's ranking logic favors a lighter/less aggressive ASR quantization over squeezing extra budget into the LLM, and says so explicitly.
- [ ] A sources list with links appears at the end.

## Fail conditions (any one of these fails the scenario)

- Recommending a quant method the stated runtime can't actually run (e.g. GPTQ for `llama.cpp`, or a `bitsandbytes`-only format for `faster-whisper`).
- Presenting any WER/perplexity/memory number without a cited-or-estimated tag.
- Claiming or implying this specific pairing has been directly, jointly benchmarked in a public source.
- Skipping the memory budget step and jumping straight to a recommendation.
- Ignoring the stated accuracy priority in the final ranking.
