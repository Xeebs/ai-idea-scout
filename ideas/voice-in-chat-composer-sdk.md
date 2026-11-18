# Composer Voice: A Drop-In Bidirectional Voice SDK for Existing Text-First Chat UIs

- **Status**: PROPOSED
- **Date**: 2026-11-17
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-17-voice-multimodal-agents.md · P8
- **Maturity verdict**: PARTIAL — two narrow one-off implementation attempts exist (pingdotgg/t3code PR #30720, 1 reaction/2 comments; cruzlxyz/livetalk, 2 stars), and Sierra's commercial multimodal product does the same thing but is closed; no maintained, portable library exists that any team building a text-first chat product can adopt directly.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the Gemini Multimodal Live API (`BidiGenerateContent` WebSocket), mature and documented, already used directly in the reference PR, with an OpenAI Realtime API adapter as a planned second backend. No manual data entry beyond normal chat usage.

## The Gap
A real GitHub PR (pingdotgg/t3code #30720, Nov 4 2026) adds `GeminiLiveVoiceControl` directly into a chat composer using Gemini's Multimodal Live WebSocket API — 16kHz mic capture, 24kHz gapless playback, inline in the same input the user already types into. It got minimal review engagement. A second, newer, equally tiny repo (cruzlxyz/livetalk, 2 stars, pushed Nov 14) attempts the same pattern independently. Both are one-off, unmaintained-scale implementations of a pattern no portable library covers.

## The Project
An SDK — a React/Vue component plus a thin backend relay — that drops a mic control directly into an existing chat composer, streaming audio to a realtime multimodal API and playing the response back inline in the same conversation thread, normalized behind one interface so a team isn't locked into one provider's WebSocket protocol. Any product that already has a text chat composer (support widgets, internal tools, consumer AI chat apps) can add voice without building a separate standalone voice app.

## Tangible Impact
**Population**: People for whom typing into a chat box is hard or unsafe in the moment — workers with temporary or permanent motor/dexterity impairments (CDC estimates roughly 1 in 4 U.S. adults live with a disability, a meaningful share of which is mobility/dexterity-related), commuters and drivers using consumer AI chat apps who can't safely type, and field/warehouse workers logging notes hands-free into an internal AI assistant — plus the engineering teams at any text-first chat product who would otherwise need a whole separate voice app to serve them, which most teams won't fund.
**Mechanism**: Because voice becomes a drop-in addition to an existing composer instead of a new app to build and maintain, far more existing chat products can plausibly ship voice access, so these users gain a voice input option on products they already use rather than needing to wait for a bespoke standalone voice app.
**Measure**: (1) number of distinct chat products integrating the SDK; (2) task completion time/rate for voice-preferring users vs. typing on the same product; (3) change in abandonment rate (users who start typing but drop off before submitting) after voice is enabled, as a proxy for users who couldn't comfortably type.

## Why Now
Gemini's Multimodal Live API and OpenAI's Realtime API are both mature, documented, low-latency WebSocket APIs today — the only missing piece is a maintained, provider-agnostic composer-level wrapper, which both known attempts prove is buildable but neither has made reusable.

## Skill Angle
An **integration-scaffolding skill**: given a description of an existing chat UI's framework and composer structure, it drafts the specific integration diff (component wiring, backend relay stub, auth handshake) for adding the SDK — a repeatable, one-shot drafting task independent of the SDK's own runtime infrastructure.

## MVP Sketch
Scope: a single React component + Node relay supporting Gemini Multimodal Live only for v1, with a documented adapter interface for a second provider later. Stack: TypeScript/React, Node WebSocket relay, deployable as an npm package. Validating experiment: integrate into one real open-source chat UI (e.g., a Chatwoot or open-source support-widget fork) and measure setup time and whether voice sessions complete without audio dropouts across 20 test calls.

## Risks & Open Questions
- Realtime WebSocket APIs from both Gemini and OpenAI change fast; keeping a provider-agnostic adapter current is ongoing maintenance load.
- Browser mic permission UX and background-tab audio handling are genuinely fiddly — a thin wrapper might not hide enough of that complexity to be worth adopting over writing it directly.
- Sierra's closed commercial product proves demand but also that well-resourced competitors could ship an open equivalent at any time.
- Accessibility-impact claims need real user testing with motor-impaired users to confirm the mechanism, not just plausibility.
