---
name: voice-agent-speculative-tool-calling-middleware
description: Reviews a voice agent's tool manifest plus sample transcripts and produces a per-tool speculate/wait classification, confidence threshold, and cancellation policy for speculative tool calling. Use when a team is about to add speculative/eager tool execution to cut voice-agent "thinking" latency and needs the design judgment (which tools are safe to fire early) before writing any middleware code.
---

# Speculation Planner: Voice-Agent Speculative Tool-Calling Policy

## When to use this
Someone is building or operating a voice agent (phone/IVR bot, voice assistant, real-time call-center agent) on a framework like Pipecat, LiveKit Agents, or Vocode, is hitting a multi-second "thinking" silence while the LLM decides which function to call, and wants to start firing likely tool calls on the *partial* transcript before the caller finishes speaking — but needs to decide, tool by tool, which calls are safe to speculate on before wiring up the actual middleware. This is a one-shot design/review task, not the runtime library itself: run it once per tool manifest (and again whenever tools change), not per call.

## Inputs
**Data source**: Manual — the user pastes two artifacts directly into the chat (no live connector reads them automatically): (1) the tool/function manifest — every tool name, a one-line description, its side-effect type, and whether it's idempotent; (2) a set of example multi-turn conversation transcripts representative of real caller traffic for this agent.

Required:
1. **Tool manifest** — for each tool: name, short description, side-effect class if known (read-only vs. write vs. payment/irreversible), idempotency (same call twice = same safe outcome, yes/no), and approximate backend cost/latency if known (e.g., "cheap DB lookup" vs. "calls a paid third-party API").
2. **Example transcripts** — at least 10 real or realistically-reconstructed multi-turn conversations covering the agent's main intents, ideally including a few where the caller starts one way and pivots ("actually, never mind, I meant—"). Full transcripts are fine; partial-transcript timing is a bonus, not required.

Optional:
3. Current median time-to-tool-call-decision (the latency being solved for) and an acceptable wasted-speculative-call-rate threshold (default to <15% if not given, matching common practice).

If the manifest is missing side-effect class or idempotency for a tool, do not guess it — ask the user to classify that tool explicitly before scoring it.

## Procedure
1. **Hard-exclude pass.** For every tool, check for any of: moves money, cancels/modifies an irreversible commitment, sends an outbound message/notification to a third party, or touches compliance-sensitive data (e.g., writes to a medical/legal record). Any match → classify `NEVER_SPECULATE` immediately and skip the rest of the analysis for that tool. This pass overrides every signal below; no amount of transcript evidence promotes a tool out of `NEVER_SPECULATE`.
2. **Side-effect scoring** for the remaining tools: `READ_IDEMPOTENT` (safe lookup, repeatable), `READ_NON_IDEMPOTENT` (e.g., "get next queue position" — result can change between calls), `WRITE_REVERSIBLE` (can be undone cheaply, e.g., a draft save). Tools with no cheap, automatic undo path that aren't already excluded in step 1 get downgraded one tier of eligibility in step 4.
3. **Confusability scan.** For each remaining tool, scan the example transcripts for other tools whose triggering phrases overlap in the first ~60% of the utterance (e.g., "I want to check my..." could precede "order status" or "appointment time"). Tag each tool's confusability as LOW (distinguishable almost immediately), MEDIUM (distinguishable only after a key noun lands), or HIGH (frequently still ambiguous near the end of the utterance in the sample).
4. **Eligibility + threshold.** Combine side-effect tier and confusability into a verdict:
   - `READ_IDEMPOTENT` + LOW/MEDIUM confusability → `SPECULATE`, confidence threshold 0.55–0.65 (fire early).
   - `READ_IDEMPOTENT` + HIGH confusability, or `READ_NON_IDEMPOTENT` + LOW/MEDIUM → `SPECULATE_CONDITIONAL`, confidence threshold 0.75–0.85 (fire late, only once the classifier is quite sure).
   - `READ_NON_IDEMPOTENT` + HIGH confusability, or any `WRITE_REVERSIBLE` → `WAIT`, do not speculate; note the specific reason.
   - Anything already `NEVER_SPECULATE` from step 1 stays that way regardless of this scoring.
5. **Cancellation policy per speculated tool.** For `SPECULATE`/`SPECULATE_CONDITIONAL` tools, recommend: cache-and-discard (idempotent reads — just drop the cached result if the final transcript disagrees, no cleanup needed) or cache-with-timeout-abort (non-idempotent reads — issue a cancellation/abort call if the backend supports it, otherwise shorten the speculation window instead of speculating blind).
6. **Transcript-sample caveat.** If fewer than 10 transcripts were provided, or they don't cover all tools in the manifest, label every threshold in the output as PROVISIONAL and say explicitly which tools had zero or near-zero transcript coverage.
7. **Risk flag.** For every `SPECULATE`/`SPECULATE_CONDITIONAL` tool, note it must never be spoken aloud to the caller until the final transcript confirms the intent — this applies even to `READ_IDEMPOTENT` tools, because a correct-but-premature answer to the wrong question is still a trust failure.

## Output format
A markdown table, one row per tool:

```
| Tool | Side-effect class | Verdict | Confidence threshold | Cancellation policy | Rationale |
```

Followed by:
- A one-paragraph summary naming the tools cleared for speculation and the ones explicitly excluded and why.
- A **"Before you ship"** checklist: validate thresholds against a held-out transcript set, measure actual wasted-call rate against the stated threshold (default <15%), and confirm the runtime never surfaces a speculative result before confirmation.
- If step 6 triggered, a visible `PROVISIONAL — low transcript coverage` banner at the top of the table, naming which tools it affects.

## Guardrails
- Never mark a payment, cancellation/irreversible-commitment, outbound-notification, or compliance-sensitive-write tool as speculate-eligible — step 1's hard-exclude always wins, regardless of how clean the transcripts look for that tool.
- Never invent a side-effect class or idempotency value for a tool the user didn't specify — ask, don't assume safe.
- Never present this output as a validated, production-ready policy. It is a design recommendation to be measured against a real pilot; always include the "Before you ship" checklist.
- Never recommend speaking, logging-as-fact, or otherwise surfacing a speculative tool result to the end caller before the final transcript confirms intent, even for low-risk tools.
- If transcript coverage for a tool is zero, do not score that tool's confusability — label it `INSUFFICIENT DATA` and default it to `WAIT` rather than guessing a threshold.
