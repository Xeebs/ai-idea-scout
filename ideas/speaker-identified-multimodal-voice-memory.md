# Who Said That: Speaker-Identified Multimodal Memory for Shared Voice Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-ii.md · P4
- **Maturity verdict**: PARTIAL (real shipped-but-narrow tools exist on both sides — `alexwboles/voice-memory`/`callrecall-ai` for single-speaker per-caller memory, and LiveKit+Speechmatics' production diarization add-on with no persistent memory layer — but no production voice-agent platform combines continuous, boundary-free, multi-party speaker-identified memory as a shipped feature; EgoMem, M2A, and VoxPolyMem remain research-only)
- **Format**: PROJECT

## The Gap
EgoMem states the problem directly: "earlier memory agents assume known user identities, clear session boundaries, and text-only input, and those assumptions fail in full-duplex omnimodal use." Shared voice agents — a smart-speaker-style device used by multiple household members, or a kiosk/office voice agent multiple employees interact with — currently either blend everyone's preferences into one memory profile or require an explicit login/session step that defeats the point of a voice-first interface. Research systems (EgoMem, M2A, VoxPolyMem, which scores 85.0 on its own benchmark, 23.6 points above its strongest baseline) solve pieces of this, but no shipped product combines continuous speaker identification with per-person, incrementally-editable memory.

## The Project
A memory layer for shared voice agents that identifies individual speakers by voice inside continuous audio with no explicit session boundary, attributes each new fact or preference to the correct speaker, and lets those per-person memories be incrementally corrected as preferences change — without requiring any login step or wake-word-per-person ritual. It plugs into existing voice-agent stacks as a memory backend, combining off-the-shelf speaker diarization/voice-ID with a per-speaker memory store and a conflict-resolution policy for when diarization confidence is low.

Components: a continuous speaker-ID front end, a per-speaker memory store with incremental edit/correction support, a low-confidence fallback (ask a disambiguating question rather than guessing), and a cross-contamination test suite (does the system ever apply person A's preference to person B).

## Tangible Impact
**Population**: multi-person households and small shared workspaces using a shared voice-agent device — e.g., family members using one smart-speaker-style assistant, or a small team using a shared office kiosk voice agent — where a single blended memory currently causes visible errors (recommending one person's dietary restriction to another, repeating another person's calendar details).
**Mechanism**: correctly attributing facts and preferences per speaker, continuously and without a login step, removes the cross-contamination errors that currently make shared voice agents feel unreliable or mildly invasive to the people who share the device, and lets each person get personalized responses without administrative setup.
**Measure**: per-speaker fact-attribution accuracy on a multi-person test household/office corpus; cross-contamination error rate (wrong-person preference applied); user-reported "it doesn't remember me correctly" incident rate in a pilot deployment.

## Why Now
Low-latency, high-accuracy speaker diarization and voice-ID are now commodity components (LiveKit+Speechmatics ships this in production), and editable dual-layer memory architectures (M2A) are published with enough detail to replicate — the missing piece is combining the two, which is newly feasible without needing a research-grade jointly-trained model.

## MVP Sketch
Wire an existing open speaker-diarization/voice-ID component to a simple per-speaker key-value memory store with incremental edit support; build a small multi-person test corpus (3-4 speakers interacting with a shared device over several sessions with no explicit login); measure fact-attribution accuracy and cross-contamination rate against a single-blended-memory baseline. The single experiment: does speaker-identified memory measurably reduce cross-contamination errors versus the current blended-memory default, without requiring a login step.

## Risks & Open Questions
- Voice-ID accuracy degrades with similar-sounding speakers (e.g., siblings), which is exactly the household case this targets most — the fallback disambiguation question needs to handle this gracefully or the feature feels broken.
- Privacy concerns are real: continuous voice-ID inside a household raises consent questions (does every household member know they're being identified and tracked) that the project needs a clear answer for before deployment.
- No existing labeled multi-person household corpus exists publicly; building one is slow and may not generalize to the eventual real deployment context.
- If voice-ID confidence is persistently low in noisy real-world settings, the system may fall back to disambiguation questions often enough to undermine the "no login step" value proposition.
