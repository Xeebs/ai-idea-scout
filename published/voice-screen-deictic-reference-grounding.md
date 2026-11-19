# Point To It: A Deictic Reference Grounding Layer for Voice+Screen Multimodal Agents

Say you're on a support call with an AI agent that can see your screen. You say "this button isn't working" — and the agent has no idea which button you mean. Not because its vision model is weak, but because nobody built the piece that turns "this" into a coordinate. That piece doesn't exist yet, anywhere, in production.

## The Gap

Voice+screen support products shipped for real in 2026 — ScreenMeet, Retell AI, Atomicwork, and a LiveKit/Beyond Presence tutorial all describe systems that feed live screen frames to a vision model at roughly 1fps and talk the caller through a fix. Every one of them leaves the hardest part — resolving "this," "that," "the red button on the left" — to the base model's unaided judgment. There's no dedicated grounding step anywhere in the stack.

This isn't a hunch. A practitioner engineering post states it directly: "when callers say 'this screen' or 'the red button on the left,' the agent has zero visual grounding," and that "the hardest part of multimodal agents isn't any single modality — it's orchestrating them together." A 2026 arXiv paper (abs/2602.05671) arrives at the same conclusion independently, from the academic side: multimodal voice agents still lack the kind of environmentally-occasioned visual grounding that human remote-sighted assistants rely on for physical-inspection tasks.

Search the literature and you find real movement, just not a shipped answer. A March 2026 paper introduces EgoPoint-Ground, an egocentric deictic-grounding dataset, with a baseline model called SV-CoT. A related benchmark paper (EcoG) argues that existing multimodal benchmarks skip deictic reasoning entirely. A 2025 Imperial College paper solves "put that there" for virtual windows via gaze and pointing — a different problem surface than screen UI. The one production mitigation that exists at all is narrow: routing small on-screen *text* to a specialist CV model when it's misread — a fix for bad OCR, not for figuring out what the caller is pointing at.

## The Project

The fix is a middleware layer that sits between a voice+vision agent's reasoning step and the screen it's watching, and turns a spoken deictic phrase into an actual bounding box before the agent acts on it.

On a turn with a deictic cue, the layer works in order of cost and reliability. First, if the content is a web page or native app with an accessibility tree, it matches the phrase against labeled, positioned elements directly — cheap and precise. If no tree exists (native canvas apps, video, a physical camera feed), it falls back to a vision-grounding model call against the current frame. Either way, it cross-references recent screen diffs and cursor position to break ties — "the thing that just changed" beats "the thing in that general area" when two candidates are plausible. And when confidence comes back below threshold, it doesn't guess: it asks one clarifying question — "Do you mean the blue Save button, or the gray Cancel button below it?" — instead of silently acting on the wrong element.

The pieces: a frame/DOM capture adapter per platform, a grounding resolver that tries DOM-match before vision-fallback, a disambiguation-prompt generator, and an evaluation harness built on the public EgoPoint-Ground dataset plus a self-collected set of screen-UI deictic references.

## Tangible Impact

**Population**: End users on AI-mediated remote tech-support and software-walkthrough calls — the same population already served by the roughly 2.8 million U.S. customer-service-representative workforce (BLS, 2024) that AI voice+screen support agents are starting to supplement or replace. These are mostly non-technical callers who describe UI elements by appearance or position — "the red button," "the thing on the left" — because that's how people naturally talk about a screen they're looking at, not by exact label.

**Mechanism**: Right now, when a multimodal support agent misresolves "this," it either acts on the wrong element — a bad click or instruction that extends the call and risks a worse outcome — or the model guesses silently with no flag that it was uncertain. A grounding layer replaces that silent wrong guess with either a correctly resolved action or one fast, cheap clarifying turn.

**Measure**: deictic-resolution accuracy on a held-out screen-UI test set, reported separately for DOM-available and vision-only cases; the rate of agent actions taken on a misresolved target, before vs. after; and call duration/turn count on a benchmark set of scripted screen-share support scenarios with deliberately embedded ambiguous references.

## Why Now

Vision-grounding models with explicit pointing/region output — Molmo-class open models, Claude's computer-use grounding — are now mature and cheap enough to call on every turn, and yet nobody's wired one into a deictic-resolution pipeline. At the same time, voice+screen support went from pilot to shipping vendor feature across 2026, so this gap now sits in live production call volume, not a hypothetical.

## Risks & Open Questions

- The DOM-first path only covers web content with a real accessibility tree. Native apps, games, and physical-camera use cases (AR, smart glasses) need the harder vision-only fallback — that's where most of the open research risk actually sits.
- Vision-grounding models' pointing accuracy on dense, cluttered real-world UIs — not the clean benchmark images most of them are evaluated on — is unproven. The project's own eval set would be the first honest test of this.
- A clarifying-question fallback costs a conversational turn. If the confidence threshold is tuned too conservatively, it could annoy callers more than an occasional wrong guess would — this needs tuning against real call transcripts, not lab accuracy alone.
- This might already be quietly solved inside a vendor's unpublished implementation. The search here found marketing claims from ScreenMeet, Atomicwork, and similar products, but no technical disclosure — there's a real chance a shipped black-box solution exists that this project would otherwise be reinventing poorly, without their training data.

---

Surfaced from `research/2026-11-18-voice-multimodal-agents.md`, pattern `P4`.
