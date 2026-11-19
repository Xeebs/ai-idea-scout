---
name: voice-native-agent-core-architecture
description: Audits an existing voice-agent pipeline description/code for the "bolted-on voice" anti-pattern (full-text-before-TTS, turn-state as a boolean flag, no commit-confidence gating, exception-style barge-in) and drafts a prioritized migration plan toward a chunked-commit, state-machine-native core. Use when a team is deciding whether to invest engineering time in redesigning their voice agent's reasoning-to-speech boundary.
---

# Voice-Native Core Architecture Audit

## When to use this
A team has a working voice agent — built on LiveKit, Pipecat, Vapi, a custom stack, or any combination — and suspects their agent "thinks before it speaks" in a way that produces a perceptible pause or clunky turn-taking, but they aren't sure whether the fix is a quick adjustment or a from-scratch rebuild of their reasoning loop. They want a same-sitting design review before committing a sprint (or more) to a migration.

This is NOT for teams who just want raw latency numbers — if they already have call recordings or OTel traces, point them to a latency-measurement tool instead; this skill works from a description/code of the pipeline's *structure*, not from timing data. It is also a one-time design review, not a running audit — rerun it manually after a migration to re-check, it doesn't monitor anything.

## Inputs
**Data source**: Manual — the user pastes a description of their pipeline, and/or actual code (the function or module that calls the reasoning model, the TTS invocation, and whatever tracks "is the agent currently listening/speaking/interrupted"). Nothing is read from a connector or API; this is a static design review of what the user hands over, not a running audit of their live system.

