# Fits On My Card: Independent Hardware-Tier Verification for Local World Models

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models.md · P8
- **Maturity verdict**: PARTIAL — multiple well-resourced teams (Overworld, Skywork AI, InSpatio-WorldFM) are shipping real-time interactive world models with papers and HF releases, but none confirm RTX 3060-class performance specifically, none are independently evaluated, and none are integrated into mainstream local-inference tooling (Ollama/LM Studio-style ecosystems).
- **Format**: BOTH
- **Data Sources**: CONNECTED — web/GitHub/Hugging Face search for vendor-claimed hardware tiers and independent benchmark reports; a mature generic capability (standard search), not a bespoke API or MCP connector. (Backfilled 2026-11-12 — field was missing when this idea was first synthesized; derived from the skill-synthesizer's downstream classification.)

## The Gap
Reddit r/LocalLLaMA, "I'm releasing a Local World Model Ive been building that turns images into interactive videos you control in real time. It works on RTX 3060, 4060 and anything above" (2026-11-11), is a solo builder's claim about entry-level consumer GPU support for an emerging generative category. The established competitors in this space (Overworld's Waypoint line, Skywork's Matrix-Game, InSpatio-WorldFM) target mid-to-high-end cards (RTX 3090–5090) and report their own benchmarks with no third-party verification — meaning anyone with a genuinely entry-level GPU has no trustworthy way to know which, if any, of these claims actually hold on their hardware before investing setup time.

## The Project
An independent benchmark-and-packaging layer for local interactive world models: run every publicly released model (lucidml/gta, Overworld's lower-end variant, InSpatio-WorldFM, and new entrants as they ship) against a fixed suite of real GPUs spanning RTX 3060 through 4090, measure actual sustained FPS, input-latency, and visual-quality degradation at each tier, and publish the results alongside a one-click runner (modeled on how Ollama standardized "pull and run" for LLMs) that only offers configurations the benchmark actually verified for the user's detected card. The centerpiece is the verification step, not a new model — it turns a field of unverifiable marketing claims into a trustworthy "will this actually run acceptably on my GPU" answer.

## Tangible Impact
**Population**: PC owners with entry-to-mid-tier consumer GPUs (RTX 3060/4060-class cards are consistently among the most common discrete GPUs in the Steam Hardware Survey) who are indie game prototypers, creative technologists, or hobbyists interested in interactive generative video but priced out of the RTX 4090/5090-class hardware the leading research teams actually benchmark on.
**Mechanism**: Replaces "download and hope" with a verified compatibility answer before setup time is spent, and gives the broader entry-level-GPU population honest visibility into a category whose marketing (including the source Reddit post itself) currently outruns independent proof.
**Measure**: (1) gap between vendor-claimed and independently measured FPS/quality at each GPU tier; (2) percentage of catalogued models that actually meet a defined "real-time interactive" bar (e.g., ≥15 FPS at stable latency) on RTX 3060/4060 specifically, vs. claims; (3) setup-to-running time for a new user via the packaged runner compared to manually following each project's own install instructions.

## Why Now
Interactive world models went from research curiosity to a cluster of competing public releases within the same 30-day window (Overworld, Skywork, InSpatio, and this Reddit release all surfaced in October–November 2026), and none of the competing teams have an incentive to publish unflattering lower-tier-hardware numbers themselves — the verification gap is wide open precisely because the category is new enough that no neutral benchmark exists yet.

## Skill Angle
A companion skill handles the one-shot verification task without the full packaging infrastructure: given a specific world-model repo/release and a target GPU model, the skill researches the project's claimed requirements, runs (or walks through running) the model against a standard probe scene, and produces a compatibility report — "verified: 18 FPS sustained on RTX 4060" or "unverified: claims 3060 support, repo's own benchmarks only show 4090 numbers." This differs from the project: the project is the persistent benchmark database plus the packaged multi-model runner meant to stay current as new releases ship; the skill is a point-in-time due-diligence check someone runs before committing to try a specific release on their own hardware.

## MVP Sketch
Scope: benchmark 3 current public world models (lucidml/gta plus two others from the digest's verdict notes) on 2 real GPU tiers (a rented RTX 3060 and RTX 4060 cloud instance), publish raw FPS/latency numbers and a compatibility matrix, wrap the best-performing one in a minimal one-click local runner. Stack: Python, the models' own inference code, cloud GPU rental (Vast.ai/RunPod) for the benchmark tier, a simple static site for results. Single validating experiment: does any model actually clear a defined real-time bar on the RTX 3060 tier as claimed — if none do, that finding alone is the MVP's value and the packaging layer gets deprioritized.
## Risks & Open Questions
- The category is moving fast enough that today's benchmark results may be stale within weeks as new releases ship — this needs to be a maintained, recurring effort, not a one-time report, which raises the sustained-effort bar beyond a typical MVP.
- Access to real low-end consumer GPUs for benchmarking (vs. higher-end cloud instances) may be harder/pricier to rent than assumed; cloud GPU tiers don't perfectly map to desktop RTX 3060 thermal/driver conditions.
- If one of the established teams (Overworld, Skywork) publishes their own low-end-hardware benchmark with real numbers, a large part of this project's unique value disappears.
- "Real-time interactive" quality is partly subjective (visual coherence, control responsiveness) — the FPS/latency numbers are necessary but may not fully capture what makes a demo actually usable.
