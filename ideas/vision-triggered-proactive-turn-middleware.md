# Scene Speak: A Frame-Diff-Triggered Proactive-Turn Middleware for Multimodal Voice+Vision Agents

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-20-voice-multimodal-agents.md · P5
- **Maturity verdict**: PARTIAL — an arXiv study on ChatGPT's voice mode confirms vision is used only as context for speech-triggered turns, never as a turn trigger itself; the OpenAI Realtime API's own developer community confirms "all triggering is either voice-based or manual"; Pydantic AI's "Watch mode" camera example is a fixed 3.5-second timer nudge the model can ignore, not real scene-change detection ("context only," explicitly does not start a turn); one independent dev's "Iris" blog prototype (Gemini Live) does implement real frame-diff thresholding, but it's a one-person blog post with no located repo.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads live video frames via the host multimodal realtime API's own vision-input stream (OpenAI Realtime API, Gemini Live API — both mature, actively documented APIs that already accept video frames mid-session), computing frame-diff/change-detection server-side against the preceding frame; no pasted video or images are required for the live runtime. (The companion skill's input is MANUAL — see Skill Angle.)

## The Gap

Current voice+vision agents can "see" but never speak first because of what they saw. The arXiv finding is explicit: ChatGPT's voice mode "cannot currently respond to changes in the visual scene mid-utterance by uttering a new turn." Stream's open-source Vision Agents framework and the older i-Code Studio prototype both combine real-time audio/video in one session, but turn-taking in both stays speech-triggered. The one real counter-example — a solo blog post implementing genuine frame-diff thresholding (threshold 20, 8s cooldown) against Gemini Live — is a prototype with no maintained repo, proving the idea works but that nobody has shipped it as a usable library.

## The Project

A middleware layer that sits between a camera/screen feed and a realtime multimodal API session: it computes a lightweight frame-diff (or a cheap vision-model delta score) on each incoming frame, and when the delta crosses a configurable threshold with a cooldown (generalizing the one working "Iris" prototype's threshold-20/8s-cooldown approach into a tunable, documented parameter), it injects a system-level nudge that causes the model to proactively initiate a new turn — e.g. "say something about what just changed," not just silently update context. Ships with presets for the most obvious real use cases (a cooking-camera "the pan is smoking" alert, a workshop-safety "someone entered the restricted zone" alert) so adopters aren't tuning thresholds from zero.

## Tangible Impact

**Population**: Builders of hands-busy or heads-down multimodal assistants where the user cannot be expected to ask the right question at the right moment — cooking assistants, workshop/lab safety monitors, physical-therapy form-checking apps, and accessibility aids for low-vision users who need the agent to speak up about a visual event (a stove left on, a fall risk) rather than wait to be asked. Builds on the same multimodal realtime API base (OpenAI Realtime, Gemini Live) whose developer adoption underlies the broader voice-AI-agent market estimated at $3.5–5.1B in 2026 (Grand View Research, Meticulous Research).
**Mechanism**: Without this, every one of these use cases either gets no proactive alerting at all (the overwhelming current default, per the arXiv finding) or a bespoke one-off hack like the single "Iris" blog prototype — meaning the agent stays silent exactly when a visual event is the whole point of the product. A shared, tunable middleware turns "detect this kind of visual change and say something" into a config, not a research project.
**Measure**: time-to-notify from the actual visual event to the agent's spoken alert (latency budget); false-positive proactive-turn rate per hour of real use (noise from irrelevant scene changes); task-level outcome in a concrete pilot (e.g. time-to-notice a boiling-over pan in a cooking-assistant trial, with vs. without the middleware).

## Why Now

Both major realtime multimodal APIs (OpenAI Realtime, Gemini Live) now accept live video streams in the same session as voice — the raw capability this middleware needs has existed only since 2026's realtime-API maturation, and the one working prototype (Iris) proves the trigger mechanism itself is simple enough to generalize now rather than waiting on any new model capability.

## Skill Angle

A "trigger policy designer" skill: given a plain-text description of the use case (e.g. "a cooking assistant watching a stovetop camera for smoke or boil-over"), it drafts the specific trigger-policy spec — what counts as a meaningful visual change for this scenario, a starting threshold/cooldown, and the exact system-nudge prompt text to inject — so an adopter has a tuned starting config instead of guessing at the two raw parameters from scratch.

## MVP Sketch

Scope: one realtime API target (start with Gemini Live, the one with a working reference prototype to validate against), 2-3 preset use cases, and a single frame-diff detector (no vision-model delta scoring yet). Stack: a small Python/TypeScript middleware sitting in the existing session's video pipe, injecting a text event the model sees as a system turn. Validating experiment: reproduce the "Iris" blog's own smoke-test (does a genuine scene change reliably trigger a proactive turn without excessive false positives over a real multi-minute session) as the pass/fail bar before adding presets.

## Risks & Open Questions

- Naive frame-diff is sensitive to lighting flicker and camera noise — the real engineering risk is tuning false-positive rate down without also missing genuine events, which the one existing prototype only lightly validated.
- If OpenAI or Google ship native scene-change-triggered turns in a future Realtime/Live API release, this middleware becomes a thin shim rather than a necessary layer — worth monitoring both vendors' realtime-API changelogs.
- Overly aggressive proactive interruption could make an assistant feel intrusive rather than helpful; the UX design of "when should the agent actually speak unprompted" needs real user testing, not just a tunable threshold.
- A vision-model-based delta score (richer than pixel-diff) would catch semantically meaningful changes pixel-diff misses, but adds latency and cost — worth scoping as a v2, not blocking the MVP on it.
