# Block Kit: Portable, Provider-Agnostic Call-Flow Building Blocks for Voice Agents

- **Status**: PROPOSED
- **Date**: 2026-11-17
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-17-voice-multimodal-agents.md · P4
- **Maturity verdict**: OPEN — only single-vendor, vendor-locked templates exist (CallSphere bundles, Telnyx's scheduling template, Dialogflow CX's English-only "prebuilt components"); no portable, provider-agnostic block layer usable across platforms the way v0 blocks are for web UI.
- **Format**: BOTH
- **Data Sources**: CONNECTED — compiles and pushes assembled flows via the Vapi/Retell/Pipecat agent-configuration APIs (all mature, documented REST APIs for assistant creation today); the component registry/compiler itself is the new piece.

## The Gap
An Indie Hackers post predicts "eventually, we'll reach a 'V0' layer for voice just like we have for web apps... pre-built blocks for onboarding, scheduling, and lead capture" — explicit "why doesn't this exist yet" framing from a builder, not a pointer to an existing product. Search for a cross-platform composable voice-agent component library found only single-vendor, often English-only, vendor-locked templates — nothing portable.

## The Project
A registry and compiler (think shadcn/ui, but for voice call flows): vetted, parameterized blocks for the handful of flows that recur across almost every client engagement — appointment scheduling with calendar-check, lead qualification Q&A, intake/triage, voicemail-to-callback — expressed in one portable intermediate schema that a CLI compiles down into a working Vapi, Retell, Pipecat, or LiveKit Agents assistant config. A builder picks blocks, fills in client-specific slots (business hours, services offered, escalation rules), and compiles to whichever platform the client is on, instead of writing the flow logic from scratch each time.

## Tangible Impact
**Population**: Freelance and small-agency voice-agent contractors — the same population the Indie Hackers contractor post comes from — who are paid to stand up near-identical call flows for SMB clients repeatedly. No hard headcount is available from search; proxy signal is the growth of Vapi/Retell's own in-platform template marketplaces and the volume of "voice AI agent setup" contractor gigs, both pointing at a real, recurring population without naming an exact size.
**Mechanism**: A builder assembling a new client's flow from vetted, tested blocks spends far less time on logic that's identical across clients and more time on what's actually client-specific, and ships fewer of the corner-case bugs that come from re-deriving scheduling/intake logic solo each time.
**Measure**: (1) time-to-first-working-flow per new client engagement, before vs. after adopting the block library; (2) number of corner-case defects caught in a standard test-call checklist per flow; (3) number of distinct target platforms a single block deploys to unmodified.

## Why Now
The underlying frameworks this compiles to (Pipecat, LiveKit Agents, Vapi, Retell) are all mature and actively maintained today — the missing piece is purely the portable component layer on top, not new model or infra capability.

## Skill Angle
A **call-flow requirements-intake skill**: given a client's described business process (pasted meeting notes, an intake form, or a transcript of a scoping call), it maps the requirements to the nearest existing blocks, flags gaps needing a custom block, and drafts the slot-parameter fill-in — a repeatable drafting task a builder can use even before touching the compiler.

## MVP Sketch
Scope: 4 blocks (scheduling, lead qualification, intake/triage, voicemail-to-callback) compiling to Vapi and Pipecat only. Stack: a YAML/JSON intermediate schema, a small Python/Node compiler CLI, blocks hosted as a public GitHub registry. Validating experiment: have 3 real or simulated freelance builds use the library for a new client flow and time them against a freshly-recalled past from-scratch build.
## Risks & Open Questions
- Platform APIs (Vapi/Retell) change fast; the compiler needs ongoing maintenance to stay compiled-correct, which is real ongoing cost for a small team.
- "Composable blocks" for voice may hit a ceiling faster than web UI blocks did — call flows have more client-specific branching logic than a scheduling widget does.
- If Vapi or Retell ship their own cross-platform template marketplace first, this collapses to redundant.
- Unclear how many contractors would adopt a third-party registry versus just keeping their own private template folder, which is the status quo today.
