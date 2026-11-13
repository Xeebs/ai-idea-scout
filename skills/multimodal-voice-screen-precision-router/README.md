# Precision-Routing Auditor for Voice+Screen Agents

A portable prompt for finding out where a voice-driven, screen-watching AI agent is likely to misread small on-screen detail — and what routing policy would fix it — before you build or ship the fix.

This is for anyone designing, reviewing, or debugging an agent that talks to a user by voice while watching their shared screen: remote tech support, software walkthrough copilots, troubleshooting assistants. It works in any chat tool; no special setup, SDK, or screenshot upload required — you just describe the architecture in words.

## How to use it

Paste the block below into any AI chat tool, then give it:
1. **Your architecture**: which model(s) handle the voice/dialogue loop and which (if any) see the screen frames; how frames are captured if you know it (resolution, frame rate); and what UI the agent watches (web app, desktop app, mobile, embedded panel).
2. **The task list**: what the agent is actually asked to do with what it sees on screen — concrete examples, not "it helps with troubleshooting."
3. *(Optional, improves accuracy)* A transcript or support log showing specific moments the agent misread something or gave wrong instructions based on the screen.

If you leave the task list out, a good response will ask for concrete examples rather than guessing.

---

### The prompt

> You are auditing a voice+screen AI agent's architecture to find where it is likely to miss small on-screen detail, and to recommend a routing policy to a specialist model for those cases. Work only from what is given — never invent failure evidence, engagement numbers, or user complaints that weren't provided.
>
> First, extract the architecture facts: which model(s) handle voice and vision, whether a specialist/secondary model already exists, frame capture characteristics if stated, and the UI context.
>
> Then classify every visual subtask the agent performs against this taxonomy:
> - Scene-level context (what app/screen this is, general layout)
> - Small/dense body text (paragraphs, tooltips, fine print)
> - Status icons, toggles, checkboxes
> - Dense forms, tables, or settings grids
> - Numeric readouts, counters, graphs/charts
> - Error messages / modal dialogs
>
> For each category not already handled by a named specialist model, flag it as a likely-miss risk, with reasoning tied to known general-multimodal-model failure modes at typical screen-share resolution (small glyphs, dense layouts, low-contrast icons) — not a generic "AI might get this wrong." If a transcript or log was given, match specific misread incidents to categories and raise those to confirmed-miss, cited to the actual incident.
>
> Build a routing policy: for each likely- or confirmed-miss category, recommend a specialist type (OCR for text-heavy categories, a UI-element/icon detector for toggles and icons, a chart/table parser for numeric readouts) — name categories of model, not a single vendor you insist on — a rough confidence threshold at which the primary model should hand off, and a fallback for when the specialist is also low-confidence (ask the user to zoom or clarify; never guess).
>
> Explicitly list which categories do NOT need routing — where the primary model's own scene-level reasoning is already adequate — so the policy doesn't over-route and add latency for no accuracy gain.
>
> Output exactly this structure:
> ```
> ## Architecture Reviewed
> <restate the input, flag any missing facts you assumed or had to ask for>
>
> ## Risk Table
> | Category | Miss risk | Reasoning / evidence | Recommended specialist | Handoff confidence threshold | Priority |
> |---|---|---|---|---|---|
> <one row per taxonomy category>
>
> ## Routing Policy (pseudocode)
> <category -> specialist -> threshold -> fallback, as a short if/else or config block>
>
> ## Not Recommended For Routing
> <categories where the primary model stays sufficient, and why>
>
> ## Suggested Validation
> <what a 20-30 item benchmark of real screenshots for this specific UI should cover before shipping the policy>
> ```
>
> If no transcript/log was given, say explicitly that the risk table is architecture-level reasoning, not a measurement of observed failures. If the task list given is too thin to classify, ask for concrete task examples before producing a risk table rather than inventing plausible-sounding ones.
>
> Here is my architecture and task list:
> [paste your architecture description, task list, and optional transcript/log here]

## Why this exists

Teams building voice-driven, screen-sharing agents keep hitting the same failure — the general-purpose multimodal model that handles the voice+scene loop misses small text, dense settings menus, and tiny icons — and engineering blogs (Getstream.io, alexcloudstar.com) name the fix ("route precision tasks to a specialized CV model") without naming any reusable tool for deciding *where* to draw that routing boundary. The one working reference implementation found (NVIDIA's XR-AI docs) is a docs example, not something a team can run against their own architecture. This prompt is that missing design-time step: a repeatable way to turn "our agent keeps misreading the screen" into a concrete routing policy an engineering team can act on, before anyone writes the runtime middleware.

Full project context, evidence, and the sketch of the runtime (library) version of this idea: see [`ideas/multimodal-voice-screen-precision-router.md`](../../ideas/multimodal-voice-screen-precision-router.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
