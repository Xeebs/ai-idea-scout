# Screen Zoom: A Precision-Routing Layer for Multimodal Voice+Screen Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-ii.md · P1
- **Maturity verdict**: PARTIAL (NVIDIA's XR-AI docs ship a real but narrow, non-packaged reference router sending direct visual questions to one model and screen frames to another; practitioner blogs at Getstream.io and alexcloudstar.com recommend the pattern but name no reusable, product-grade middleware; an arXiv paper treats per-action VLM routing as research-only)
- **Format**: BOTH

## The Gap
Voice agents that also watch a shared screen (remote tech support, software walkthroughs, troubleshooting copilots) keep hitting the same failure: the general-purpose multimodal model that handles the voice+scene loop misses small on-screen text, dense settings menus, and tiny icons. Getstream.io's engineering blog names the fix directly — "route precision tasks ... to a specialized CV model instead of expecting the multimodal model to catch everything" — and alexcloudstar.com calls orchestrating modalities together "the hardest part," not any single modality. The one working implementation found (NVIDIA's XR-AI docs example) proves the pattern works, but it's explicitly a docs example, not a library anyone can drop into their own voice+screen stack.

## The Project
A routing middleware that sits between a voice+screen agent's main multimodal loop and its downstream model calls. It classifies each visual subtask by granularity (scene-level context vs. small-text/dense-UI/icon-level detail) using cheap heuristics (bounding-box density, text-size estimation from the frame, a lightweight pre-classifier) and dispatches precision tasks to a dedicated CV/OCR-capable model while the primary multimodal model keeps handling voice dialogue and scene-level reasoning. It ships as a stack-agnostic adapter (Pipecat/LiveKit-compatible) rather than a bespoke integration.

Components: a frame-triage classifier, a pluggable specialist-model adapter (defaults to an open OCR/detection model, swappable), a routing-decision log for debugging misroutes, and a benchmark of real small-UI-element tasks (settings toggles, dense forms, tiny status icons) to measure accuracy gain over single-model baselines.

## Tangible Impact
**Population**: end users of voice-driven, screen-sharing support and walkthrough agents — e.g., customers troubleshooting software or hardware settings by talking to an AI while sharing their screen, a pattern already shipping in customer-support copilots and onboarding assistants per the digest's cited vendor posts.
**Mechanism**: correctly reading small text and dense UI elements means the agent stops asking users to repeat themselves or giving wrong instructions based on misread screen content, which is the direct cause of abandoned self-service sessions and escalations to a human.
**Measure**: small-UI-element task accuracy with vs. without routing (on the precision-task benchmark); session escalation-to-human rate in a pilot deployment; average turns-to-resolution for tasks involving dense/small on-screen elements.

## Why Now
Cheap, fast OCR/detection specialist models and low-latency multimodal APIs with vision+voice streaming are now mature enough to run a routing decision inside a voice turn's latency budget — exactly the gap the Getstream.io and alexcloudstar.com posts describe as newly visible now that screen-watching voice agents are shipping broadly.

## Skill Angle
A Claude Code skill that, given a description or transcript of an existing multimodal voice+screen agent's architecture (what the primary model sees, what tasks it handles), audits where precision-routing boundaries should go — flagging which visual subtask categories are likely to be missed by the general model and recommending a routing policy (which categories to route, to what kind of specialist, with what confidence threshold). Output: a routing-policy recommendation doc a team can hand to engineering, distinct from the runtime middleware itself.

## MVP Sketch
Build the frame-triage classifier and one specialist-model adapter (OCR for small text) as a Pipecat plugin; assemble ~30 real small-UI-element screenshots/tasks as a benchmark; compare task accuracy with routing on vs. off using an existing open multimodal model as the baseline. The single experiment: does routing measurably raise small-text/dense-UI task accuracy over the single-model baseline without adding latency the voice turn can't absorb.

## Risks & Open Questions
- The triage classifier itself could misroute, adding latency without accuracy gain — the MVP must measure net latency cost, not just accuracy.
- NVIDIA's reference implementation suggests the pattern might get absorbed into vendor SDKs before an independent middleware gains adoption.
- Benchmark construction (real dense-UI screenshots with ground truth) is manual and may not generalize across UI frameworks.
- If next-generation multimodal models close the small-detail gap natively, the routing layer's value window could be short.
