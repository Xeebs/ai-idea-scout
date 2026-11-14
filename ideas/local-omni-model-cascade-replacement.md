# Cascade Out: A Benchmarked Local Omni-Model Replacement for the STT+LLM+TTS Voice Pipeline

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-14-voice-multimodal-agents.md · P1
- **Maturity verdict**: PARTIAL — ~6 independent repos in the last two weeks (`MhaWay/lfm3-realtime`, `baka-onii/VoxLoop`, `Red-fuchs/kitsune`, `oki/poc-lfm3-audio`, plus the source `ArpanSM/forge-voice#1` spike) run a local omni-model (LFM3-Audio-2B) doing STT+reasoning+TTS with native `tool_calls` in one process, but all are brand-new, single-maintainer, un-starred hobby projects — no maintained, benchmarked, reusable package productizes the pattern. Vendor cloud products (Gemini 3.1 Flash Live, PolyAI Dialog-RSN-1) solve the structural equivalent but only as paid hosted APIs.
- **Format**: BOTH
- **Data Sources**: MANUAL — the user pastes their current voice-agent architecture (vendor STT/LLM/TTS endpoints and model names, current per-call cost and p50/p95 latency numbers, and the list of tool/function definitions the agent calls). No external connector is needed for the migration-assessment skill since this is a one-time architecture description, not live account data; the runtime project itself talks to no third-party account, only to the local model process it hosts.

## The Gap
Builders chaining Deepgram/Cartesia-style STT+TTS vendors around an LLM are discovering that a single local audio-native model (LFM3-Audio-2B) can do STT, reasoning, and TTS in one process with native `tool_calls`, eliminating per-minute vendor costs and a network hop per utterance (`ArpanSM/forge-voice#1`, explicitly marked "do not merge" — a spike). At least six other hobbyists independently built the same thing in the same two weeks, but every implementation is a solo, unstarred, unbenchmarked proof of concept — nobody has packaged it as something a team could actually adopt with confidence.

## The Project
A maintained open-source package that wraps a local omni-model (starting with LFM3-Audio-2B, designed to swap in successors) behind the same tool-calling interface popular voice-agent frameworks (LiveKit Agents, Pipecat) already expose — so migrating off a three-vendor cascade is a config change, not a rewrite. The centerpiece is a reproducible benchmark suite comparing the local-omni path against a cascaded baseline on the dimensions that actually matter to a team deciding whether to switch: end-to-end latency, tool-call accuracy under barge-in, voice quality (MOS), and cost per 1,000 minutes on commodity GPU hardware (one 24GB card, the realistic self-host target). Components: (1) an adapter layer exposing the omni-model's native tool_calls through the standard agent-framework tool interface, (2) a benchmark harness with a fixed task/call-scenario set, (3) a hosting profile (Docker + model weights pinned) so "it worked on my machine" isn't the only evidence.

## Tangible Impact
**Population**: small voice-agent shops and solo builders currently paying Deepgram/Cartesia/ElevenLabs per-minute fees for production call volume — the same population the source evidence is drawn from (builders explicitly citing "no API key or per-minute cost" as the win). Deepgram alone reports tens of thousands of active developer accounts; a meaningful fraction run cost-sensitive, high-volume use cases (appointment booking, order intake) where per-minute vendor fees are the single largest line item after compute.
**Mechanism**: a team currently paying ~$0.01-0.02/min combined STT+TTS vendor fees can self-host the omni-model on hardware they already provision for other inference, eliminating that marginal cost and one network round-trip per turn — provided the benchmark proves parity on tool-call accuracy and MOS, which nobody has independently verified yet.
**Measure**: cost per 1,000 call-minutes (vendor cascade vs. local omni, on identical call scenarios); tool-call accuracy and end-to-end latency delta between the two paths; adoption measured by GitHub stars/forks and number of distinct frameworks the adapter has been wired into within 90 days of release.

## Why Now
LFM3-Audio-2B and comparable omni-audio models only became viable on consumer-tier GPUs in the last few months, which is exactly why six independent hobbyist repos appeared in a two-week window — the capability is new enough that nobody has had time to productize it, but mature enough that a packaged version is buildable today, not a "once models improve" bet.

## Skill Angle
A migration-feasibility skill: given a team's pasted current architecture (vendor stack, tool definitions, latency/cost numbers), it produces a go/no-go assessment — estimated cost savings, a list of tool-calling features that may not map cleanly onto the omni-model's native tool_calls (e.g. parallel tool calls, streaming partial args), and a recommended hosting tier. This is distinct from the project: the project is the actual adapter/benchmark runtime; the skill is the one-shot analysis a team runs *before* committing to the migration.

## MVP Sketch
Scope: wire LFm3-Audio-2B behind a LiveKit Agents-compatible tool-calling interface; build a 15-scenario call benchmark (appointment booking, order lookup, simple FAQ) run against both the local-omni path and a Deepgram+GPT+Cartesia cascade on the same hardware budget. Stack: Python, the model's existing inference server, LiveKit Agents SDK for the adapter shim. The single validating experiment: does the local-omni path hit ≥95% of the cascade's tool-call accuracy at ≤50% of its p95 latency, on one consumer GPU, within a 3-week build.

## Risks & Open Questions
- The underlying model ecosystem (LFM3-Audio-2B and successors) is moving fast; the adapter may need frequent rework to track breaking changes upstream.
- Native tool_calls support in small audio-native models may be shallower than LLM function-calling (e.g. no parallel calls) — the benchmark could reveal the pattern doesn't actually hold up for complex agents, which would be a valid, useful negative result.
- GPU hosting cost (even "free" self-hosted) isn't actually free at scale; the cost comparison must include amortized hardware, not just marginal electricity, or it misleads adopters.
- Six parallel hobbyist efforts suggest this could consolidate around one of them before this project ships — worth checking in 4-6 weeks whether any has gained real traction.
