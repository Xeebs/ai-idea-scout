# Fit Tune: A Device-Aware Fine-Tuning Method and Quantization Recipe Selector

Every team fine-tuning an open-weight model on a device they've already chosen runs the same guessing game: try full fine-tuning, watch it OOM, try LoRA, hit an accuracy cliff at 4-bit quantization, try QLoRA at 8-bit, and finally — hours and several failed training runs later — land on something that fits. Two separate academic papers in 2026 built a pipeline to automate exactly this decision. Neither released the tool.

## The Gap

A 2026 MobiUK paper describes a "device-aware pipeline that uses a cloud teacher to generate fine-tuning data, then picks a fine-tuning method and quantization based on the target hardware," validated on a healthcare fraud dataset. A separate late-2026 preprint builds the equivalent for on-premise CPU inference in a manufacturing setting. Both independently prove the same underlying idea — that the fine-tuning-method-and-quantization decision can be made by measurement rather than guesswork — works on real data. Neither ships it as something a team outside the paper's own authors can run.

Meanwhile the state of the art for everyone else is manual trial and error: pick a method, pick a quantization level, run it, and find out the hard way whether it fits the device or holds up on the task. That's precisely the friction both papers' own internal pipelines were built to remove — they just kept the fix to themselves.

A web search for anything general-purpose that takes "my device plus my task" and returns a validated recipe turned up only narrow, vendor-locked alternatives: AMD's Quark Auto-Search handles precision/calibration search for AMD hardware only, with no fine-tuning-method selection at all. ESP-DL AutoQuant is scoped to Espressif's ESP32 chips and does quantization only. The one paper that explicitly combines both decisions, HAQA (arXiv 2601.03484), states plainly that its code isn't released. Nothing ties the two halves of this decision — method and quantization — together in a tool anyone can install.

## The Project

Fit Tune is a CLI/library that profiles a target device — VRAM/RAM, compute class, whether it's training-capable or inference-only — and a user-supplied slice of their actual task data, then runs a battery of cheap comparative probes: short LoRA, QLoRA, and (where the device allows) full fine-tune training runs on a tiny slice of the user's own data, each at one or two candidate quantization levels. It scores each probe against a held-out slice of the same data and reports which method-plus-quantization combination actually fits the device's memory budget and performs best — instead of asking the user to discover the OOM or the accuracy cliff themselves.

The core idea that makes this more than a lookup table: the recommendation is a *measured probe*, not a static rule keyed off device specs alone. It adapts to how hard the user's actual task turns out to be, which a raw VRAM number can't tell you.

The pipeline has four pieces: a device profiler (VRAM/RAM/compute-class detection); a probe-run orchestrator that trains tiny slices under each candidate combination while timing and measuring memory headroom; a held-out eval scorer against the user's own sample; and a recipe report — recommended method, quantization level, estimated full-run time and memory headroom — that ships with the raw probe results attached, so the recommendation is auditable rather than a black box.

## Tangible Impact

**Population**: Small ML teams and solo developers fine-tuning open-weight models (Llama/Qwen/Gemma-class, 1B-13B) for a narrow task, who have one specific target device in mind — a single consumer GPU, a specific cloud instance type, or an on-premise edge box — and today only arrive at a working method/quantization combination after at least one failed attempt. This is the exact friction both source papers set out to remove in their own narrow domains, just never generalized.

**Mechanism**: Converts "try full fine-tune, hit OOM, try LoRA, hit an accuracy cliff at 4-bit, try QLoRA at 8-bit, finally works" into a single automated probe pass that surfaces the same answer in minutes, because the comparison runs on tiny data slices before any full-scale commitment.

**Measure**: (1) number of failed full-scale training attempts — OOM or below-threshold eval score — avoided per project versus a team's own prior manual-guess baseline; (2) wall-clock time from "device + task description" to a validated recipe recommendation, targeting under 30 minutes on commodity hardware; (3) eval-score delta between the tool's recommended combination and whatever combination the team would have tried first by guessing, measured on the user's own held-out examples.

## Try It

A companion Claude Code skill already exists at `skills/device-aware-finetune-quant-recipe-selector/` — the **Fit Tune Advisor**. Its one-line description: "Recommends a starting fine-tuning method (full / LoRA / QLoRA) and quantization level for a given target device and task, before any training run starts. Use when someone has a GPU/instance in mind and a fine-tuning task but hasn't picked a method yet and wants to avoid discovering an OOM or accuracy cliff the hard way."

This is the one-time advisory half of the idea, not the full probe-based tool: it uses known VRAM-footprint rules of thumb and quantization-tradeoff patterns to give you a first guess worth validating, rather than running any actual training. To use it, either drop the `device-aware-finetune-quant-recipe-selector` folder into `~/.claude/skills/` for Claude Code, or paste the contents of its `README.md` into any AI chat tool and hand over your device, model, task type, and a few real example rows.

The full probe-running CLI described above — the part that actually trains tiny slices and measures the result — remains unbuilt; the skill is the lightweight advisory layer you'd reach for first.

## Why Now

QLoRA and LoRA are now cheap enough on consumer hardware that running several short comparative probes instead of committing to one long guessed training run is genuinely affordable. Two independent 2026 academic papers just proved the joint method-plus-quantization decision is worth automating on real domains — but neither released the tooling, leaving the general-purpose version sitting unbuilt despite the underlying technique already being validated twice, on two unrelated domains, by two unrelated teams.

## Worth Weighing

Short probe runs on tiny data slices may not reliably predict full-run accuracy — this is the central open question, and the proposed MVP experiment is designed explicitly to check whether probe-scale signal correlates with full-scale outcome before anyone should trust the recommendation. Both source papers validate on exactly one domain each, so the general-purpose recipe logic may not transfer cleanly across very different task types — classification, generation, extraction — without broader validation of its own. There's also a real possibility that `vllm-project/llm-compressor` or a similarly well-resourced framework generalizes into this space given how close it already sits to quantization tooling; that's worth rechecking before investing past a minimal prototype. And training-time device profiling is less standardized than inference-time VRAM estimation, which is part of why the probe-based approach exists in the first place — but it also means every use of the tool costs real GPU time just to get an answer.

---

Surfaced from `research/2026-11-18-small-and-local-models.md`, pattern `P7`.
