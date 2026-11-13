# Fit Pack: One-Command Quantization Auto-Selection and Launch for 8–16GB Consumer GPUs

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Small & local models
- **Source**: research/2026-11-13-small-and-local-models.md · P4
- **Maturity verdict**: PARTIAL — `llmfit` evaluates memory requirements and picks a GGUF level for single LLMs but explicitly skips pre-quantized AutoRound/AWQ/GPTQ and has no confirmed FP8 or multimodal (diffusion+TTS) support; Intel's AutoRound can *export* GGUF/AWQ/GPTQ/FP8 from one run but doesn't auto-select by VRAM; LM Studio/Ollama show VRAM estimates but don't auto-pick across the full FP8/Int8/GGUF/AutoRound matrix for a full multimodal pipeline. The specific ask — one command, full multimodal pipeline, auto-selected quant format for an 8–16GB card — remains the actively-open, unresolved `vllm-project/vllm-omni` issue #10008.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads model size/config metadata from the Hugging Face Hub API (mature, public, no auth needed for most repos) and detects local hardware directly via `nvidia-smi`/`rocm-smi`/platform APIs (no external service — this is local system introspection, not a connector that needs building). No manual data entry beyond the user naming which models/pipeline they want to run.

## The Gap
`vllm-project/vllm-omni` issue #10008 ("Local serving on RTX laptops (8–16 GB, Linux/WSL2)," 2026-11-08, 27 comments) explicitly scopes an unmet need: "Make a full pipeline ... runnable with one command on a single 8/12/16 GB RTX GPU ... so FP8/Int8/GGUF/AutoRound all qualify per the quantization matrix." Today that choice is manual, per-card, per-model-combo trial and error — forum-crowdsourced the same way hardware-throughput questions are (per the digest's P1 evidence). Real partial tooling exists in pieces (`llmfit`, AutoRound's exporters, LM Studio/Ollama's VRAM estimates) but nothing closes the loop end-to-end for a full multimodal pipeline on a specific consumer card.

## The Project
A CLI, `fitpack`, that takes a pipeline spec (e.g. `--llm llama-3.1-8b --tts xtts-v2 --diffusion sdxl`), detects the local GPU and its free VRAM, and consults a maintained compatibility matrix mapping each component + VRAM tier to the quantization format and artifact that actually fits with headroom (GGUF via llama.cpp, AWQ/GPTQ/FP8 via AutoRound/vLLM-omni) — then downloads the right pre-quantized artifact (or triggers a one-shot AutoRound conversion if none exists) and launches the whole pipeline with the correct runtime flags in one command. The novel piece is the cross-component, VRAM-budget-aware selection logic itself, not reimplementing any inference engine — `fitpack` is a thin orchestration layer over llama.cpp/AutoRound/vLLM-omni/Ollama.

Core components: hardware prober (`nvidia-smi`/`rocm-smi` parsing), a versioned compatibility matrix (model/component → VRAM tier → best format + artifact source), a VRAM-budget allocator that splits the total budget across concurrent pipeline components with headroom reserved, and a launcher that emits/calls the correct per-component runtime invocation.

## Tangible Impact
**Population**: Hobbyist and indie developers running local multimodal AI pipelines on 8–16GB consumer/laptop GPUs (RTX 3060/4060/4070 laptop and desktop tiers) — the exact hardware tier the vllm-omni issue scopes. r/LocalLLaMA alone has ~500K+ members and VRAM-constrained hardware threads are a recurring top-level category there; GPU market-share data (Steam Hardware Survey, Jon Peddie Research GPU shipment reports) puts 8–16GB cards as the dominant consumer gaming/creator tier, putting the addressable population in the hundreds of thousands who want to run local AI on hardware they already own.
**Mechanism**: Replaces hours of manual format trial-and-error (download a GGUF, OOM, try a smaller quant, try FP8, repeat per component) with a single command that gets it right the first time by reasoning over actual VRAM budget across the whole pipeline at once, not one model in isolation.
**Measure**: (1) median time-to-first-successful-multimodal-launch vs. a manual-selection baseline; (2) first-attempt OOM/crash rate across a test matrix of common GPU tiers × pipeline combos; (3) number of supported hardware/pipeline combos that launch successfully out of the box within 90 days of release.

## Why Now
Multimodal local pipelines (LLM + TTS + diffusion stacked together) have only recently become common enough on consumer hardware that the quantization-format decision now has to be made jointly across components instead of per-model — exactly what the fresh (2026-11-08) vllm-omni issue is scoping, and exactly the gap the existing single-model tools (`llmfit`, LM Studio, Ollama) don't cover.

## Skill Angle
A Claude Code skill that, given a user's GPU model/VRAM and a desired pipeline (e.g. "I have a laptop 4070 8GB, I want Llama-3-8B + XTTS + SDXL running locally"), reasons through the same compatibility-matrix logic and outputs a recommended quant format per component plus the exact commands/flags to run today's existing tools (AutoRound export command, llama.cpp invocation, etc.) — without building or maintaining any persistent launcher. This is the fast, zero-infrastructure way to validate the matrix logic is correct before committing to the full `fitpack` CLI; the project is the actual automated, repeatable tool that detects hardware and launches for you.

## MVP Sketch
A Python CLI covering just two components (one LLM family + one TTS model) across 4 common 8–16GB card configs. Hardcode the compatibility matrix for ~10 popular model+quant combos initially (hand-verified, not auto-generated). Single experiment: have 5 people from r/LocalLLaMA run `fitpack` against their own card and a 2-component pipeline, and measure whether it launches successfully on the first attempt versus their own prior manual attempt.

## Risks & Open Questions
- The full matrix (every model × every quant format × every GPU tier) is combinatorially large; the MVP must stay narrow (2 components, ~10 combos) or it becomes an unmaintainable spreadsheet.
- `vllm-omni` itself may ship exactly this natively before an independent build gains traction — worth checking that issue's resolution before investing heavily; if it ships, the better outcome may be contributing the matrix logic upstream rather than competing.
- Hardware detection on WSL2/Windows GPU passthrough is notoriously flaky (the issue's own title flags Linux/WSL2 specifically) — may need per-platform fallback logic that adds real engineering cost.
- New model/quant releases will stale the matrix quickly without an update cadence — this needs a lightweight community-contribution path (PR-a-row) from day one, not a one-time hand-built table.
