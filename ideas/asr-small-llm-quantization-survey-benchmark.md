# Edge Stack Survey: A Combined ASR + Small-LLM Quantization Benchmark for Edge Deployment

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models-2.md · P4
- **Maturity verdict**: PARTIAL (raw material exists in pieces — Qualcomm's Edge-ASR benchmark (arXiv 2507.07877) covers 8 PTQ methods across Whisper/Moonshine variants on 7 datasets, a separate paper compares 4 PTQ libraries for Whisper-small, and small-LLM quantization documentation is abundant elsewhere — but no primary source combines ASR + small-LLM quantization methods into one comparative reference for builders who need both together)
- **Format**: BOTH
- **Data Sources**: CONNECTED — pulls open ASR and small-LLM model weights directly from HuggingFace Hub (mature, freely accessible) to run the comparative benchmark; the companion skill's only manual input is the user naming their target model pair and hardware tier (e.g. "Whisper-tiny + Qwen2.5-0.5B on a Raspberry Pi 5").

## The Gap
A GitHub issue (`rahulsharmavishwakarma/vesper#265`) states the need directly: "we need a primary-source survey of weight quantization methods for both ASR and small LLMs: what each method is, what it needs (checkpoint format, calibration data, etc.)" — framed as groundwork the author needs before adding "custom adapters for the new sub-1B ASR and writing candidates." WebSearch confirmed strong material exists for each half separately (Qualcomm's Edge-ASR benchmark for ASR, abundant small-LLM quantization docs elsewhere) but nothing combines them into one reference for someone building a device that needs both a speech-input and a text-generation model quantized together under one memory/compute budget.

## The Project
A living, reproducible benchmark matrix that runs standard PTQ methods (GPTQ, AWQ, GGUF variants, bitsandbytes) across paired ASR models (Whisper Tiny/Base/Small, Moonshine Tiny/Base) and small writing/LLM models (sub-1B to ~3B class), measured together on the same reference hardware tiers (phone-class, SBC-class like Raspberry Pi, laptop-CPU-class) — reporting WER, perplexity, latency, and memory footprint for each combination so a builder picks a calibrated pairing instead of researching each half from scratch and guessing at how they interact under one shared memory budget.

Core components: (1) a reproducible benchmark harness extending Qualcomm's Edge-ASR methodology to also cover the LLM half, (2) a published comparison matrix keyed by hardware tier, (3) a decision helper that recommends a quant-method pairing given a target model pair and hardware constraint.

## Tangible Impact
**Population**: Indie developers and small teams building offline voice-input-plus-text-generation apps for consumer and embedded hardware — dictation-and-rewrite tools, voice journaling apps, offline meeting-note assistants — targeting phones, Raspberry Pi-class SBCs, or laptops without discrete GPUs, where both an ASR model and a writing model must fit the same device budget simultaneously.
**Mechanism**: Today these builders separately dig through ASR-specific quantization research and generic LLM quantization docs with no source telling them, for their specific hardware tier, which PTQ method combination hits the best combined WER/perplexity-per-megabyte/latency tradeoff when both models run together — the exact groundwork the `vesper#265` issue describes needing before it can even start adding new model candidates. A combined, hardware-tiered matrix collapses that research into a lookup.
**Measure**: (1) time to pick a quant-method pairing for a target model pair and hardware tier (target: under an hour via the matrix/skill, versus the multi-day research the issue's filer describes needing); (2) median WER/perplexity improvement at matched combined memory footprint versus naively applying the same quant method to both models independently; (3) number of hardware tiers and model pairs covered in the published matrix.

## Why Now
Sub-1B ASR and writing-model candidates are maturing fast enough in 2026 that a real project (`vesper`) is actively trying to adopt new ones and hitting this exact documentation gap right now — the raw benchmark material (Edge-ASR, Whisper-small quant comparisons) only became available in the last several months, making the synthesis newly possible rather than something that should already exist.

## Skill Angle
A companion research-synthesis skill: given a user's named target ASR model, target writing model, and hardware tier, the skill queries the project's published comparison matrix (or, if the pairing isn't yet benchmarked, synthesizes current primary-source data the way the `vesper` issue originally asked for) and returns a recommended quant method per model plus the expected WER/perplexity/latency/memory tradeoff. This differs from the project: the skill is a one-shot recommendation given a specific pairing; the project is the maintained, continuously-expanding benchmark matrix and reproduction scripts behind it.

## MVP Sketch
Two to three weeks, 1–2 people: pick 3 ASR models (Whisper Tiny/Base, Moonshine Tiny) and 3 small LLMs (sub-1B to ~1.5B class), apply 3 PTQ methods to each, measure WER/perplexity/latency/memory on one reference hardware tier (e.g., Raspberry Pi 5), and publish the first matrix plus the decision-helper skill against it. Stack: Python, HuggingFace `transformers`/`optimum`, `llama.cpp`/GGUF tooling, a reference SBC for actual on-device measurement rather than simulated numbers.

## Risks & Open Questions
- Combined ASR+LLM memory/compute interaction on real hardware may not be well-approximated by benchmarking each model in isolation — the project needs to actually run both loaded together, not just sum separate numbers.
- Qualcomm's Edge-ASR benchmark methodology may be license-restricted or hardware-specific (Snapdragon-tuned) in ways that don't generalize cleanly to the Raspberry Pi/laptop-CPU tiers this project targets.
- The gap is narrower than it first appears — most of the hard half (ASR) already has strong primary-source data; the actual unique contribution may be smaller (the combination and the LLM-side measurement) than the "nothing exists" framing implies.
- Keeping the matrix current as new sub-1B ASR/LLM candidates ship monthly requires ongoing maintenance, not a one-time publish — scope the MVP honestly as a snapshot, with a clear update cadence commitment.
