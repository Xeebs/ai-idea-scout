# Checkpoint Check: A Consumer-Friendly Interpretability Auditor for Community GGUF Models

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models.md · P7
- **Maturity verdict**: PARTIAL — NeuronDump is a real but solo/early tool (3 points, single hobbyist repo) combining a navigable 3D graph with live ablation on everyday local GGUF files; mature mechanistic-interpretability libraries exist for pieces of this (TransformerLens, CircuitsVis, FailSpy/abliterator, Meta's LM Transparency Tool) but none package into a consumer-friendly auditing tool for people running third-party local model files.
- **Format**: BOTH

## The Gap
Hacker News, "NeuronDump: Open a local LLM as a 3D graph, cut parts, see what breaks" (3 points, 2026-10-25), shows a hobbyist building hands-on interpretability tooling for local GGUF models used with Ollama/LM Studio/llama.cpp — the exact everyday format millions of people download pre-quantized from Hugging Face without any way to verify what's actually inside. Serious mechanistic-interpretability libraries exist, but they target researchers working with raw model weights in research frameworks, not people who just pulled a community GGUF quant and want to know whether it does anything it shouldn't before pointing it at real data.

## The Project
A local-model auditing tool that wraps mature mechinterp libraries (TransformerLens-style activation access, CircuitsVis-style visualization, ablation techniques from FailSpy/abliterator) behind a workflow built for GGUF consumers rather than research-framework users: load any local GGUF model, run a library of probe prompts designed to surface known backdoor/trigger patterns (e.g., unusual completions on specific trigger tokens, refusal-suppression circuits, embedded instructions), and get a readable report flagging anomalous activation patterns worth a closer look — with the option to drop into an interactive ablation view (NeuronDump's core idea) for anything flagged. The novel pattern is making circuit-level auditing a push-button step in the local-model download workflow, not a research exercise.

## Tangible Impact
**Population**: Self-hosted local-LLM users and small teams who download community-quantized GGUF checkpoints from Hugging Face to run via Ollama/LM Studio/llama.cpp — a large and growing population given Ollama's and LM Studio's download counts, and one with a documented real risk: 2025–2026 reporting has repeatedly surfaced poisoned/backdoored quantizations uploaded to public model hubs.
**Mechanism**: Gives non-research users a way to screen a downloaded checkpoint for planted trigger behaviors before deploying it (personal assistant, internal tool, agent backend), closing the gap between "mechanistic interpretability can detect this in principle" and "an ordinary local-LLM user has no practical way to check."
**Measure**: (1) detection rate on a labeled benchmark of models with known planted trigger behaviors vs. clean models (true/false positive rate); (2) time for a non-research user to run a full audit end-to-end; (3) number of community-reported suspicious GGUF uploads the tool correctly flags in a live trial against Hugging Face's public hub.

## Why Now
Community GGUF quantization has become the dominant distribution channel for local models, model-supply-chain poisoning incidents are an active 2025–2026 concern, and the mechinterp libraries needed to build the detection core (TransformerLens, CircuitsVis, abliterator) are mature and stable enough to compose into a product rather than requiring new research.

## Skill Angle
A Claude Code skill version handles the analysis half without the full interactive 3D UI: given a path to a local GGUF model (or the model loaded via Ollama) and a description of a suspected anomalous behavior ("this model refuses normally but complies when I say X"), the skill writes and runs the probing/ablation code (via the mechinterp libraries) to localize which layer/circuit produces the behavior and returns a report naming the suspect component and confidence. This differs from the project: the project is the persistent, general-purpose GUI auditing tool meant for routine pre-deployment screening of any model; the skill is a one-shot investigative aid for someone who already has a specific behavior to chase down and wants Claude to do the circuit-tracing legwork.

## MVP Sketch
Scope: a CLI + minimal web report (not the full 3D explorer yet) that loads a GGUF model via llama.cpp's Python bindings, runs a seed set of 10–15 known trigger-pattern probes drawn from published backdoor-LLM research, and flags activation outliers. Stack: Python, llama-cpp-python, a small adapted slice of TransformerLens-style hooks compatible with quantized GGUF inference. Single validating experiment: build or source 2–3 deliberately backdoored test checkpoints (several exist in academic backdoor-LLM papers) plus clean controls, and measure whether the probe set reliably distinguishes them — if detection is no better than chance, the probe-library approach needs rethinking before any UI work.

## Risks & Open Questions
- Backdoor detection via probing is an open research problem even in full-precision models; GGUF quantization may further obscure or alter the exact signal the probes rely on — false negatives could make the tool actively misleading if marketed as a guarantee.
- TransformerLens-style hooks are built for full-precision inference; adapting them to quantized GGUF weights without reimplementing large parts of the activation-access layer may be harder than it looks.
- Adoption depends on local-LLM users caring enough to run an extra step before using a model — if Ollama/LM Studio integrate basic provenance checks natively, this tool's reason to exist narrows.
- The two existing GitHub projects named in the digest's verdict (NeuronDump, abliterator) could converge toward this exact product on their own; worth checking their roadmaps before committing.
