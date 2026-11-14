---
name: voice-vision-session-reanchoring-middleware
description: Reviews a voice+vision agent's architecture (session length, what it watches, how fast the screen/scene changes, latency budget) and produces a visual-grounding degradation risk estimate with a recommended re-anchoring cadence and payload — the design step before wiring up a live re-anchoring scheduler. Use when a team is building or debugging a voice-driven screen-share, walkthrough, or accessibility agent that holds a session open past ~30 seconds of continuous visual engagement.
---

# Session-Degradation Risk Reviewer

## When to use this
Reach for this skill when someone is designing, or already running, a voice+vision agent (screen-share support call, live tutoring/onboarding walkthrough, voice-first screen reading for blind/low-vision users) that keeps a session open and watches video or a shared screen continuously, and either:
- is seeing the agent give instructions based on stale on-screen state ("click the button" when it's gone, describing a screen that already changed), or
- hasn't built it yet and wants to know, before wiring up a live re-anchoring loop, where in a session visual grounding is likely to degrade and how aggressively to re-anchor.

This is a design/review aid, not the runtime middleware itself. It produces the cadence and payload spec a team implements; it does not watch a live video stream or run inside a production session loop.

## Inputs
**Data source**: MANUAL — carried over with one clarification from the parent idea. The parent idea's runtime middleware is CONNECTED (it reads the live video/screen-share frame stream directly through LiveKit's or Pipecat's video-track ingestion). This skill is the design-time advisor that precedes that build, so it runs on MANUAL input only: the user types or pastes a short description of their agent's architecture. No live connector is read by this skill — it never touches an actual frame stream.

What the user hands over (ask for any that are missing before producing output):
1. **Typical session length** — median and max duration of a real session (e.g., "support calls run 2-5 minutes," "tutoring sessions run 20-40 minutes").
2. **What the agent is watching** — a static document, a slowly-scrolling page, an actively-edited IDE/spreadsheet, a live camera feed, a multi-step UI workflow.
3. **How often the visual content changes** — roughly how many meaningfully different screen/scene states occur per minute of a typical session.
4. **The underlying multimodal model and its known context window / stated session-length caveats**, if known.
5. **Per-turn latency budget** — how much added delay a re-anchoring event can afford without breaking the voice interaction's real-time feel (e.g., "turns must stay under 800ms").
6. **Any existing symptoms** — specific instances the user has seen of the agent referencing stale screen state, if the agent is already live.

## Procedure
1. **Confirm or request the six inputs above.** If the user gives a vague architecture description, ask one targeted follow-up per missing item rather than guessing — a cadence recommendation built on an assumed session length is worse than no recommendation.
2. **Build a degradation risk profile**, reasoned explicitly from the inputs, not a lookup table:
   - Map typical/max session length against the ~30-second degradation window named in current practitioner reporting on continuous voice+vision sessions (treat this 30-second figure as one practitioner's measured observation, not a universal constant — state that caveat in the output).
   - Weight the risk up for high change-frequency content (active editing, multi-step workflows) and down for static/slow content (a single document, a mostly-still camera).
   - Flag explicitly if the session length is short enough (well under 30 seconds) that re-anchoring is probably unnecessary overhead — the point of this skill is also to say "don't build this yet" when the risk doesn't justify it.
3. **Recommend a re-anchoring cadence**, stated as both a fixed-timer fallback and an adaptive rule:
   - Fixed baseline: a concrete interval (e.g., "25-30s") to use as a control/fallback when change-detection isn't available yet.
   - Adaptive rule: a plain-language trigger condition based on the user's stated change frequency (e.g., "re-anchor on any detected frame-diff above threshold X, with a hard ceiling of 20s between anchors regardless of detected change" for fast-changing content; "re-anchor every 45-60s" for static content).
4. **Recommend the anchor payload** — for each cadence tier, specify whether the anchor should be a full fresh frame re-sample, a lightweight diff/state summary ("what's changed since last anchor"), or both, reasoned against the stated latency budget and the vision-token cost of a full re-sample.
5. **Name the cost/latency tradeoff explicitly** — state in plain terms that a more aggressive cadence buys lower staleness risk at the price of added per-anchor latency and token cost, and give a rough qualitative read (low/medium/high added cost) for the recommended cadence against the stated latency budget.
6. **Sketch a minimal evaluation plan** — 3-5 bullets describing how the user could validate the recommendation with their own real session recordings (what to record, what timestamps to label, what "correct" looks like), so the recommendation is falsifiable rather than a one-shot guess.

## Output format
A single structured brief, in this order:
1. **Inputs used** — restate the six inputs as given/assumed, flagging any the user didn't provide and what default assumption was used instead.
2. **Risk profile** — one paragraph: is this session type high, medium, or low risk for mid-session visual grounding degradation, and why (tie explicitly to session length vs. the ~30s reference point and the stated change frequency).
3. **Recommended cadence** — the fixed-fallback number and the adaptive rule, each in one sentence.
4. **Recommended anchor payload** — full re-sample vs. diff summary vs. both, per cadence tier.
5. **Cost/latency tradeoff** — one short paragraph, qualitative.
6. **Evaluation plan** — 3-5 bullet points.
7. **Caveats** — at minimum, note that the 30-second figure is from one practitioner's testing, and that this recommendation should be validated against the user's own sessions and their specific model before being treated as final.

## Guardrails
- Never produce a cadence recommendation without first getting the six inputs (or explicit user confirmation to proceed on stated assumptions) — a number with no architecture behind it is worse than refusing to guess.
- Never present the ~30-second degradation window as a universal, model-agnostic constant; it is one named practitioner observation and must be flagged as such every time it anchors a recommendation.
- Never recommend the most aggressive possible cadence by default — always weigh the stated latency budget and name the cost tradeoff, even when the user doesn't ask about cost.
- Never claim this skill validates the recommendation itself — it produces a design hypothesis and an evaluation plan; only the user's own session recordings (or the runtime middleware's eval harness) can confirm it.
- Never conflate this skill with the runtime middleware — it does not read a live frame stream, does not run inside a production session loop, and does not replace the engineering work of actually building the re-anchoring scheduler.
