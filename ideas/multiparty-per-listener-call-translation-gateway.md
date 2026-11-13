# Lingua Bridge: A Phone-Number-Based Multi-Party Per-Listener Translation Gateway

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-iii.md · P8
- **Maturity verdict**: PARTIAL (the per-listener live-translation technique itself is already shipped in two maintained open-source examples — `livekit-examples/gemini-live-translate` and Google's own `google-gemini/gemini-live-translate-livekit`, both video-room-based; neither is a phone-number-based telephony system combining human↔human, AI-outreach, and human↔agent call legs the way a GitHub issue on the TalkFlow project explicitly scopes — that specific integration remains an open, unscoped issue in one small project, not a shipped combination)
- **Format**: PROJECT
- **Data Sources**: CONNECTED — bridges live call audio legs via SIP/PSTN (LiveKit SIP, Twilio Voice, or Telnyx) into a real-time per-listener translation pipeline (Gemini Live API or an equivalent streaming speech-translation API); all audio is live-connected, never pasted or uploaded as a transcript.

## The Gap
A GitHub issue on the TalkFlow project explicitly scopes this as a goal: "Build a phone-number based multilingual customer calling system... Support: (1) customer ↔ human agent calls, (2) AI agent calls customers for approved outreach/support, and (3) human ↔ human calls with live per-listener translation." This is an open issue describing work still to be scoped and built inside one small project — not a shipped or widely-referenced capability. Meanwhile, the underlying per-listener translation technique is already proven in maintained open-source video-room examples (LiveKit + Gemini Live, defaulting to 8-person rooms with 16 languages and a per-listener captions sidebar), but nobody has wired that technique into actual telephony with mixed call-leg types.

## The Project
A SIP/PSTN gateway that bridges ordinary phone calls (not a video room, no app required) into a multi-party, per-listener real-time translation pipeline, supporting mixed call-leg types in one system: human-to-human, AI-to-human outreach, and human-to-agent. Each participant hears every other participant's speech translated live into their own chosen language, regardless of what language the call was dialed in. The novel pattern is the centerpiece: taking the already-proven per-listener translation technique out of the video-room context it currently lives in and making it work over a plain phone call.

Components: a SIP/PSTN ingress-egress gateway, a per-listener language-routing layer feeding a streaming speech-translation API, a call-leg type manager handling human/AI/mixed legs, and a latency/accuracy benchmark harness specific to narrowband telephony audio.

## Tangible Impact
**Population**: limited-English-proficiency (LEP) individuals and their multilingual family or community networks who rely on ordinary phone calls, not video-conferencing apps, for multi-party conversations — a multigenerational family care-coordination call, a multilingual tenant-association meeting, or a community-health-outreach conference call. (U.S. Census Bureau American Community Survey estimates commonly cite roughly 26 million U.S. residents as having limited English proficiency — a widely used general demographic estimate, not a figure sourced from this digest's evidence.)
**Mechanism**: a phone-only, per-listener translation gateway removes the requirement that every participant join a video platform or rely on a single bilingual pair-translation relay, so a genuinely multi-party, multi-language phone call becomes possible without hiring a human interpreter for every language pair in the room.
**Measure**: number of simultaneous languages served per call without added human interpreters; end-to-end translation latency per listener leg, benchmarked against the existing two-person speech-to-speech baseline; task-completion and comprehension rate in a scripted multi-party test call with three or more languages, compared against a baseline single bilingual-interpreter call.

## Why Now
The per-listener translation technique itself only shipped in maintained open-source form in 2026 (LiveKit + Gemini Live examples), proving technical feasibility for the first time — but it has only ever been demonstrated inside a video room. The TalkFlow issue shows real, current demand to combine that technique with actual telephony and mixed call-leg types, scoped but genuinely unbuilt.

## MVP Sketch
Build a SIP/PSTN gateway (using LiveKit SIP or Twilio Voice) that bridges an inbound or outbound phone call into a LiveKit room running the existing `livekit-examples/gemini-live-translate` per-listener pipeline, supporting at minimum three call legs across three languages. Validate with a scripted test call (one English speaker, one Spanish speaker, one Mandarin speaker, phone-only, no app or video required) measuring per-leg translation latency and completing a structured task (e.g., scheduling coordination) to confirm comprehension.

## Risks & Open Questions
- Telephony audio (narrowband, 8kHz) is lower quality than the WebRTC audio the existing video-room examples were built and tested on; translation accuracy needs its own validation on degraded audio, not an assumption it carries over.
- Latency stacking (ASR + translation + TTS, repeated per listener) could make real-time phone conversation infeasible at four or more languages; may require capping party count or accepting a perceptible delay.
- No telephony-specific implementation of per-listener translation exists yet to benchmark against — a genuine first-mover build with no established accuracy/latency bar to beat, which cuts both ways (no competition, but also no proof the approach survives telephony constraints).
- Real-time consent and data-handling obligations for live-translated call content (recording, processing, cross-border data residency through the translation API) add compliance overhead not present in the existing video-room demos.
