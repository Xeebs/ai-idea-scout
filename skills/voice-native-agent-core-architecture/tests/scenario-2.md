# Scenario 2 — Partially-streaming Pipecat bot with missing input (expect a clarifying question first)

## Input (what the user pastes)

> We're on Pipecat with a streaming LLM — tokens come in and we forward them to TTS sentence-by-sentence using Pipecat's sentence aggregator, so synthesis starts well before the full response is done. We also have an explicit `TurnState` enum (LISTENING, AGENT_SPEAKING, USER_INTERRUPTING) that our transport layer updates. Can you audit our architecture?

(Note: the user did not say anything about (a) whether the reasoning loop itself consults `TurnState` or only the transport layer does, and (b) what happens to the reasoning loop when `USER_INTERRUPTING` fires — no mention of recovery behavior at all.)

## Expected output characteristics (pass/fail checklist)

- [ ] The assistant does **not** immediately produce a full four-checkpoint scorecard. Two required inputs are missing/too vague to classify: (3) whether the reasoning loop itself reads `TurnState` (vs. only the transport layer) and (4) what the reasoning loop does on interruption (recovery behavior, if any). Per the guardrail ("never produce a full scorecard when more than one of the five required inputs is missing or too vague"), the assistant should stop and ask for these two specifically by name.
- [ ] The clarifying question names the exact gaps (does the reasoning loop consult `TurnState`? what happens to the reasoning loop's internal state on `USER_INTERRUPTING`?) rather than asking a generic "tell me more about your architecture."
- [ ] The assistant does NOT guess or assume Checkpoint B is NATIVE just because a named enum (`TurnState`) exists — correctly treats "an enum exists" as insufficient on its own to score B, since PARTIAL vs NATIVE hinges on *who reads it*, which wasn't stated.
- [ ] The assistant does NOT guess or assume Checkpoint D's verdict from the enum's existence alone.
- [ ] If the assistant provisionally comments on Checkpoint A or C (which the user *did* give enough detail on — sentence-by-sentence streaming to TTS as text generates, no mention of confidence gating), it's acceptable, but the response as a whole must not present a complete scorecard with all four rows filled in before the missing detail is obtained.

## Follow-up turn (after user clarifies)

> Only the transport layer reads `TurnState` — the reasoning loop just generates tokens and doesn't know about turns at all. On interruption we currently just stop forwarding tokens to TTS; the LLM call itself isn't cancelled or told anything, so if you un-mute it it'll finish rambling into a buffer that gets discarded.

- [ ] With this added, Checkpoint A scores **PARTIAL** (text streams to TTS via sentence aggregation, but no commit-confidence concept — it's a formatting heuristic, matching the PARTIAL definition for A almost exactly).
- [ ] Checkpoint B scores **PARTIAL** (named state exists, but only the transport layer reads it — reasoning loop doesn't consult it), explicitly citing "only the transport layer reads TurnState."
- [ ] Checkpoint C scores **BOLTED-ON** (sentence aggregation is a formatting heuristic, not a confidence gate — no such concept was described).
- [ ] Checkpoint D scores **BOLTED-ON** (LLM call isn't cancelled/informed, continues generating into a discarded buffer — no recovery logic, reasoning loop doesn't know interruption happened).
- [ ] "What to keep" explicitly credits Pipecat's sentence aggregator and streaming transport as working infrastructure, not something to rip out.
- [ ] Migration sequencing puts making the reasoning loop state-machine-aware (B) and cancelling/informing the LLM call on interruption (D) ahead of or alongside adding commit-confidence gating (C), with a stated dependency reason.

**Fail conditions**: scoring any checkpoint from the first message alone without asking for the missing detail; treating "an enum exists" as sufficient evidence for NATIVE; recommending Pipecat's transport/aggregator be replaced; inventing a specific latency figure anywhere.
