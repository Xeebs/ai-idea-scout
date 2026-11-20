# Mute Echo: An Open, Stack-Agnostic Self-Voice Transcript Filter for Voice-Agent Barge-In Detection

- **Status**: EXPLORING
- **Date**: 2026-11-17
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-17-voice-multimodal-agents.md · P7
- **Maturity verdict**: PARTIAL — Soniox STT v6 shipped a real, text-conditioned self-voice filter on Nov 3 2026, but it is a single proprietary vendor feature; Deepgram and AssemblyAI rely on a different approach (acoustic echo cancellation / mic-pause during playback), and no open-source or second-vendor implementation of text-conditioned filtering exists anywhere.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — reads the agent's own outgoing TTS text buffer and the live STT transcript stream, both already present inside any Pipecat/LiveKit Agents pipeline. No external API or manual paste is needed; it runs as an inline plugin fed from data the pipeline already has.

## The Gap
Soniox's November 3 announcement describes an STT model that "takes the agent's own text as input and filters the agent's voice out of transcripts, which helps when users interrupt" — a real, shipped technique. But it is locked to one vendor's STT. Deepgram's and AssemblyAI's own docs confirm they solve the same echo-vs-real-interruption problem acoustically instead (echo cancellation, keyterm boosting, pausing mic capture during playback) — so any team not on Soniox, including every self-hosted Pipecat/LiveKit Agents builder, has no equivalent.

## The Project
A stack-agnostic middleware plugin that sits between any STT output and any downstream interruption/barge-in classifier (including the already-published Barge Triage classification engine in this repo's own INDEX). It takes the agent's known outgoing TTS text as a side-channel input and runs lightweight text-conditioned matching against incoming transcript segments to flag and strip segments that are the agent hearing itself rather than the caller speaking — working with any STT vendor's raw output, since it's a post-processing filter rather than a change to the STT model itself.

## Tangible Impact
**Population**: Self-hosted/open-source voice-agent builders on Pipecat (17,311 GitHub stars) and LiveKit Agents (15,266 stars) — a sizeable, actively-maintained builder base — who have no access to Soniox's proprietary filter and currently rely on weaker acoustic echo cancellation. Downstream, the callers interacting with these agents, who experience the agent cutting its own sentence off mid-word when it mishears itself as being interrupted.
**Mechanism**: Reducing false self-interruptions means fewer agent responses get needlessly truncated or re-started, which directly lowers call friction and the chance a caller hangs up confused or frustrated.
**Measure**: (1) false-barge-in rate attributable to self-echo, before/after, on a held-out set of real call recordings; (2) call abandonment rate on calls with vs. without the filter enabled; (3) downstream classifier accuracy (e.g. Barge Triage) when fed filtered vs. unfiltered transcripts.

## Why Now
Soniox just proved the technique works in production (Nov 3 2026) but kept it proprietary — the open-source Pipecat/LiveKit ecosystems are mature and widely deployed enough today that a portable version has an immediate, sizeable adopter base rather than needing to wait on anything.

## MVP Sketch
Scope: a single Pipecat processor plugin that ingests the pipeline's own TTS text queue and raw STT transcript stream, does simple text-similarity-based segment flagging (no new model training required for v1), and emits a cleaned transcript plus a "likely self-echo" confidence score. Stack: Python, as a Pipecat FrameProcessor. Validating experiment: replay 20 recorded calls with known ground-truth barge-in moments through the pipeline with and without the filter, and measure the change in false-barge-in count.

## Risks & Open Questions
- Simple text-matching may miss cases where caller speech coincidentally overlaps agent content (e.g., caller repeats the agent's own words back) — false negatives could be as costly as the false positives it's meant to fix.
- A full learned model (rather than text-matching heuristics) may be needed to match Soniox's real-world accuracy, which is a bigger build than the MVP implies.
- If Deepgram or AssemblyAI add an equivalent text-conditioned mode to compete with Soniox, this collapses to a thin compatibility shim rather than a novel contribution.
- No independent benchmark of Soniox v6's actual accuracy lift exists yet, so the ceiling this project is chasing is itself unverified.
