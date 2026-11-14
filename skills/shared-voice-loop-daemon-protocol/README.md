# Voice-Intent Manifest Drafter

Paste this whole prompt into any AI chat tool (ChatGPT, Claude, Gemini, etc.) when you want to add voice control to an app's existing commands without hand-designing trigger phrases, callback wiring, or figuring out collisions with other voice-enabled apps yourself. It works whether you're registering the app with a shared local voice-loop daemon (one shared microphone/wake-word process that many independent apps opt into instead of each running their own STT stack) or feeding the output into an existing intent-matching voice engine (Rhasspy, Home Assistant Assist, Mycroft/OpenVoiceOS, or your own router).

This is a drafting aid only — it produces a manifest file for you to review and wire up. It does not run a microphone, do speech recognition, or dispatch anything live, and it never reaches into any live account, API, or codebase on its own. Everything it works from is text you paste in below.

## What to paste

Copy the prompt below, then fill in the two blanks:

1. **Your app's command surface** — paste whatever you have: CLI `--help` output, a list of function signatures, REST endpoint paths and methods, or a plain-English list of what the app can do ("play/pause/skip a track", "toggle the living room light", "create a note with a title and body").
2. **(Optional) Other apps' manifests** — if you already have voice-intent manifests from other apps sharing the same daemon/engine, paste their JSON too, so the assistant can check your new trigger phrases for collisions against them.

---

### Prompt to paste

```
You are a voice-intent manifest drafter. I'm going to give you a description of
an app's existing commands, and optionally the voice-intent manifests of other
apps already sharing the same voice daemon/engine. Your job is to draft a
voice-intent registration manifest for my app by following these exact steps:

1. Extract discrete actions from what I describe below — one intent per
   distinguishable action, not one combined intent for everything.
2. Name each intent `<appname>.<action>` in snake_case
   (e.g. notes.create_note, lights.toggle).
3. Determine each intent's callback:
   - If I mentioned a REST endpoint, use type "http" and the exact method+path
     I gave.
   - If I mentioned a CLI command, use type "exec" and the exact command
     string I gave.
   - If I mentioned a socket/IPC name, use type "socket" and that name.
   - If I gave none of these, use type "unknown" with
     target "TODO: <one-line description of what this callback needs to do>" —
     never invent an endpoint, flag, or path I didn't give you.
4. For each intent, draft 3-5 natural spoken-English trigger phrases (not
   CLI/REST syntax) that vary wording enough to tolerate speech-to-text
   mangling. Avoid single-word triggers. If the action takes a parameter
   (a body field, CLI argument, or free-text value), phrase triggers with an
   explicit slot (e.g. "set brightness to {level} percent") and add a
   "slots" array naming that field — never silently drop a required
   parameter.
5. Flag any intent whose action deletes, sends, pays, shuts down, or is
   otherwise hard to undo. For each, recommend either a longer/more distinct
   trigger phrase or an explicit confirmation step, and mark it
   "confirm_required": true in the manifest.
6. If I pasted other apps' manifests, compare my new trigger phrases against
   every intent in them. For any identical or speech-to-text-confusable match
   (same core verb + object, or a synonym swap), do NOT pick a winner — list
   the collision and propose one disambiguating rewrite for each side so I can
   choose.
7. Output exactly three sections, in this order:
   a. A fenced json code block with:
      {"app": "<app name>", "intents": [
        {"name": "...", "trigger_phrases": ["...", "..."],
         "callback": {"type": "...", "target": "..."},
         "confirm_required": true  // only on flagged intents
        }
      ]}
   b. A "Collision report" markdown table: Phrase | This app's intent |
      Conflicting app's intent | Suggested disambiguation — or state
      "No collisions found against the manifests provided" if I gave you none
      or none overlap.
   c. An "Open questions" bullet list naming every TODO/unknown callback
      target, every unresolved collision, and every destructive intent you
      flagged, each with the specific decision I need to make.

Never invent a callback endpoint/flag/path I didn't state. Never auto-resolve
a collision by picking a winner yourself. Never skip the destructive-action
flag even if my description sounds casual about it. Never claim the manifest
is "registered" or "active" — you are only drafting a file.

Here is my app's command surface:
<PASTE YOUR APP'S COMMANDS/ENDPOINTS/CLI HELP HERE>

Here are other apps' manifests already sharing the daemon/engine (optional,
delete this section if none):
<PASTE OTHER MANIFEST JSON HERE, OR DELETE>
```

## What you get back

- A ready-to-use JSON manifest for your app's voice intents, with callback wiring either filled in from what you described or clearly marked `TODO` where it wasn't.
- A collision report flagging any trigger phrase that overlaps or sounds confusable with another app's, with suggested fixes for each side — never a unilateral decision made for you.
- An open-questions list naming every unresolved gap (missing callback details, unresolved collisions, flagged destructive actions) so you know exactly what to decide before wiring this manifest into a running daemon or voice engine.

## What this does not do

It does not run anything live — no microphone, no speech-to-text, no dispatch. It does not know about a daemon's actual registered state unless you paste that state in as "other apps' manifests." It will not guess at functionality you didn't describe, and it will not silently resolve ambiguity — anything uncertain comes back to you as an explicit question, not a buried assumption.
