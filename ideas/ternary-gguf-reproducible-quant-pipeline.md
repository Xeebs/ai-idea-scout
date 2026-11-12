# Second Source: A Reproducible, Verified Build Pipeline for Ultra-Low-Bit GGUF Quants

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models-2.md · P8
- **Maturity verdict**: PARTIAL (general multi-maintainer GGUF quant culture is mature — mradermacher, QuantFactory, and individual accounts already publish parallel quants, and tooling like AutoGGUF variants and llama.cpp's quantize script exists — but ultra-low-bit/ternary-specific support genuinely lags: Prism ML's own Ternary-Bonsai-8B-gguf card notes its Q2_0 format isn't yet in mainline llama.cpp, leaving independent reproduction of this specific niche blocked)
- **Format**: BOTH
- **Data Sources**: CONNECTED — pulls original FP16/BF16 base weights and existing community GGUF quant uploads directly from HuggingFace Hub (mature, freely accessible), and tracks/contributes to the llama.cpp GitHub repository for kernel support; no manual paste required beyond the user naming a target model repo.

## The Gap
A May-2026 third-party analysis of 265 r/LocalLLaMA posts cites a complaint that "only the author's own GGUF quants were available and hoped others would follow" — a named single-point-of-failure problem for ultra-low-bit (1-bit/1.58-bit ternary) model distribution, surfaced around the "Ternary Bonsai" family and community quants of larger models for constrained-VRAM cards. WebSearch confirmed general GGUF quant culture is mature (multiple independent maintainers routinely publish parallel quants of mainstream models), but the ternary-specific tooling isn't there yet: Prism ML's own model card for Ternary-Bonsai-8B-gguf states its Q2_0 format isn't merged into mainline llama.cpp, meaning the kernel support an independent maintainer would need to cleanly reproduce the quant doesn't fully exist.

## The Project
A reproducible build-and-verify pipeline for ultra-low-bit/ternary GGUF quants, paired with upstream contribution work to close the missing-kernel gap. The pipeline takes an original model's FP weights and a target ternary/1-bit quant spec, reproduces the quantization using the author's documented method, and runs a verification pass comparing the rebuilt quant's perplexity/task-accuracy against the original maintainer's published claims — flagging drift, corruption, or undisclosed changes. In parallel, the project contributes the missing Q2_0 (and related ternary) kernel support to mainline llama.cpp so independent reproduction stops depending on a single maintainer's fork or private build process.

Core components: (1) a reproducible quantization pipeline for ternary/1-bit formats, (2) a verification harness checking rebuilt quants against published benchmark claims, (3) upstream PR work for missing llama.cpp kernel support, (4) a public registry tracking which ternary models currently have ≥1 independently-verified second source.

## Tangible Impact
**Population**: Self-hosters and hobbyists running ternary/1-bit (BitNet-class) models on constrained consumer hardware, who currently depend entirely on one maintainer's (e.g., Prism ML's) GGUF build with no second source and no independent verification that the quant matches the claimed quality — the single-point-of-failure complaint explicitly cited in the r/LocalLLaMA post analysis.
**Mechanism**: If the sole maintainer of a given ternary quant goes inactive, ships a flawed build, or is compromised, there is currently no fallback and no way for a user to even check whether their downloaded weights match the claimed benchmark numbers. A reproducible build-and-verify pipeline plus upstream kernel support lets any independent maintainer produce and verify a second source, and lets end users verify what they downloaded, closing both the availability risk and the trust gap in one pass.
**Measure**: (1) number of ternary/1-bit model releases with ≥2 independently-verified GGUF builds (baseline: effectively 0 per the evidence gathered, i.e., genuine single points of failure); (2) median time from an original ternary model's release to a second independently-verified build being available (target: days, not indefinite); (3) whether the missing Q2_0 kernel work merges into mainline llama.cpp, removing the fork/private-build dependency entirely.

## Why Now
Ternary/1-bit model families (Ternary Bonsai and the broader BitNet b1.58 lineage) only became practically runnable and popular enough in 2026 to generate dedicated community complaint threads about distribution risk — the demand and the gap both emerged recently, and llama.cpp's own kernel backlog for this specific format means the window to contribute upstream support before someone else does (or before community interest moves on) is open now, not indefinitely.

## Skill Angle
A companion verification skill: given a model repo URL or model card for a downloaded ternary/1-bit GGUF file, the skill walks the user through reproducing a perplexity/task-accuracy check against the original maintainer's published claims, flagging any mismatch that could indicate a bad or tampered build. This differs from the project: the skill is a one-shot verification a user runs on a single downloaded file; the project is the maintained pipeline and upstream kernel contribution that make independent second-source builds possible at all.

## MVP Sketch
Three weeks, 1–2 people: pick the Ternary-Bonsai family as the first target, build a reproducible quantization script from its documented method, verify output against the model card's published benchmark numbers, and open a PR to llama.cpp adding or completing Q2_0 kernel support. Stack: Python/C++ matching llama.cpp's existing quantize tooling, HuggingFace Hub for weight access, llama.cpp's own eval harness for perplexity checks.

## Risks & Open Questions
- Ternary/1-bit quantization methods may have undocumented or proprietary steps (calibration data, specific rounding schemes) that make bit-exact reproduction harder than standard GGUF quant work — scope the MVP to "verifiably close" rather than assuming bit-exact reproduction is achievable.
- Upstream llama.cpp maintainers may have already-planned or in-progress Q2_0 kernel work that supersedes this project's contribution — check open PRs/issues before starting the kernel work to avoid duplicating effort.
- The niche may simply be too small (few ternary models, small user base) to sustain ongoing second-source maintenance — the registry component should track real demand (download counts, community requests) before over-investing in process.
- If a well-known quant maintainer (mradermacher, QuantFactory) independently starts covering ternary formats once llama.cpp support lands, this project's distinct value narrows to the verification harness and the upstream contribution, not the build pipeline itself.
