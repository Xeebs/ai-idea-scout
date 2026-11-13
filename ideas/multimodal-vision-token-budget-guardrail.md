# Vision Budget: A Pre-Flight Token-Spend Guardrail for Multimodal Agent Loops

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-13-voice-multimodal-agents.md · P4
- **Maturity verdict**: PARTIAL (OpenAI ships an official reference image-cost calculator — not open-source, estimate-only, excludes prompt/output/caching tokens — and a niche Rust crate `shift-preflight`, docs.rs-only with unverified maintenance, estimates image tokens for OpenAI/Anthropic; no budget-guardrail middleware that gates or warns on vision-token spend *inside a running agent loop*, as opposed to a one-off calculator run by hand, was found on GitHub or web search)
- **Format**: BOTH
- **Data Sources**: CONNECTED — the middleware wraps the agent's own outbound calls to the multimodal provider API it's already using (OpenAI, Anthropic, or Gemini's vision-enabled endpoints), inspecting image/frame payloads and request parameters before they're sent; it reads nothing pasted by a user. The provider SDKs are mature and already in use by any team this targets; the wrapper and budget-estimation/gating logic are the new piece.

## The Gap
alexcloudstar.com's 2026 production write-up names this explicitly as a practitioner surprise: "an image is not one token," and teams discover the real cost footprint of feeding images or video frames into a multimodal agent only after shipping, when the bill arrives. The only mitigations found are after-the-fact: OpenAI's own calculator is a manual, one-off estimate tool excluded from running agent code, and a single low-adoption Rust crate does the same job for a narrower audience. Nothing sits inside the agent loop itself to estimate spend before a call goes out and gate or warn when it's about to blow past a budget.

## The Project
A middleware wrapper around a multimodal agent's outbound vision API calls that estimates the token cost of an image/frame payload before sending it — accounting for resolution, tiling/detail mode, and model-specific pricing quirks the OpenAI calculator already encodes but no runtime hook exposes — and applies a configurable policy: warn-and-log, downscale/compress automatically to fit a budget, or hard-block the call and fall back to a cheaper path (lower resolution, text-only, or a specialist CV model instead of the general multimodal model). It ships as a thin SDK wrapper so adopting it is "wrap your existing client," not a rewrite.

Components: a per-provider token/cost estimator (seeded from OpenAI's published calculator logic and Anthropic/Gemini's documented pricing), a configurable budget policy (per-session, per-request, or per-user caps), an automatic downscale/fallback path, and a spend ledger so a team can see where their vision-token budget is actually going across a running deployment, not just in a post-hoc bill.

## Tangible Impact
**Population**: engineering teams building production multimodal agents that process images, video frames, or live screen shares as part of the agent loop — the same builders cited across this digest's P3 (screen-state/precision-routing) and P5 (session-length degradation) patterns, who are demonstrably already shipping voice+vision agents that stream frames continuously, which is exactly the usage pattern that makes vision-token spend balloon unpredictably compared to a single-image chatbot use case.
**Mechanism**: today a team ships a multimodal agent, estimates cost from a handful of manual test calls, and only learns the real per-session cost once production traffic (especially continuous video/screen-frame streaming) multiplies it — by which point the cost model is baked into pricing or budget commitments already made. A pre-flight guardrail makes the cost visible and controllable before the call goes out, turning a post-launch bill shock into a configurable, enforced limit.
**Measure**: variance between pre-flight cost estimate and actual billed cost (target: within a small percent, proving the estimator is trustworthy enough to gate on); rate of budget-policy triggers (downscale/block events) in a pilot deployment and whether they correlate with avoided overage; total vision-token spend before vs. after adoption on an unchanged workload.

## Why Now
Multimodal agents that stream continuous video or screen-share frames (rather than a single uploaded image) are new enough in 2026 that the cost-per-session math genuinely surprises teams used to single-image or text-only pricing intuition — this digest's own P3 and P5 patterns are evidence that voice+vision agents processing continuous visual input are now common enough to be a recognized, named failure-mode category, not a hypothetical. The provider APIs and their pricing structures are stable and documented enough today to build a reliable estimator against, which wasn't true when vision pricing models were still shifting release to release.

## Skill Angle
A companion skill, "vision-token cost auditor," takes a pasted snippet of an agent's multimodal-calling code (or a description of its image/frame-sending pattern: resolution, frequency, detail mode) and estimates the per-session and per-month cost at a given traffic volume, flagging which specific calls are the most expensive and suggesting concrete downscale or routing changes. This is a one-shot pre-launch review distinct from the project: the skill is the audit a team runs before shipping; the project is the always-on guardrail that enforces the resulting budget live.

## MVP Sketch
Build the wrapper for one provider first (OpenAI's vision API, since its calculator logic is public and reference-able), implement the token/cost estimator and a two-tier policy (warn-and-log, hard-block-with-fallback), and validate estimate accuracy against ~50 real API calls of varying image sizes/detail modes by comparing predicted vs. actual billed tokens. The single experiment: is the pre-flight estimate accurate enough (within an agreed tolerance) to safely gate real traffic on, not just inform a dashboard after the fact?

## Risks & Open Questions
- Provider pricing and tokenization rules for images change without much notice; the estimator needs a maintenance commitment or it silently drifts out of accuracy, which is worse than no guardrail if teams trust a stale number.
- Auto-downscaling to fit a budget risks degrading the exact precision-task accuracy that P3's pattern is already worried about — the fallback policy needs to be budget-aware without becoming the cause of a different failure mode.
- A provider could ship this as a native API parameter (a `max_tokens`-style cap for vision) before an independent wrapper gains adoption; differentiation has to be cross-provider portability and the automatic-fallback policy, not just estimation.
- If teams are willing to just eat the cost once they understand it, the guardrail's real value is visibility/control rather than hard savings — the MVP should measure whether teams actually act on warnings, not just whether warnings fire accurately.
