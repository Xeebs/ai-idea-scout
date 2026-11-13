---
name: multimodal-voice-screen-precision-router
description: Audits a voice+screen agent's architecture description (and, optionally, session transcripts) to find visual subtasks the primary multimodal model is likely missing — small text, dense UI, icons — and produces a routing-policy recommendation for where to add a specialist CV/OCR model. Use when designing, reviewing, or debugging a voice-driven screen-sharing agent (remote support, software walkthrough, troubleshooting copilot) that keeps misreading on-screen detail.
---

# Precision-Routing Auditor for Voice+Screen Agents

## When to use this
A team is building, reviewing, or debugging an agent that talks to a user by voice while watching their shared screen (remote tech support, onboarding walkthroughs, troubleshooting copilots), and either (a) hasn't yet decided whether it needs a specialist model alongside its main multimodal/voice model, or (b) has users reporting the agent misreads small text, dense settings panels, tiny icons, or status toggles. The trigger moment is "where in my architecture should I add a routing boundary to a specialist model, and for which tasks" — not a request to build or run the routing middleware itself.

## Inputs
**Data source**: Manual — the user pastes a description of their existing or planned architecture: which model handles the voice/dialogue loop, which model (if any) sees screen frames, how frames are captured (resolution, frame rate if known), and the list of tasks the agent is asked to perform on-screen. Optionally they also paste a session transcript or support log showing specific misread/failed moments. There is no connector or live system access here — this is a static design/review pass over text the user provides, not a runtime integration or screenshot analysis.

If the architecture description omits model names, frame resolution, or task list entirely, ask for at least the task list before proceeding — a routing recommendation without knowing what the agent is asked to *do* on-screen is a guess, not an audit.

## Procedure
1. **Extract the architecture facts** from the input: primary model(s) handling voice + vision, whether any specialist/secondary model already exists, frame capture characteristics if stated, and the UI context (web app, native desktop, mobile, embedded device panel).
2. **Enumerate the visual subtasks** the agent performs or is asked to perform, and classify each against this fixed taxonomy:
   - Scene-level context (what app/screen is this, general layout orientation)
   - Small/dense body text (paragraphs, tooltips, fine print)
   - Status icons, toggles, checkboxes
   - Dense forms, tables, or settings grids
   - Numeric readouts, counters, graphs/charts
   - Error messages / modal dialogs
3. **Flag likely misses**: for every subtask category not already handled by a named specialist model, mark it a likely-miss risk, with the reasoning tied to known general-multimodal-model failure modes at typical screen-share resolutions (small glyphs, dense layouts, low-contrast icons) — never a generic "AI might get this wrong."
4. **Cross-reference evidence if given**: if a transcript/log was provided, match specific misread incidents to taxonomy categories and use them to raise that category's priority from likely to confirmed.
5. **Build the routing policy**: for each likely-miss or confirmed-miss category, recommend a specialist type (OCR engine for text-heavy categories, a UI-element/icon detector for toggles and icons, a chart/table parser for numeric readouts), a rough confidence threshold at which the primary model should hand off rather than answer itself, and a fallback if the specialist is unavailable or also low-confidence (ask the user to zoom/clarify, don't guess).
6. **State what's NOT a risk**: explicitly list categories where the primary model's own scene-level reasoning is adequate, so the team doesn't over-route and add latency nobody needs.

## Output format
A **Routing-Policy Recommendation Doc**:

```
## Architecture Reviewed
<one-paragraph restatement of the input architecture, flagging any missing facts assumed or asked for>

## Risk Table
| Category | Miss risk | Reasoning / evidence | Recommended specialist | Handoff confidence threshold | Priority |
|---|---|---|---|---|---|
<one row per taxonomy category>

## Routing Policy (pseudocode)
<short if/else or config-shaped block: category -> specialist -> threshold -> fallback>

## Not Recommended For Routing
<categories where the primary model stays sufficient, and why>

## Suggested Validation
<what a 20-30 item benchmark of real screenshots for this specific UI should cover before shipping the policy>
```

## Guardrails
- Never invent engagement numbers, user complaints, or failure evidence that wasn't in the input — if no transcript was given, say the risk table is based on architecture-level reasoning alone, not observed failures.
- Never recommend a single named commercial vendor as the only viable specialist — name a model/technique category (open OCR, UI-element detector) with example options, and let the team pick.
- Never present this as a completed accuracy audit — it is a design-time risk review of a description, not a measurement of the live system. Say so explicitly in the output if no transcript/benchmark data was supplied.
- Do not skip the "Not Recommended For Routing" section — a policy that routes everything adds latency without the accuracy gain the whole pattern exists to produce.
- If the task list given is too thin to classify (e.g., only "it watches the screen" with no task examples), ask for concrete task examples before producing a risk table — don't fabricate plausible-sounding tasks.
