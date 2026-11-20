# Preview Pane: A Vendor-Neutral Live-Traffic Preview for New Eval Definitions

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-20-llm-evaluation-observability.md · P2
- **Maturity verdict**: PARTIAL — "shadow testing" is a well-documented generic practice (Arize, Statsig, tianpan.co) and LiteLLM ships a maintained vendor-specific "auto-router shadow evaluations" feature, but that shadows candidate model/routing versions, not a newly-authored eval definition (filter/judge/check) being previewed before activation. PostHog shipped this as an internal UI feature (PR #130326); no standalone, vendor-neutral tool does eval-definition preview-on-live-traffic independent of one platform's own UI.
- **Format**: BOTH — the live-sampling preview service that connects to a platform's trace store and runs the draft eval against sampled traffic is persistent infrastructure; a one-shot "given this draft eval definition and a pasted batch of real transcripts, tell me what it would flag" is a separable judgment task.
- **Data Sources**: CONNECTED — reads a sample of real production traces via the team's existing observability platform's trace/export API (PostHog AI evals API, Langfuse API, or a generic OpenTelemetry collector) — these trace-retrieval APIs already exist and are mature. The draft eval definition itself (the filter, prompt, or judge code being tested) is authored/pasted by the user; the project's new piece is the vendor-neutral sampling-and-preview layer sitting on top of whichever trace API is already in place.

## The Gap
PostHog/posthog PR #130326 (2026-11-05, 7 comments): "People setting up an evaluation see no result until it runs on live traffic, so a wrong filter or check shows up only after they create it." PostHog solved this inside its own UI. The generic "shadow traffic" practice is well documented for swapping model/router versions, but no portable tool previews a newly-authored eval definition against sampled live traffic independent of any one platform's dashboard — teams on Langfuse, Braintrust, promptfoo, or an in-house harness have no equivalent today.

## The Project
A small service/CLI that plugs into an existing observability platform's trace-export API, pulls a configurable recent sample of real production traffic, and runs a draft eval definition (prompt-based judge, code-based check, or simple filter) against that sample before the user ever flips it on — reporting hit rate, flag distribution, estimated per-run cost, and the specific transcripts that would have been flagged, so a wrong filter is caught at authoring time instead of after activation. Ships as adapters per platform (PostHog, Langfuse, promptfoo) behind one shared preview-and-report core, so the preview logic itself is written once.

## Tangible Impact
**Population**: engineering and ML teams authoring new LLM evals across any observability platform other than PostHog (Langfuse, Braintrust, promptfoo, deepeval, in-house harnesses) — platforms that, per this digest's own research, have not shipped this preview UI themselves; PostHog's bug report itself names this as a "most of the tool's validation errors" class of problem for one vendor alone, suggesting the underlying need is not vendor-specific.
**Mechanism**: surfacing exactly what a draft eval would have flagged on real, recent traffic before it is switched on turns "find out after the fact that the filter was wrong" into "see it's wrong during authoring and fix it before anyone acts on a bad flag."
**Measure**: % of newly-authored evals that get edited before first live activation (vs. after); number of false-positive/false-negative flags caught in preview vs. discovered post-activation; median time from eval draft to a correctly-calibrated, activated eval.

## Why Now
MCP- and API-driven eval authoring has made creating a new eval cheap enough that teams spin up many per week, which raises the cost of each one going live mis-calibrated; PostHog's internal fix (shipped this cycle) demonstrates the underlying trace-sampling mechanics are already cheap and fast enough to run synchronously at authoring time.

## Skill Angle
Trigger: a user has drafted an eval definition (a judge prompt or a code-based check) and wants a sanity check before wiring it into a live pipeline. Inputs: the draft eval definition plus a pasted batch of 10–30 real (or realistic) transcripts/traces. Output: a per-transcript flag/no-flag call with brief reasoning, an aggregate hit-rate estimate, and a flag for any transcript where the eval's behavior looks surprising relative to its stated intent. This is the lightweight, no-infrastructure version of the same check the always-on preview service runs against a live trace sample.

## MVP Sketch
2–4 weeks, 1–2 people: build the preview-and-report core plus one adapter (PostHog's AI evals API, since its schema and the exact gap are already documented), run a handful of real or synthetic draft evals against a sampled trace export, and validate by deliberately authoring one mis-calibrated filter and confirming the preview surfaces the bad flags before activation.

## Risks & Open Questions
- If PostHog and other platforms each ship their own native preview UI, the vendor-neutral layer loses its reason to exist — needs at least one platform without a native preview to stay relevant.
- Preview quality is bounded by how representative the sampled traffic is; a too-small or stale sample could give false confidence.
- Overlaps conceptually with `llm-shadow-canary-rollout-orchestrator.md` (shadow-then-canary for prompt/model changes) — this idea must stay scoped to previewing an eval definition itself before first activation, not promoting an already-active eval through environments.
- Cost of running a preview against a meaningful traffic sample could itself be non-trivial for high-volume teams; needs a sampling-budget control from day one.
