# Pocket Dispatch: A Tool-Call Resolution Framework for On-Device Multimodal Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-iii.md · P7
- **Maturity verdict**: PARTIAL (for the exact Gemini Nano case, no library was found — Google's own ML Kit function-calling and ADK-for-Android on-device backends are reported, by third-party field accounts, to lack a tool-execution path, requiring manual loop-closing; but the general problem isn't fully unsolved elsewhere — `lemcoder/koog-edge` is a maintained Kotlin framework shipping tool-calling for other on-device models via Cactus Compute/Leap SDK, and `uny/koog-ondevice` wraps Gemini Nano through Koog, though its listing doesn't confirm tool-calling support)
- **Format**: PROJECT
- **Data Sources**: CONNECTED — calls the host device's on-device model runtime directly (Android AICore / ML Kit GenAI APIs exposing Gemini Nano) and the app's own locally-registered tool-function catalog; there is nothing for a user to paste, since the framework operates entirely on live API calls and local function signatures.

## The Gap
A 2026 developer field guide on building with Gemini Nano reports that "on-device tool calling... required closing the agent loop manually, and... the model invented a plausible but wrong tool name until the exact names were pinned in the system instruction," and that Google's own guidance is a hybrid split (cloud orchestrates tools, on-device sub-agents stay text-only) rather than full on-device tool calling. The source frames this explicitly as *not* a flip-a-checkbox capability — the described workaround is a manual, per-app hack repeated by every developer who tries, not a packaged, reusable framework.

## The Project
A reusable framework that handles tool-call dispatch and name resolution for on-device multimodal models, closing the agent loop automatically instead of requiring each app developer to hand-pin exact tool names into the system prompt. The centerpiece is a fuzzy tool-name resolution layer — when the model invents a plausible-but-wrong tool name, the framework matches it back to the real registered tool via embedding similarity rather than failing outright — paired with an automatic loop-closer that detects a function-call-shaped response, executes it against the app's local tool registry, and re-prompts the model with the result.

Components: a tool-registration API, an embedding-based name-resolution matcher, an automatic execute-and-reprompt loop-closer, and a benchmark harness comparing resolution success against the hand-pinned-prompt baseline the field guide describes.

## Tangible Impact
**Population**: Android app developers building offline-capable multimodal agent features on Gemini Nano-class on-device models (Pixel 8+ and a growing set of 2025-2026 Android flagships with AICore), and by extension the end users of those apps — people using a health-symptom-logging app, an offline field-inspection assistant, or a privacy-sensitive journaling app — who currently get no working tool-calling at all because developers find the manual loop-closing too brittle to ship.
**Mechanism**: packaging name-resolution and loop-closing as a reusable library turns "on-device tool calling isn't a checkbox you flip" into something closer to one, letting more apps actually ship offline, cloud-free tool-calling features instead of abandoning the attempt — directly expanding what on-device AI features reach users with no network dependency or cloud data exposure.
**Measure**: tool-call success rate (correct tool invoked) across a benchmark prompt set, comparing the hand-pinned-prompt baseline against the framework's resolution layer; developer integration time to add tool-calling to a sample app, before vs. after; invented-tool-name rate caught and corrected by the framework vs. left as an unhandled failure.

## Why Now
Gemini Nano-class on-device models only recently became broadly available on 2026 Android devices, and the field guide's reported pain is current, not hypothetical. Google's own current guidance is a hybrid split rather than full on-device tool-calling support, leaving an open window for independent tooling, and adjacent frameworks (`koog-edge`) already prove the general dispatch-and-resolution approach is buildable today against other on-device models.

## MVP Sketch
Extend the approach demonstrated by `lemcoder/koog-edge` to specifically target Gemini Nano via ML Kit GenAI/AICore, adding an embedding-similarity name-resolution layer and an automatic loop-closer so a host app only needs to declare its tools once. Validate on a reference Android demo app (a notes/calendar assistant) running a fixed set of 30 tool-calling prompts, measuring success rate against the manual hand-pinned-prompt baseline described in the digest's source field guide.

## Risks & Open Questions
- Google's own platform limits (simultaneous-request caps, daily invocation caps for battery management) constrain throughput independent of how good the dispatch logic itself is.
- If Google ships native on-device tool-calling support in ML Kit/AICore before this framework gains adoption, it is immediately obsoleted — the digest itself flags this timing risk.
- Fuzzy name-resolution could silently dispatch the *wrong* tool with high confidence, a failure mode potentially worse than today's loud hard failure.
- The population of on-device multimodal apps attempting tool-calling at all today may still be small, limiting real-world validation data available before launch.
