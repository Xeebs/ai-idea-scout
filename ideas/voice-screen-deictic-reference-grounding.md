# Point To It: A Deictic Reference Grounding Layer for Voice+Screen Multimodal Agents

- **Status**: PUBLISHED
- **Date**: 2026-11-18
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-18-voice-multimodal-agents.md · P4
- **Maturity verdict**: PARTIAL (only academic work — EgoPoint-Ground/SV-CoT dataset+baseline, a 2025 Imperial College "put that there" gaze+pointing paper for virtual windows — plus one narrow practitioner workaround (routing small on-screen text to a separate CV model) were found; no production system resolves general deictic reference)
- **Format**: PROJECT
- **Data Sources**: CONNECTED — live screen-share video frames via WebRTC (mature; standard in LiveKit/Pipecat voice-agent stacks already), the browser/app DOM or OS accessibility tree via Chrome DevTools Protocol or platform accessibility APIs (mature, widely used for automated testing and screen readers), and a vision-grounding model API for non-DOM/native-app content (e.g. Molmo's point-at-coordinates grounding or Claude's computer-use region grounding — both exist today, neither is wired into a deictic-resolution pipeline).

## The Gap

When a caller on a voice+vision support call says "this screen" or "the red button on the left," production multimodal agents have no mechanism to resolve what's actually being pointed at — a practitioner blog states this plainly, and a 2026 arXiv paper (abs/2602.05671) independently concludes multimodal voice agents lack the deictic grounding human remote-sighted assistants rely on for physical-inspection tasks. A confirming WebSearch of 2026 AI screen-share support vendors (ScreenMeet, Retell AI, Atomicwork, a LiveKit/Beyond Presence tutorial) found real shipped products that feed screen frames to a vision model at ~1fps and give voice guidance back, but every one leaves the "this"/"that" link entirely to the base model's unaided judgment — none runs a dedicated grounding step. The only concrete mitigation anywhere is the narrow workaround already covered by this repo's existing "Screen Zoom" idea (routing small on-screen *text* to a specialist OCR/CV model) — that solves misread text, not "which thing is the caller talking about."

## The Project

A middleware layer that sits between a voice+vision agent's reasoning step and the screen feed it's watching, and turns a spoken deictic phrase into a concrete bounding box or coordinate on the current frame before the agent decides what to do. On each turn with a deictic cue ("this," "that," "here," "the one on the left," "it"), the layer: (1) pulls the DOM/accessibility tree if the content is a web page or native app that exposes one, matching the phrase against labeled, positioned elements first (cheapest, most reliable path); (2) falls back to a vision-grounding model call against the current frame when no accessibility tree exists (native canvas apps, video, physical camera feeds); (3) cross-references recent screen diffs and cursor/gaze position to disambiguate competing candidates ("the thing that just changed" beats "the thing in that general area"); (4) returns a calibrated confidence score, and below threshold, emits a one-line clarifying question ("Do you mean the blue Save button, or the gray Cancel button below it?") instead of guessing.

Component list: a frame/DOM capture adapter per platform (browser extension + OS accessibility hook), a grounding resolver (DOM-match-first, vision-model-fallback), a disambiguation-prompt generator, and an evaluation harness built on the public EgoPoint-Ground dataset plus a self-collected screen-UI deictic-reference test set.

## Tangible Impact

**Population**: End users on AI-mediated remote tech-support and software-walkthrough calls — the same callers already served by the ~2.8 million U.S. customer-service-representative workforce (BLS, 2024) that AI voice+screen support agents (ScreenMeet, Retell AI, Atomicwork-class products confirmed shipping in 2026) are starting to supplement or replace. These are typically non-technical callers who describe UI elements by appearance or position ("the red button," "the thing on the left") rather than by exact label, because that's how people naturally talk about screens they're looking at.
**Mechanism**: Today, when a multimodal support agent misresolves "this," it either acts on the wrong element (a wrong click/instruction, extending the call and risking a bad outcome) or the underlying model silently guesses without flagging uncertainty. A grounding layer that resolves the reference correctly — or asks one clarifying question when it can't — replaces silent wrong guesses with either a correct action or a fast, cheap disambiguation turn.
**Measure**: (1) deictic-resolution accuracy on a held-out screen-UI test set (DOM-available and vision-only subsets reported separately); (2) rate of agent actions taken on a misresolved target, before vs. after; (3) call duration/turn count change on a benchmark set of scripted screen-share support scenarios with embedded ambiguous references.

## Why Now

Mature, general-purpose vision-grounding models with explicit pointing/region output (Molmo-class open models, Claude's computer-use grounding) now exist and are cheap enough to call per-turn — they just aren't wired into a deictic-resolution pipeline anywhere found in this search. At the same time, voice+screen support products went from pilot to shipping vendor feature in 2026 (confirmed via WebSearch across multiple vendors this cycle), so the gap is now live in production call volume rather than hypothetical.

## MVP Sketch

Scope to one platform first: a Chrome extension + small LiveKit/Pipecat-compatible middleware that (a) reads the live DOM/accessibility tree of the shared tab, (b) matches a transcribed deictic phrase against labeled elements using a lightweight embedding/keyword match plus position-proximity scoring, (c) falls back to a single Molmo/Claude vision-grounding call only when no DOM match clears a confidence floor, and (d) emits either a resolved element ID or a clarifying question. Validate on 30 scripted screen-share scenarios (web-app support flows) with deliberately ambiguous spoken references, scoring resolution accuracy and clarifying-question rate against a human-labeled ground truth. Stack: TypeScript browser extension, a small Python/Node resolver service, Molmo or Claude vision API for the fallback path. Buildable by 1–2 people in 3–4 weeks for the web-only MVP; native-app/physical-camera support is a clearly separate phase 2.

## Risks & Open Questions

- The DOM-first path only works for web content with a real accessibility tree — native apps, games, and physical-camera (AR/smart-glasses) use cases need the harder vision-only fallback, which is where most of the open research risk sits.
- Vision-grounding models' pointing accuracy on dense, cluttered real-world UIs (not the clean benchmark images most grounding models are evaluated on) is unproven; the MVP's own eval set is the first honest test of this.
- A clarifying-question fallback adds a conversational turn — if confidence calibration is too conservative, it could annoy callers more than an occasional wrong guess would; needs tuning against real call transcripts, not just lab accuracy.
- This might already be quietly solved inside a vendor's unpublished implementation (ScreenMeet, Atomicwork) — the WebSearch found marketing claims but no technical disclosure, so there's a real chance a shipped black-box solution exists that this project would be reinventing poorly without their training data.
