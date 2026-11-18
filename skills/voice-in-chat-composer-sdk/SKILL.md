---
name: voice-in-chat-composer-sdk
description: Drafts the concrete frontend/backend diff for bolting realtime voice (Gemini Multimodal Live or OpenAI Realtime) onto an existing text-first chat composer, inline in the same input and message thread. Use when someone wants to add a mic button to a chat UI they already have, not build a new standalone voice app.
---

# Voice-in-Composer Integration Scaffolder

## When to use this
The user already has a working text-first chat UI (a support widget, an internal tool, a consumer AI chat app, anything with a text input + send button + message list) and wants to add voice input/output *inline in that same composer and thread* — not a separate voice-only screen or app. The trigger phrase is something like "add voice to our chat" or "can users talk instead of type in our existing chat box" where "existing" is the operative word. If the user wants a brand-new standalone voice app with no existing chat UI, this is the wrong skill — that's a from-scratch build, not an integration diff.

## Inputs
**Data source**: Connected — the Gemini Multimodal Live API (`BidiGenerateContent` WebSocket), mature and documented today, is the default target backend this skill writes integration code against; an OpenAI Realtime API variant is offered as the alternate. The skill itself does not call either API at design time — it writes code that will, at runtime, once the user deploys it, reaching into their chosen provider's live connector rather than requiring any manual transcript pasting.

To produce a real diff (not a generic template), the user must hand over:
1. **The actual composer component source** — pasted verbatim (the text `<input>`/`<textarea>`, the send handler/function, and the piece of state or store that holds the message list). A description in prose is a fallback, not a substitute — flag reduced specificity if no code is pasted.
2. **Frontend framework** — React, Vue, or vanilla JS/TS (changes the hook/component shape drafted).
3. **Backend runtime for the relay** — Node/Express, Next.js API routes/route handlers, or "none yet" (changes where the relay stub gets written).
4. **Target provider** — Gemini Multimodal Live or OpenAI Realtime. If unstated, default to Gemini Multimodal Live (the mature, documented reference pattern) and say so explicitly in the output rather than silently guessing.
5. **Interaction mode** — push-to-talk (hold a button to speak) or continuous open-mic streaming. If unstated, default to push-to-talk (safer default: lower cost, fewer false triggers) and say so.
6. **Existing auth pattern for text API calls** — e.g. "session cookie", "JWT in an Authorization header" — so the relay's auth handshake reuses it instead of inventing a new scheme.

## Procedure
1. **Parse the pasted composer code.** Identify: the input element/ref, the send handler function signature, the message-list state update call (e.g. `setMessages`, a Redux action, a Zustand store setter). If no code was pasted, use `[YOUR_SEND_HANDLER]`-style placeholders throughout rather than inventing plausible-looking function names that won't match the user's real file.
2. **Resolve the provider and mode** from input #4 and #5, defaulting as described above and stating the default explicitly in the output header.
3. **Draft the frontend diff**: a mic button added next to the existing send button, wired to a `VoiceSession` hook/class that:
   - Captures mic audio via `getUserMedia` and encodes to 16kHz PCM chunks (Gemini) or the provider's documented input format.
   - Opens a WebSocket to the user's own backend relay (never directly to the provider from the browser — the API key must never reach client code).
   - On receiving audio chunks back (24kHz for Gemini), queues them for gapless playback via the Web Audio API, and on receiving transcript text, appends it into the *same* message-list state update the existing text send handler already uses — so a voice turn renders as an ordinary chat message, not a separate UI mode.
4. **Draft the backend relay stub**, sized to the stated backend runtime: a WebSocket endpoint that (a) authenticates the inbound browser connection by reusing the stated existing auth pattern, (b) opens the outbound connection to the provider's realtime WebSocket using a server-side-only API key read from an environment variable, and (c) pipes audio/text frames in both directions with minimal buffering.
5. **Draft the auth handshake note**: one short paragraph stating plainly that the browser never holds a provider API key, the relay holds it server-side, and the browser-to-relay leg reuses the existing session/token scheme named in input #6.
6. **Attach the standing risk flags** (every output, not just when relevant): mic permission prompts differ by browser (Safari's stricter permission model), audio playback can be blocked by browser autoplay policy until a user gesture occurs, and continuous open-mic mode has real per-minute cost implications the user should confirm against their provider's pricing before shipping.
7. **List manual follow-up steps**: npm/pip package installs needed, environment variables to set, and a note that this diff has not been run or tested — it is a drafted starting point for the user's own PR, not verified working code.

## Output format
A single markdown document with these sections in order:
1. **Assumptions** — provider, mode, and any defaulted inputs, stated plainly (e.g. "No provider stated; defaulting to Gemini Multimodal Live").
2. **Frontend diff** — one fenced code block per changed/new file, using `+`/`-` diff-style lines where editing existing pasted code, plain new-file content where adding a new hook/component.
3. **Backend relay stub** — one fenced code block, a complete new file (not a diff, since this is new code).
4. **Auth handshake** — one short paragraph, no code.
5. **Risk flags** — a fixed 3-item bullet list (permissions, autoplay, cost) plus any input-specific risks noticed while parsing.
6. **Manual follow-up checklist** — a bullet checklist of install/env/test steps.

## Guardrails
- Never invent plausible-looking function or variable names standing in for the user's real code when no code was pasted — use explicit `[PLACEHOLDER]` markers instead, and say in Assumptions that specificity is reduced.
- Never write a provider API key into any frontend/browser code path in the drafted diff — it always lives in the backend relay's environment only.
- Never reference or tell the user to `npm install` a pre-existing "composable voice SDK" package as if it already exists and is published — as of this skill's writing no maintained, publicly installable package covers this pattern (only two narrow one-off repo PRs do; see the parent idea's Gap). This skill drafts original integration code directly against the raw provider WebSocket APIs, not an install of a third-party wrapper, unless the user explicitly states they already have such a package in their own dependencies.
- Never silently default the provider or mode when the user did state one — honor stated inputs over the stated defaults every time.
- Always include all three standing risk flags (permissions, autoplay, cost) even when nothing in the pasted code looks at risk — these are environment-level failure modes, not code-level ones, so static analysis of the pasted snippet can't rule them out.
- Never present the drafted diff as tested or production-ready — it is a scaffold for the user's own review and testing, say so explicitly in the output.
