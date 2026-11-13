# Full Call: A Consolidated End-to-End Conversational Eval Framework for Voice Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-ii.md · P3
- **Maturity verdict**: PARTIAL (at least eight independent, low-adoption eval repos created in 2026 — ArtemisVoice, VoiceAgentsEval, EVA-Bench, Cekura, Ultravox's custom benchmark, DeepEval's tooling, among others — confirm real, fragmented, non-converged implementations; no consolidated, cross-adopted tool exists; a Sprinklr paper finds LLM-judge reliability for voice agents "metric- and configuration-dependent," not solved)
- **Format**: BOTH
- **Data Sources**: MANUAL — the user pastes or uploads a description of their current voice-agent eval setup (what's measured per component, which judge model if any, sample call transcripts) for the skill's coverage audit; the project's own eval framework ingests call recordings/transcripts the team already has, not a live connector.

## The Gap
ServiceNow's EVA paper states plainly that "most existing efforts test components in isolation" (ASR accuracy, LLM response quality, TTS naturalness scored separately), missing the multi-turn, full-conversation failure modes that actually break production voice agents. Ultravox's own engineering blog admits none of the existing benchmarks "perfectly addresses our users' specific needs," so they built a bespoke one — which is itself the evidence of the gap: five-plus separate teams (ServiceNow, Ultravox, Cekura, DeepEval, assorted GitHub repos) built independent, non-converging eval efforts in the same few months because no consolidated, validated standard exists, and a Sprinklr paper shows the LLM-judge component that most of these rely on isn't reliably calibrated either.

## The Project
An open evaluation framework that scores full multi-turn spoken conversations end-to-end — not per-component ASR/LLM/TTS metrics — using an audio-native LLM-judge whose reliability has been validated against human ratings (following the Sprinklr paper's recommendation for human-in-the-loop calibration rather than a frozen, unvalidated judge). It ingests real or simulated call recordings, runs a battery of conversation-level failure-mode checks (context loss across turns, inappropriate interruption handling, failure to resolve the stated goal), and reports a calibrated score with a documented judge-reliability interval rather than a single opaque number.

Components: a conversation-simulation harness for generating realistic multi-turn test calls, an audio-native judge pipeline with a human-gold calibration set (reusing the approach from this repo's own tiered-judge-calibration-pipeline idea where applicable), a failure-mode taxonomy specific to full-call voice interactions, and an adapter layer so teams can plug in their own call recordings.

## Tangible Impact
**Population**: callers interacting with production voice agents built by small and mid-size engineering teams — companies too small to build bespoke eval infrastructure the way ServiceNow or Ultravox did, who currently ship on per-component metrics that miss conversation-level failures.
**Mechanism**: catching multi-turn failure modes (context loss, goal non-resolution, mishandled interruptions) before launch, using a calibrated rather than ad hoc judge, reduces the rate at which these failures reach real callers as a bad call experience or an unresolved issue requiring a callback.
**Measure**: correlation between the framework's calibrated score and real-world call outcomes (CSAT, resolution rate) on a held-out set of real calls; reduction in post-launch incident count for teams adopting the framework vs. a matched baseline; judge-score agreement with human raters on the calibration set.

## Why Now
EVA-Bench's open-sourcing by ServiceNow and the proliferation of independent eval repos in 2026 means the component pieces (simulation harnesses, audio-native judges, failure taxonomies) now exist publicly to be consolidated rather than built from scratch — the fragmentation itself is the signal that the moment for a consolidation effort is now, before one vendor's bespoke tool calcifies into the de facto standard without independent validation.

## Skill Angle
A Claude Code skill that, given a description of a team's existing voice-agent eval setup (what they currently measure, how), audits it against an audio-native-plus-validated-judge checklist and drafts a gap report plus a starter conversation-level failure-mode taxonomy tailored to their call types. This is a one-shot review/drafting task, distinct from the runtime harness the project builds, useful to a team before they commit to adopting (or building) the full framework.

## MVP Sketch
Take EVA-Bench's open-sourced components as a base; add a human-gold calibration set of ~50 real or realistic call recordings scored by human raters; measure judge-score agreement against that gold set; run the full pipeline against one real team's existing call logs and compare its flagged failures against their own incident reports. The single experiment: does the calibrated end-to-end score correlate better with real incident/CSAT outcomes than the team's current per-component metrics.

## Risks & Open Questions
- Building a genuinely validated judge (not just another self-reported one) requires real human-rated calibration data, which is expensive and may not generalize across call domains.
- The fragmentation itself might mean the market doesn't want consolidation — teams may prefer bespoke benchmarks tied to their own call types, limiting adoption.
- If LiveKit, Vapi, or another platform vendor ships this as a built-in feature first, an independent framework loses its reason to exist.
- Audio-native judging is compute-intensive; cost per evaluation run could limit adoption by the smaller teams this is meant to serve.
