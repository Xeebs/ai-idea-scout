# Voice-in-Composer Integration Scaffolder

A paste-into-any-AI-chat-tool prompt that drafts the actual code diff for adding a mic button to a chat UI you already have — voice input/output inline in the same text composer and message thread, not a separate standalone voice app.

## When to use this

You have a working text-first chat UI — a support widget, an internal tool, a consumer AI chat app, anything with a text box, a send button, and a message list — and you want users to be able to talk instead of type, with the response read back and the voice turn showing up as a normal message in the same thread. If you don't have an existing chat UI yet and want to build a voice app from scratch, this isn't the right prompt; it specifically drafts an *addition* to something that already exists.

## Data source

**Connected** — this prompt writes integration code targeting the Gemini Multimodal Live API (`BidiGenerateContent` WebSocket), a mature, documented realtime provider, with OpenAI's Realtime API as an alternate target. It does not call either API itself while drafting — it produces code that will call one of them once you deploy it. You are not expected to paste any transcript or API response; you're expected to paste your own composer code (see below).

## What to hand over before using this prompt

Gather these six things. The more of #1 you provide verbatim, the less generic the output will be:

1. **Your actual composer component source**, pasted verbatim — the text input/textarea, the send handler function, and the piece of state or store that holds the message list. A prose description works as a fallback but produces a more generic, placeholder-heavy result.
2. **Frontend framework** — React, Vue, or vanilla JS/TS.
3. **Backend runtime for the relay** — Node/Express, Next.js API routes, or "I don't have a backend yet."
4. **Target provider** — Gemini Multimodal Live or OpenAI Realtime. If you're not sure, say so; the default is Gemini Multimodal Live.
5. **Interaction mode** — push-to-talk (hold a button to speak) or continuous open-mic. If unsure, the default is push-to-talk (cheaper, fewer false triggers).
6. **How your existing text API calls authenticate** — e.g. "session cookie," "JWT in an Authorization header" — so the new voice relay reuses that instead of inventing a new login scheme.

## The prompt

Paste this into any AI chat tool, filling in the bracketed sections with your own answers to the six items above:

```
You are drafting an integration diff to add realtime voice input/output to
an existing text-first chat composer, inline in the same input and message
thread — not a new standalone voice screen.

Here is my setup:
1. My composer component source (pasted verbatim below), or a description
   if I don't have code handy:
   [PASTE YOUR COMPOSER CODE OR DESCRIBE IT HERE]
2. Frontend framework: [React / Vue / vanilla JS/TS]
3. Backend runtime for a relay server: [Node/Express / Next.js API routes /
   "I don't have a backend yet"]
4. Target realtime provider: [Gemini Multimodal Live / OpenAI Realtime /
   "not sure, pick one"]
5. Interaction mode: [push-to-talk / continuous open-mic / "not sure"]
6. How my existing text API calls authenticate: [session cookie / JWT /
   other / describe it]

Do the following:

1. State your assumptions up front — which provider and mode you're using,
   and anything you defaulted because I left it unstated (default to
   Gemini Multimodal Live and push-to-talk if I didn't specify).

2. Parse my pasted composer code to find: the input element, the send
   handler, and the message-list state update call. If I didn't paste real
   code, use explicit [PLACEHOLDER] markers instead of invented function
   names that won't actually match my file, and say so.

3. Draft a FRONTEND diff: a mic button next to my existing send button,
   wired to a voice-session hook/class that captures mic audio via
   getUserMedia, encodes/streams it to MY OWN backend relay over
   WebSocket (never directly to the provider — the API key must never
   reach browser code), receives audio back for gapless playback via the
   Web Audio API, and appends the transcript into the SAME message-list
   state update my existing text send handler already uses — so a voice
   turn looks like a normal chat message, not a separate mode.

4. Draft a BACKEND relay stub sized to my stated backend runtime: a
   WebSocket endpoint that authenticates the inbound browser connection
   using the auth pattern I described in #6, opens an outbound WebSocket
   to the chosen provider using a server-side-only API key from an
   environment variable, and pipes frames both directions.

5. Write one short paragraph on the auth handshake: confirm the browser
   never holds a provider API key, the relay holds it server-side only,
   and the browser-to-relay leg reuses my existing auth scheme.

6. Always include these three risk flags, regardless of what my code
   looks like: (a) mic permission prompts differ by browser, Safari is
   stricter; (b) browser autoplay policy can block audio playback until a
   user gesture happens; (c) continuous open-mic mode has real per-minute
   cost — confirm against the provider's pricing before shipping.

7. List manual follow-up steps: packages to install, environment
   variables to set, and an explicit note that this diff is a drafted
   starting point for my own review and testing, not verified working
   code.

8. Do not tell me to install some pre-existing "voice chat composer SDK"
   package as if one already exists and is published — as of now no
   maintained public package covers this pattern, only a couple of
   one-off repo PRs. Write the integration directly against the raw
   provider WebSocket API instead, unless I've told you I already have
   such a package in my own dependencies.

Output as:
- Assumptions
- Frontend diff (code blocks per file)
- Backend relay stub (one complete new-file code block)
- Auth handshake (short paragraph, no code)
- Risk flags (the fixed three, plus anything specific to my code)
- Manual follow-up checklist
```

## What you get back

A single markdown deliverable with six labeled sections — Assumptions, Frontend diff, Backend relay stub, Auth handshake note, Risk flags, and a manual follow-up checklist — that you can drop straight into your own pull request as a starting point. It is a scaffold, not tested code: you still need to install the right packages, set your environment variables, and verify it against your actual provider account and browser targets before shipping.

## Guardrails this prompt enforces

- No invented function/variable names standing in for your real code — placeholders instead, if you didn't paste code.
- No provider API key ever appears in frontend code — it stays server-side in the relay.
- No pretense that a ready-made "voice-in-composer SDK" package exists to `npm install` — it doesn't yet; this drafts original code against the provider's own WebSocket API.
- Your stated provider and interaction mode are always honored over the defaults.
- The three standing risk flags (permissions, autoplay, cost) appear every time, because they're environment-level risks a code snippet alone can't rule out.
- The output is always labeled as an unverified scaffold for your own review, never presented as tested or production-ready.
