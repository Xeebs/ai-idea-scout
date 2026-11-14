# One Mic, Many Apps: A Shared Local Voice-Loop Daemon and Protocol

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-14-voice-multimodal-agents.md · P3
- **Maturity verdict**: PARTIAL — `overnightworks/agents#803` (20 comments) frames "one voice loop for every app" as an open, aspirational request, not a shipped feature. Two 2026 shipped products approach the ambient-listening framing (Vellum Ambient, screen-aware on Mac since Sept 2026; Mistlabs' Ambi, cross-platform, $26M raise, out of beta Oct 2026) but both require explicit activation/screen-sharing per app rather than a shared, opt-in protocol multiple independent apps can register with — no implementation of a genuinely shared, app-agnostic voice-loop bus surfaced.
- **Format**: BOTH
- **Data Sources**: MANUAL — for the companion skill, the user pastes their app's existing voice/command-handling code or a description of its current input surface (REST endpoints, CLI commands, or function signatures it wants voice-triggerable), and the skill drafts the integration manifest. The daemon project itself reads no external account data; it only brokers audio and intent between locally-registered apps that opt in.

## The Gap
The source thread's literal request — "ich will dass die ki alles mithört" ("I want the AI to hear everything") — plus 20 comments of discussion shows real appetite for one persistent voice interface instead of every app shipping its own siloed push-to-talk feature. But both shipped 2026 products (Vellum Ambient, Ambi) solve this as a single vendor's always-on assistant over the *entire screen*, not as an open protocol that lets independent, otherwise-uncooperative apps register their own voice-triggerable actions with a shared loop. No GitHub implementation of that narrower, more buildable framing — a voice-loop bus apps opt into — surfaced in this run.

## The Project
A local daemon plus a lightweight registration protocol: any app on a machine can register a manifest of voice-triggerable intents (a name, trigger phrases or embedding-matched descriptions, and a local callback — a CLI invocation, a Unix socket message, or a localhost HTTP call) with the daemon. The daemon owns the single microphone stream, does wake-word/always-listening capture, routes a detected utterance to whichever registered app's intent best matches, and dispatches. This replaces N apps each running their own STT+wake-word stack (and fighting over mic access) with one shared listener and a routing layer apps opt into — closer to a "D-Bus for voice intents" than a screen-reading ambient assistant.

## Tangible Impact
**Population**: desktop power users running several voice-adjacent local tools simultaneously (a note-taking app, a home-automation hub, a coding assistant, a music player) who today either run one app's voice feature at a time or suffer multiple apps fighting for the microphone; and the indie developers building those apps, who currently each re-implement wake-word detection and STT from scratch to add a voice feature.
**Mechanism**: a developer integrates a voice feature in the time it takes to write a manifest instead of standing up an STT pipeline, and an end user gets one consistent wake phrase and mic-ownership model across every participating app instead of a different voice UX (and a mic-contention bug) per app.
**Measure**: integration time for a new app (manifest-only vs. a from-scratch STT pipeline, in developer-hours); number of distinct apps registered with the daemon within 90 days of release; intent-routing accuracy (correct app dispatched) on a mixed-intent test set across 5+ registered apps.

## Why Now
Lightweight local STT (Whisper.cpp-class models) and wake-word detection are now cheap enough to run continuously on a laptop CPU without noticeable battery/fan impact, which is what makes a shared always-on daemon newly practical rather than a drain every app would resist sharing; the Vellum Ambient and Ambi launches this year are evidence the appetite is real, but both chose the heavier screen-reading path instead of this lighter opt-in protocol.

## Skill Angle
A one-shot integration-manifest generator: given a pasted description of an app's existing command surface (function names, CLI flags, or API endpoints), the skill drafts the daemon-registration manifest — trigger phrases, callback wiring, and a suggested disambiguation phrase for intents that might collide with another registered app. This is separable from the project: the project is the always-running daemon and routing logic; the skill is the drafting aid a developer runs once per app they want to connect.

## MVP Sketch
Scope: a local daemon (Python or Rust) owning one `pyaudio`/`cpal` mic stream, running a small wake-word model plus Whisper.cpp for STT, with a simple JSON manifest format (`intents: [{name, trigger_phrases, callback: {type: "http"|"socket"|"exec", target}}]`) and a CLI for apps to register/deregister. Validate with 3 toy registered apps (a notes CLI, a mock smart-light toggle, a music-player control) and measure routing accuracy on 50 mixed utterances. Target: 3-4 weeks for two people (daemon + protocol design, plus the 3 demo integrations).

## Risks & Open Questions
- Multiple apps registering overlapping or ambiguous trigger phrases is the central product risk — the disambiguation/arbitration logic (which app gets a genuinely ambiguous utterance) needs real design, not an afterthought.
- Always-on microphone capture raises the same privacy concerns Vellum Ambient and Ambi both had to address with explicit opt-in UX; a daemon with no equivalent consent/indicator design will face the same pushback, or worse since it's multi-app.
- If a major OS vendor (Apple, Microsoft) ships an equivalent system-level voice-intent registration API, this project's value narrows to cross-platform/Linux use cases — worth checking OS roadmaps before over-investing.
- The "one voice loop for every app" framing in the source thread may really be asking for ambient *screen* awareness (what Vellum/Ambi built), not an opt-in app protocol — if so, this project solves an adjacent but genuinely different problem than what the original requester wanted.
