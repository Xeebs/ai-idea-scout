# GPU Audit: A Bloat & Real-GPU-Utilization Diagnostic for Packaged Local-Model Desktop Apps

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models-ii.md · P3
- **Maturity verdict**: PARTIAL — vendor-narrow partial fixes exist (Microsoft's Foundry Local, ~20MB, Windows-oriented; mlxstudio, a ~2MB-shell native Swift/Metal app) and standard guidance (download-on-first-run, quantization, GPU backends) addresses the underlying causes, but none directly verifies real GPU utilization or diagnoses bloat in an already-packaged MLX/GGUF build, and the original complainant's build still ships a 5.3GB DMG with "barely any GPU speedup."
- **Format**: PROJECT

## The Gap
A developer who shipped a Gemma 4 Mac app that renames screenshots using a local model found the distributable ballooned to a 5.3GB DMG and that Metal/MLX GPU acceleration delivered barely any real speedup over CPU, despite the hardware supporting it — a first-person builder complaint about the packaging/runtime layer itself, not the model (via secondary coverage of the original Show HN post, 2026). No tooling surfaced for "verify a packaged local-model app is actually using the GPU" or "break down why this bundle is this large," even though generic bundling-bloat fixes (Foundry Local, mlxstudio) exist for other stacks.

## The Project
A Mac-first diagnostic CLI that takes an already-packaged local-model `.app`/DMG and produces two concrete reports instead of leaving developers guessing from user complaints: (1) a bundle-size breakdown by directory/framework/model-weights vs. runtime vs. app code, flagging duplicated or unnecessarily-bundled runtime libraries; (2) an instrumented test run (via Metal System Trace / `powermetrics` scripting) that reports what fraction of inference time actually executed on GPU vs. silently fell back to CPU, and why (missing Metal kernel path, unsupported quantization format, batch size too small to benefit). The output is an actionable fix list, not just a diagnosis.

## Tangible Impact
**Population**: Solo and small-team indie Mac developers shipping single-purpose native local-model utility apps — the same builder population documented shipping at least three such apps in one month (budgeting, screenshot-naming, bill-detection), a subset of whom will hit this specific bloat/GPU-underuse failure once they package a real build. This is a narrower slice than the general "embed one model" builder population and is single-source evidenced today, so the addressable group is smaller and less certain — likely dozens to low hundreds of active builders findable via Show HN/IndieHackers per year.
**Mechanism**: Today a developer only discovers bloat and poor GPU utilization after shipping, via their own dissatisfaction or user complaints about download size/battery. A pre-release audit catches both before the DMG goes out, turning a vague "it's heavy and slow" into a specific, fixable finding (e.g., "42% of your DMG is a duplicated Metal runtime; your inference calls never hit the GPU path because quantization format X lacks a Metal kernel").
**Measure**: (1) median installer-size reduction after applying flagged fixes; (2) % of audited apps that move from unverified to confirmed-GPU-accelerated inference; (3) number of indie developers who run the tool against a real shipped or pre-release build within a defined window.

## Why Now
The same capability threshold that let three solo developers ship task-embedded local models in one month (P2) is producing real builds with real packaging mistakes fast enough that no tooling has caught up — the complaint is fresh (this cycle) and the vendor fixes that exist (Foundry Local, mlxstudio) are narrow enough that this exact failure mode is still shipping in production.

## MVP Sketch
Smallest version: a Mac-only CLI, `mlx-audit <app.app>`, that (1) parses the `.app` bundle to produce a size breakdown by top-level directory/framework and flags duplicate runtime libraries, and (2) wraps a scripted launch of the app with GPU-counter instrumentation to report the GPU-vs-CPU split of inference time during a fixed test input. Single experiment: run it against 3 real shipped local-model Mac apps recruited from recent Show HN posts, confirm it correctly flags the known Gemma 4 screenshot-namer's bloat/GPU issue, and check whether the resulting fix list is something a developer can act on within a week.

## Risks & Open Questions
- Single-source evidence (one developer's complaint) — unconfirmed whether this is a widespread failure mode or idiosyncratic to that one app's architecture choices.
- "Barely any GPU speedup" may sometimes be a genuine workload characteristic (small model, small batch) rather than a fixable bug — the tool risks flagging non-problems developers can't actually act on.
- Building reliable GPU-utilization instrumentation across heterogeneous runtimes (llama.cpp+Metal, MLX, CoreML) is itself nontrivial — the diagnostic layer could end up as much engineering work as the packaging fixes it recommends.
- If developers route around the problem by adopting Foundry Local or mlxstudio directly rather than auditing their current stack, the addressable need for a standalone auditor shrinks.
- Overlaps conceptually with P2's packaging framework (embedded-model-packaging-framework.md) — if that framework ships with built-in bloat/GPU checks by default, this becomes a feature of that project rather than a standalone tool; worth revisiting after P2 progresses.