Required, either volunteered or elicited by direct questions before scoring:
1. **Reasoning call shape** — does the code call the LLM for a full completion before anything happens with the text, or does it stream tokens? If it streams, what consumes the stream — only a UI, or does anything act on partial text before the full response finishes?
2. **TTS trigger point** — what piece of code decides when synthesis starts? Is it `synthesize(full_response_text)` after the LLM call returns, or is TTS fed incrementally as text becomes available?
3. **Turn-state representation** — is "whose turn it is" tracked as an explicit named state (e.g., an enum/state machine: listening, thinking, committing, speaking, interrupted) that other parts of the code consult and transition explicitly, or is it an ad hoc boolean/variable (`is_speaking = True`) set and checked in scattered places?
4. **Barge-in/interruption handling** — when the user talks over the agent, what happens? Is it a first-class transition the reasoning loop is aware of (e.g., the state machine tells the reasoning loop to stop and the loop has a defined "what was I mid-saying" recovery), or is it handled as an exception/edge case bolted on afterward (e.g., just cutting audio output with no effect on the reasoning loop's internal state)?
5. **Transport/framework in use** — LiveKit, Pipecat, Vapi, Twilio Media Streams + custom, or fully custom. (This determines what in the "keep as-is" column below is realistic to preserve.)

If more than one of the five is missing or too vague to classify (e.g., "we use streaming" without saying what consumes the stream), ask for it directly before producing the audit — a verdict built on a guess about the user's own code is worse than no verdict.

## Procedure
1. Collect all five inputs above from the user's description/code.
2. Classify each of the four **architecture checkpoints** below as **BOLTED-ON**, **PARTIAL**, or **NATIVE**, citing the specific line/behavior from what the user gave you as evidence for each call — never classify from inference alone if the user's text doesn't actually say or show it; if genuinely ambiguous, mark it **UNCLEAR** and say what additional detail would resolve it.
   - **Checkpoint A — Reasoning-to-speech handoff**: BOLTED-ON = TTS is invoked only after the full LLM response text exists. PARTIAL = text is streamed to TTS as it's generated, but the reasoning loop itself has no concept of "safe to commit" (it just forwards whatever text appears). NATIVE = the reasoning loop explicitly decides when a partial chunk is semantically complete and safe to speak before the rest is generated.
   - **Checkpoint B — Turn-state representation**: BOLTED-ON = a boolean or a small set of untyped flags, set/read in multiple unrelated places. PARTIAL = a named enum/state exists but only the audio/transport layer reads it (the reasoning loop doesn't consult it). NATIVE = the state machine is a dependency the reasoning loop itself queries and transitions as part of its own logic.
   - **Checkpoint C — Commit-confidence gating**: BOLTED-ON = no such concept exists; text is spoken as soon as it's available with no revision-risk check. PARTIAL = there's some chunking (e.g., sentence-boundary splitting) but it's a text-formatting heuristic, not a reasoning-confidence decision. NATIVE = the model (or a wrapper around it) explicitly gates commitment on confidence that the chunk won't need retraction.
   - **Checkpoint D — Barge-in/interruption handling**: BOLTED-ON = interruption just stops/mutes audio output with no effect on reasoning state (the model "doesn't know" it was cut off). PARTIAL = the state machine registers "interrupted" but the reasoning loop doesn't use that to decide what to do next (no defined recovery). NATIVE = the reasoning loop receives the interruption as a state transition and has defined behavior for resuming, abandoning, or re-grounding after it.
3. For each checkpoint, assign a **migration tier**:
   - **Keep as-is** — only applies if NATIVE.
   - **Adapt** — the existing code/transport can be modified in place without a rewrite (e.g., adding a confidence check function, converting a boolean to an enum consulted by the reasoning loop).
   - **Rebuild** — the current approach is structurally incompatible (e.g., a fully synchronous full-completion-then-synthesize call that would need the reasoning call itself restructured to stream and commit incrementally).
4. Explicitly separate what the transport/framework (LiveKit, Pipecat, Vapi, etc., per input 5) already provides and should be **kept** from what belongs to the reasoning-core layer and needs to **change**. Never recommend discarding working transport/audio plumbing — the migration is about the reasoning-to-speech boundary and turn-state ownership, not the audio stack.
5. Sequence the migration: order the checkpoints that scored BOLTED-ON or PARTIAL by (a) how much perceptible naturalness/latency improvement fixing them would plausibly produce, using the user's own stated pain point if given, and (b) ascending migration tier (Adapt before Rebuild) — ties go to whichever checkpoint blocks the others structurally (Checkpoint B's state machine typically has to exist before Checkpoint D's recovery logic can be built on top of it).
6. Produce the report in the exact format below. If the user gave fewer than all five inputs and you proceeded anyway because only one was missing, state in the report which one was assumed and flag it as lower-confidence.

## Output format
```
# Voice-Native Core Audit — <team/pipeline name, or "your pipeline" if unnamed>

**Transport/framework**: <LiveKit | Pipecat | Vapi | custom | other, as given>
**Inputs assessed from**: <code pasted | prose description | both>

## Checkpoint Scorecard
| Checkpoint | Verdict | Evidence | Migration tier |
|---|---|---|---|
| A — Reasoning-to-speech handoff | BOLTED-ON / PARTIAL / NATIVE / UNCLEAR | <quote or paraphrase from input> | Keep as-is / Adapt / Rebuild |
| B — Turn-state representation | ... | ... | ... |
| C — Commit-confidence gating | ... | ... | ... |
| D — Barge-in/interruption handling | ... | ... | ... |

## What to keep
<the transport/audio-plumbing pieces, named specifically, that need no change>

## What to change, in order
1. <highest-priority checkpoint fix, with the concrete code-shape change — not just "add a state machine" but what it would consult and when>
2. <next>
3. <next, as many as apply>

## Expected effect (qualitative, not measured)
<1-2 sentences on what should improve if this plan is followed — framed as a hypothesis to validate, e.g. "should reduce the perceptible pause before the agent starts speaking," never a specific millisecond claim unless the user supplied real numbers>

## Validate before and after
<1-2 concrete things to measure once the migration ships — e.g. "time from end of user utterance to first audio frame, on a 10-call sample" — pointing out this audit itself produces no numbers>

## Notes / assumptions
<anything assumed due to missing input, and what would sharpen the audit next time>
```

## Guardrails
- Never assign a checkpoint verdict without a specific evidence citation from what the user actually gave you — if nothing in their input addresses a checkpoint, mark it UNCLEAR and ask, don't infer from the framework name alone (e.g., "uses LiveKit" is not evidence of any checkpoint's verdict; teams misuse LiveKit's building blocks in bolted-on ways constantly).
- Never recommend ripping out a working transport/audio layer (LiveKit, Pipecat, Vapi, or custom WebRTC plumbing) — the anti-pattern this skill targets is in the reasoning-to-speech boundary and turn-state ownership, not the audio transport; always produce a "what to keep" list, never a blanket rebuild recommendation.
- Never invent or imply a specific latency number (e.g., "this will save you 150ms") unless the user supplied their own measured numbers — this is a structural design review, not a benchmark; frame expected effects qualitatively and push the user toward their own before/after measurement.
- Never produce a full scorecard when more than one of the five required inputs is missing or too vague to classify — stop and ask for the specific missing detail by name instead of guessing to keep the interaction moving.
- Never present this as a substitute for the actual reference architecture/library — if the user wants the working chunked-commit implementation rather than a review of their own code, say so plainly and point them to building or adopting a reference core, since this skill only audits and plans, it doesn't ship code.
