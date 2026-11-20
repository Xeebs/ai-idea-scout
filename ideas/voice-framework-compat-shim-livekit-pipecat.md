# Framework Bridge: A Neutral Compatibility Shim Between LiveKit Agents and Pipecat

- **Status**: EXPLORING
- **Date**: 2026-11-20
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-20-voice-multimodal-agents.md · P3
- **Maturity verdict**: PARTIAL — one single-maintainer repo (`berkerbatur/speechready`) ships narrow turn-segmentation hooks for both frameworks; SignalWire's "LiveWire" exposes LiveKit-shaped class names on SignalWire infra but treats STT/TTS/VAD/turn-detection plugin params as no-ops and only goes LiveKit→SignalWire; Pipecat's own LiveKit transport is a transport adapter, not an Agents-API-level shim. No neutral, bidirectional LiveKit Agents↔Pipecat compatibility layer exists.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the shim operates inside the existing LiveKit Agents and Pipecat runtimes, reading/writing through each framework's own native session, audio-frame, and event APIs (both official, actively maintained SDKs — LiveKit Agents ~400K weekly PyPI downloads vs. Pipecat ~90K per LiveKit's own January 2026 comparison page; GitHub star counts put them within a few thousand of each other). No pasted transcript or call data is required for the shim itself. (The companion skill's input is MANUAL — see Skill Angle.)

## The Gap

Two incompatible open orchestration frameworks (LiveKit Agents, Pipecat) now dominate voice-agent builds, and teams are already paying the lock-in cost: a real GitHub PR (`berkerbatur/speechready` #11, 2026-11-02) ports turn-segmentation hooks to both frameworks' current APIs by hand; NVIDIA's own `nemotron-voice-agent` blueprint PR (#219, 2026-11-19) restructured its repo into a one-package-per-framework layout specifically to support both side by side; and a widely-read comparison piece (forasoft.com) frames the choice as "same models, same latency, different regrets" — implying regret either way. Every attempt found is narrow, one-directional, or internal-only; nobody has shipped the neutral layer that would let a team write logic once.

## The Project

A small, framework-agnostic core abstraction — pipeline stages (STT→LLM→TTS), turn/VAD events, and tool-call hooks — with two thin adapter packages: one that maps the core API onto `livekit-agents`' current classes, one onto `pipecat-ai`'s `Frame`/`Processor` model. A team writes its turn-taking, interruption, and tool-dispatch logic once against the core API; the adapter translates calls and events in both directions, unlike LiveWire's one-way, no-op-plugin approach. Versioned against both frameworks' current releases (the digest's own evidence names `livekit-agents 1.8.10` and `pipecat-ai 1.15.0`), with CI that fails the build the moment either upstream API drifts — a real risk both frameworks have already shown.

## Tangible Impact

**Population**: Indie and small-team voice-agent builders choosing between LiveKit Agents and Pipecat today — a population in the tens of thousands given LiveKit's own reported ~400,000 weekly PyPI downloads for Agents (vs. ~90,000 for Pipecat, per LiveKit's January 2026 comparison page) and a 2026 voice-AI-agent software market estimated at $3.5–5.1B (Grand View Research, Meticulous Research) built substantially on these two frameworks.
**Mechanism**: A team that writes turn-taking/interruption/dispatch logic against the shim stops needing to pick a framework before writing a line of business logic, and stops re-deriving `speechready`'s or NVIDIA's own one-off porting work. Switching frameworks later (for latency, licensing, or hosting reasons) becomes a dependency swap instead of a rewrite.
**Measure**: time-to-port an existing non-trivial agent (e.g. a 5-stage pipeline with custom turn logic) from one framework to the other with vs. without the shim; number of framework-specific API calls a real agent needs outside the shim's coverage; CI pass rate against each framework's latest release over a 90-day window as a proxy for how well the shim tracks upstream drift.

## Why Now

Both frameworks are mid-2026 production-grade and actively diverging (LiveKit is WebRTC/multi-participant-centric, Pipecat is pipeline-flexibility-centric per multiple comparison pieces found this cycle), so the lock-in cost is rising, not falling — exactly the moment a neutral layer pays off before more production code hard-codes one framework's shape.

## Skill Angle

A "framework portability reviewer" skill: given a pasted LiveKit Agents or Pipecat agent script, it flags which constructs are framework-specific (no shim coverage yet), which are already portable, and drafts the equivalent call against the other framework's current API — letting a team assess migration risk or dual-framework feasibility before committing to the shim's infrastructure build.

## MVP Sketch

Scope: cover just the three highest-value surfaces — turn/VAD events, STT/TTS stage wiring, and tool-call dispatch — for the current stable release of each framework. Stack: Python, thin adapter classes, a shared test agent (echo + one tool call + barge-in) run against both adapters in CI. The validating experiment: port `speechready`'s own segmenter example through the shim and confirm identical behavior on both frameworks without touching the segmenter's own code.

## Risks & Open Questions

- Both frameworks evolve fast; the shim could become a permanent maintenance tax chasing two moving targets — mitigated by scoping to the stable 80% of each API, not every escape hatch.
- If one framework's next major version formally adds first-class portability (unlikely but possible), this shim becomes redundant — worth re-checking framework roadmaps before a large build commit.
- A shim inherently can't expose a framework-unique feature (e.g. LiveKit's native multi-participant room semantics) without breaking neutrality — needs an explicit "escape hatch" story, not silently papering over the gap.
- SignalWire's LiveWire shows plugin-param no-ops are an easy trap; this project must be honest in its docs about which calls are fully wired vs. stubbed, unlike LiveWire's current framing.
