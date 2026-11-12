# Native-Format Preserving Quantizer for Fine-Tuned MoE Checkpoints

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models.md · P6
- **Maturity verdict**: PARTIAL — `vllm-project/llm-compressor` is a large, maintained production quantization framework, but the specific capability (auto-detecting and preserving a fine-tuned checkpoint's own native mixed-precision tensor layout through RTN quantization) only exists as a hand-built, unmerged one-off (`DSV4FlashNativeQuantizer`) inside a single GitHub proposal, not a general reusable feature.
- **Format**: PROJECT

## The Gap
On GitHub (`vllm-project/llm-compressor#3372`, 7 comments, 2026-10-23), an engineer fine-tuning a DeepSeek-V4-Flash checkpoint via ms-swift had to build a from-scratch quantizer class after manually inspecting tensor names, shapes, dtypes, scales, and config just to apply RTN quantization without breaking the model's native mixed-precision format. No existing converter in the ecosystem's dominant quantization framework handled "take an arbitrary fine-tuned MoE checkpoint and quantize it while preserving whatever native format it was trained with" as a general, reusable path — every team hitting this has to redo the tensor-forensics step themselves.

## The Project
A format-detection-and-quantization toolkit that sits in front of (or as a contributed module to) `llm-compressor`: point it at a fine-tuned checkpoint directory, and it inspects the actual tensor metadata (names, shapes, dtypes, per-tensor/per-block scale layout, config.json quirks introduced by the fine-tuning framework) to infer the model's native mixed-precision scheme, then emits a matching RTN quantization recipe instead of forcing the checkpoint through a generic quantization format that silently degrades or breaks compatibility. The centerpiece is the detection step — a library of per-architecture "fingerprints" (starting with DeepSeek-V3/V4-class and other popular open-weight MoE families) plus a fallback heuristic inspector for unrecognized formats, so the same tool that today requires a bespoke multi-day investigation becomes a one-command check.

## Tangible Impact
**Population**: ML infra teams fine-tuning open-weight MoE models (DeepSeek-V3/V4-class, Qwen3-MoE, Mixtral-derived architectures) for production deployment — a fast-growing group given how much current fine-tuning tooling (ms-swift, LLaMA-Factory, Axolotl) now targets MoE checkpoints, but one with no size estimate better than "every team that fine-tunes and then quantizes a MoE checkpoint for self-hosted serving."
**Mechanism**: Removes the multi-day manual tensor-forensics step (inspecting dtypes/scales/config by hand) that currently stands between "I fine-tuned a checkpoint" and "I can deploy a quantized version without quietly losing accuracy or breaking downstream serving compatibility" — the exact work the GitHub proposal's author had to do from scratch.
**Measure**: (1) time from fine-tuned checkpoint to validated quantized checkpoint, compared against the manual baseline documented in the source issue; (2) accuracy delta (perplexity/eval-suite score) between native-format-preserving quantization and the generic-format fallback most teams use today; (3) number of distinct MoE architectures the fingerprint library correctly auto-detects without manual intervention.

## Why Now
MoE fine-tuning has become the default path for teams adapting open-weight frontier-adjacent models (DeepSeek-V3/V4, Qwen3-MoE) rather than training from scratch, and the quantization step for serving those checkpoints is now the long pole — the source issue is a live, unresolved example from the ecosystem's own largest quantization project, not a hypothetical.

## MVP Sketch
Scope: a Python CLI (`native-quant inspect <checkpoint-dir>` / `native-quant run <checkpoint-dir>`) built as a thin layer over `llm-compressor`'s existing RTN implementation, covering 2-3 popular MoE architectures to start (DeepSeek-V3-class, one Qwen3-MoE variant). Stack: Python, `safetensors`/`transformers` for tensor introspection, `llm-compressor` as the quantization backend. Single validating experiment: take a fine-tuned checkpoint in each covered architecture, run it through (a) the tool's detected native-format recipe and (b) the generic default quantization path, and compare eval-suite scores and serving compatibility — if native-format preservation doesn't measurably beat the generic path, the premise is wrong.

## Risks & Open Questions
- The fingerprint library only scales to architectures someone has deliberately added — coverage could permanently lag the pace of new open-weight MoE releases.
- `llm-compressor` maintainers may already be planning (unannounced) to generalize this internally, which would shrink the gap fast; worth checking the repo's roadmap/issues before committing resources.
- Unclear how large the accuracy/compatibility delta actually is in practice — the MVP experiment is explicitly designed to kill the idea if the delta is negligible.
- Enterprise teams with this exact problem may already have in-house scripts (like the source issue's author) that never get open-sourced, meaning the "unmet need" could be real but privately already solved per-company.
