# Voice-Native Core Architecture Audit

A paste-this-into-any-AI-chat-tool prompt that reviews your voice agent's existing code/design for the "bolted-on voice" anti-pattern — where voice is added as a TTS adapter on top of a text-first reasoning core instead of being a first-class part of the reasoning loop from the start — and gives you a prioritized migration plan.

## When to use this

You're building or maintaining a voice agent (support line, appointment booking, in-car assistant, voice-dictation copilot — anything on LiveKit, Pipecat, Vapi, Twilio Media Streams, or a custom stack) and it feels like the agent "thinks before it speaks" in a way that produces an awkward pause or clumsy interruption handling. You want a same-sitting design review — is this a quick fix or a from-scratch rebuild? — before you commit a sprint or more to redesigning it.

This is **not** for measuring actual latency numbers. If you have call recordings or OpenTelemetry traces and want real timing data, use a latency-measurement tool instead — this is a structural review of how your pipeline is *built*, not a benchmark of how it *performs*. It's also a one-time review, not a monitor: run it again by hand after you've made changes if you want a fresh read.

## Data source

**Manual.** You paste a description of your pipeline and/or the actual code — the function that calls your LLM, the function/call that triggers text-to-speech, and whatever tracks "whose turn it is" (listening/speaking/interrupted). Nothing is read automatically from any API, repo, or connector — this works entirely from what you paste into the chat.

## What to hand over

Before asking for the audit, give the assistant (or answer when it asks):

1. **Reasoning call shape** — does your code call the LLM for one full completion before anything happens with the text, or does it stream tokens? If it streams, what actually consumes the stream — just a UI display, or does any logic act on partial text before the full response is done?
2. **TTS trigger point** — what decides when speech synthesis starts? Is it literally `synthesize(full_response_text)` called after the LLM finishes, or is TTS fed text incrementally as it's generated?
3. **Turn-state representation** — is "whose turn it is" an explicit named state (an enum or state machine: listening / thinking / committing / speaking / interrupted) that multiple parts of your code consult and transition deliberately, or is it a loose boolean (`is_speaking = True`) checked and set in a few scattered places?
4. **Barge-in handling** — when the user talks over the agent, what happens? Does the reasoning loop get told about it and have defined behavior for what to do next (resume, abandon, re-ground), or does interrupting just cut the audio output with no effect on what the model "thinks" happened?
5. **Transport/framework** — LiveKit, Pipecat, Vapi, Twilio + custom, or fully custom. This matters because the audit will never tell you to rip out working audio/transport plumbing — only the reasoning-to-speech boundary and turn-state ownership are in scope.

If you're missing detail on more than one of these, the assistant should ask you directly for it rather than guess — a review built on a guess about your own code is worse than no review, so don't let it proceed on assumptions.

## The procedure (what the assistant should do with your answers)

1. Gather all five inputs above.
2. Score four **architecture checkpoints**, each as **BOLTED-ON**, **PARTIAL**, **NATIVE**, or **UNCLEAR** (if your input doesn't actually address it) — every score must cite something specific you said or pasted, never an inference from the framework name alone:
   - **A — Reasoning-to-speech handoff**: BOLTED-ON if TTS only starts after the full response text exists. PARTIAL if text streams to TTS but the reasoning loop has no concept of "safe to commit" (it just forwards whatever appears). NATIVE if the reasoning loop itself decides when a partial chunk is complete enough to speak before the rest is generated.
   - **B — Turn-state representation**: BOLTED-ON if it's an untyped flag set/read in multiple places. PARTIAL if a named state exists but only the audio layer reads it. NATIVE if the reasoning loop itself consults and transitions the state as part of its own logic.
   - **C — Commit-confidence gating**: BOLTED-ON if there's no concept of "is this chunk safe to speak" at all. PARTIAL if there's sentence-boundary chunking but it's a formatting heuristic, not a confidence decision. NATIVE if the model/wrapper explicitly gates on confidence the chunk won't need retraction.
   - **D — Barge-in/interruption handling**: BOLTED-ON if interrupting just mutes audio with no effect on reasoning state. PARTIAL if the state machine notices the interruption but the reasoning loop doesn't act on it. NATIVE if the reasoning loop receives the interruption as a state transition with defined recovery behavior.
3. For each checkpoint, assign a migration tier: **Keep as-is** (only if NATIVE), **Adapt** (fixable in place without a rewrite), or **Rebuild** (structurally incompatible with the current approach, e.g. a fully synchronous full-completion-then-synthesize call).
4. Separate explicitly what your transport/framework already handles well and should be **kept untouched** from what belongs to the reasoning-core layer and needs to **change**. Working audio/transport plumbing (LiveKit, Pipecat, Vapi, custom WebRTC) is never something this review tells you to discard.
5. Sequence the fixes: order BOLTED-ON/PARTIAL checkpoints by expected naturalness impact first, then by migration tier (Adapt before Rebuild), with ties going to whichever checkpoint structurally blocks the others (usually the turn-state machine, B, has to exist before interruption recovery, D, can be built on it).
6. Produce the report using the exact structure below.

## Output format

```
# Voice-Native Core Audit — <your pipeline name>

**Transport/framework**: <LiveKit | Pipecat | Vapi | custom | other>
**Inputs assessed from**: <code pasted | prose description | both>

## Checkpoint Scorecard
| Checkpoint | Verdict | Evidence | Migration tier |
|---|---|---|---|
| A — Reasoning-to-speech handoff | ... | ... | ... |
| B — Turn-state representation | ... | ... | ... |
| C — Commit-confidence gating | ... | ... | ... |
| D — Barge-in/interruption handling | ... | ... | ... |

## What to keep
<transport/plumbing pieces needing no change, named specifically>

## What to change, in order
1. <highest-priority fix, with the concrete code-shape change>
2. <next>
3. <next>

## Expected effect (qualitative, not measured)
<1-2 sentences framed as a hypothesis — never a specific millisecond claim unless you supplied real measured numbers>

## Validate before and after
<concrete things to measure once changes ship, e.g. "time from end of user utterance to first audio frame, on a 10-call sample">

## Notes / assumptions
<anything assumed due to missing input>
```

## Rules the assistant must follow

- Never score a checkpoint without a specific citation from what you actually said or pasted — if your input doesn't cover a checkpoint, it should say UNCLEAR and ask, not infer from your framework choice alone.
- Never recommend discarding a working transport/audio layer — this review only ever touches the reasoning-to-speech boundary and turn-state ownership.
- Never invent a specific latency number ("this will save you 150ms") unless you supplied your own measured numbers — expected effects should be framed as hypotheses to validate, not facts.
- Never produce a full scorecard when more than one of the five required inputs is missing — the assistant should stop and ask for the specific missing detail instead of guessing.
- This review doesn't hand you a working chunked-commit implementation — it's a design audit and migration plan for *your* code. If you want the actual reference library/architecture instead of a review of what you have, say so and ask for that separately.
