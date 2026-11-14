---
name: shared-voice-loop-daemon-protocol
description: Drafts a voice-intent registration manifest (trigger phrases, callback wiring, collision disambiguation) for an app joining a shared local voice-loop daemon or any intent-matching voice engine. Use when a developer wants to add voice control to an existing app's commands/endpoints without writing their own wake-word/STT stack.
---

# Voice-Intent Manifest Drafter

## When to use this
A developer has an app with an existing command surface (CLI flags, REST endpoints, or internal functions) and wants to make it voice-triggerable — either to register it with a shared local voice-loop daemon (one mic, many apps, each app opts in with a manifest instead of running its own STT stack) or to feed a manifest into an existing intent-matching voice engine (e.g. Rhasspy, Home Assistant Assist, Mycroft/OpenVoiceOS, or a custom wake-word router). The trigger moment is "I want X app to respond to voice commands, and I don't want to design the trigger phrases, callback wiring, or collision handling by hand."

This is a one-shot drafting aid, not the daemon itself. It produces a manifest file; it does not run a microphone, do speech recognition, or dispatch anything live.

## Inputs
**Data source**: Manual — the user pastes (a) a description of their app's existing command surface (CLI `--help` output, a list of function signatures, REST endpoint paths/methods, or plain-English feature descriptions), and optionally (b) the manifest JSON of other apps already registered with the same daemon/engine, so collisions can be checked. Nothing is read from a live connector — this skill never queries a running daemon, an app's actual codebase, or any API; everything it reasons over is text the user hands it in the conversation.

Required minimum: at least one concrete action description per intent the user wants voice-triggerable (a name or description of what it does). Helpful but optional: how the app expects to be invoked (an HTTP endpoint it exposes, a CLI command it runs, or a local socket it listens on) and any other apps' manifests to check against.

## Procedure
1. **Extract discrete actions.** Read the pasted command surface and split it into one candidate intent per distinguishable action (e.g. "play", "pause", "skip track" are three intents, not one "music control" intent) — a daemon or intent engine routes per-utterance to exactly one callback, so intents must be atomic enough to map to one callback each.
2. **Name each intent.** Use a namespaced snake_case or dot-separated name: `<appname>.<action>` (e.g. `notes.create_note`, `lights.toggle`). This namespace is what prevents two apps from silently defining an identical bare intent name even when their trigger phrases differ.
3. **Determine the callback.** Infer callback `type` from what the user described:
   - REST endpoint mentioned → `type: "http"`, `target: "<method> <path>"` (use the user's exact path; never invent one).
   - CLI command/flag mentioned → `type: "exec"`, `target: "<exact command string the user gave>"`.
   - Socket/IPC mentioned → `type: "socket"`, `target: "<socket path or name given>"`.
   - Nothing specified → `type: "unknown"`, `target: "TODO: <one-line description of what this callback needs to do>"` — never fabricate an endpoint, flag, or path that wasn't given.
4. **Draft trigger phrases per intent.** Generate 3–5 phrasings per intent that:
   - Use natural spoken English (not CLI-flag syntax or REST verbs).
   - Vary word order/synonyms enough to tolerate STT mangling (e.g. "skip this track", "next song", "play the next one").
   - Avoid single-word triggers (STT false-positive risk) and avoid phrases that are substrings of a far more common phrase already in the daemon's established vocabulary if the user mentioned one.
   - If the underlying action takes a parameter (a body field, a CLI argument, a free-text value — e.g. a brightness level, a note title, a search query), phrase triggers with an explicit slot (e.g. "set brightness to {level} percent", "search notes for {query}") and add a `"slots": ["<field name>"]` array to that intent in the manifest. Never silently drop a required parameter from the callback — if the manifest schema has no field for it, say so explicitly in Open Questions rather than omitting it.
5. **Flag destructive or consequential intents.** Any intent whose action deletes, sends, pays, shuts down, or otherwise can't be trivially undone gets flagged in the output with a recommendation: either a longer/harder-to-mishear trigger phrase, or an explicit "confirm" sub-step, before the skill finalizes it — never silently treat a destructive action the same as a benign one.
6. **Check collisions, if other manifests were provided.** Compare this app's trigger phrases against every intent in the pasted manifests. For any phrase that is identical or a likely STT-confusable near-match (same core verb + object, synonym swap) to another app's trigger phrase, do not pick a winner — list the collision and propose one disambiguating rewrite per side (e.g. add the app's name as a prefix: "notes, create a note" vs. "lights, create a note" — unlikely, but illustrates the pattern) for the developer to choose between.
7. **Assemble the manifest.** Emit valid JSON matching the schema in Output format below. Every intent must have `name`, `trigger_phrases` (array), and `callback` (object with `type`/`target`); flagged/destructive intents carry an extra `"confirm_required": true` field.
8. **List open questions.** Anything the skill had to mark `TODO`/`unknown`, or any unresolved collision, goes in a plain bullet list after the manifest so the developer knows exactly what's left to decide — never bury a gap silently inside the JSON.

## Output format
A single markdown reply with three parts, in this order:

1. A fenced ```json``` block: `{"app": "<app name>", "intents": [ {"name": ..., "trigger_phrases": [...], "callback": {"type": ..., "target": ...}, "slots": [...]|omitted, "confirm_required": true|omitted} ... ]}`
2. A "Collision report" section — a markdown table of `Phrase | This app's intent | Conflicting app's intent | Suggested disambiguation`, or the line "No collisions found against the manifests provided" if none were supplied or none overlap.
3. An "Open questions" bulleted list — every `TODO`/`unknown` callback target, every unresolved collision, and every destructive intent flagged in step 5, each with the specific decision the developer needs to make.

## Guardrails
- Never invent a callback endpoint, CLI flag, or socket path the user didn't state — use the `TODO`/`unknown` placeholder and surface it in Open Questions instead of guessing.
- Never auto-resolve a trigger-phrase collision by picking a "winner" — always present both options and let the human decide.
- Never skip the destructive-action flag for delete/send/pay/shutdown-shaped actions, even if the user's description sounds casual about it.
- Never claim this manifest is "registered" or "active" — this skill only drafts a file; it has no connection to a running daemon or voice engine.
- Never fabricate functionality the app doesn't have; if the user's description is ambiguous about what an action actually does, ask one clarifying question rather than guessing and shipping a wrong trigger phrase.
