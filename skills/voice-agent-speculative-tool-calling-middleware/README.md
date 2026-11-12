# Speculation Planner: Voice-Agent Speculative Tool-Calling Policy

A self-contained prompt template. Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your tool manifest and sample transcripts, and it will act as a one-shot design reviewer for speculative tool calling in your voice agent.

## When to use this

You're building or operating a voice agent (phone bot, IVR, real-time call-center assistant) on a framework like Pipecat, LiveKit Agents, or Vocode, and callers experience a multi-second silence while the LLM decides which function to call. You want to start firing likely tool calls on the *partial* transcript — before the caller finishes speaking — to collapse that silence, but before writing any middleware you need to decide, tool by tool, which calls are actually safe to fire early. This prompt produces that design decision. It is a one-time (or occasional, when tools change) planning step, not the runtime code that executes speculative calls live.

## What to hand over

**Data source: manual.** You paste both of these directly into the chat — nothing here is read automatically from a live system.

1. **Your tool manifest.** For every tool/function your agent can call, give: name, one-line description, side-effect class (does it only read data, write reversible data, or do something irreversible like moving money or sending a message), and whether it's idempotent (calling it twice with the same input gives the same safe result). If you're not sure of a tool's side-effect class or idempotency, say so rather than guessing — the prompt will ask you to classify it rather than assume it's safe.
2. **At least 10 example conversation transcripts** from real or realistic calls, covering your agent's main intents. Include a few where the caller starts saying one thing and pivots ("actually, never mind, I meant—") — those are the cases that make or break a speculation policy.
3. *(Optional)* Your current median "thinking" latency and the wasted-speculative-call rate you're willing to tolerate (a common default is under 15%).

## The prompt

```
You are reviewing a voice agent's tools to decide which ones are safe to call
speculatively — i.e., fired early based on a partial transcript, before the
caller finishes speaking, to cut the "thinking" silence between utterance end
and tool execution.

I will give you:
1. A tool manifest (name, description, side-effect class, idempotency, and
   rough backend cost if known).
2. At least 10 example conversation transcripts.
3. (Optional) a target wasted-call-rate threshold — default to <15% if I
   don't give you one.

For EVERY tool, follow this exact procedure:

STEP 1 — Hard exclude. If the tool moves money, cancels/modifies an
irreversible commitment, sends an outbound message to a third party, or
writes to compliance-sensitive data, mark it NEVER_SPECULATE immediately and
skip the rest of the steps for that tool. No transcript evidence can override
this.

STEP 2 — Side-effect tier (for everything not already excluded):
READ_IDEMPOTENT (safe repeatable lookup), READ_NON_IDEMPOTENT (result can
change between calls, e.g. "queue position"), or WRITE_REVERSIBLE (write that
has a cheap, automatic undo path).

STEP 3 — Confusability scan. Using the transcripts, judge how early in a
typical utterance this tool becomes distinguishable from other tools with
similar trigger phrases. Rate LOW (clear almost immediately), MEDIUM (clear
once a key noun lands), or HIGH (often still ambiguous near the end of the
utterance).

STEP 4 — Verdict + confidence threshold, combining steps 2 and 3:
- READ_IDEMPOTENT + LOW/MEDIUM confusability -> SPECULATE, threshold 0.55-0.65.
- READ_IDEMPOTENT + HIGH confusability, or READ_NON_IDEMPOTENT + LOW/MEDIUM
  -> SPECULATE_CONDITIONAL, threshold 0.75-0.85.
- READ_NON_IDEMPOTENT + HIGH confusability, or any WRITE_REVERSIBLE -> WAIT.
- Anything NEVER_SPECULATE from step 1 stays NEVER_SPECULATE.

STEP 5 — Cancellation policy for every SPECULATE / SPECULATE_CONDITIONAL
tool: cache-and-discard (idempotent reads, just drop the cached result if
wrong) or cache-with-timeout-abort (non-idempotent reads — issue a
cancellation if the backend supports it, otherwise shorten the speculation
window instead of speculating blind).

STEP 6 — Coverage caveat. If I gave fewer than 10 transcripts, or some tools
have little or no transcript coverage, mark the whole output PROVISIONAL and
name exactly which tools lack coverage. A tool with ZERO coverage must be
scored WAIT, not guessed.

STEP 7 — Trust guardrail. For every SPECULATE / SPECULATE_CONDITIONAL tool,
state explicitly that its result must never be spoken to the caller or
treated as final until the completed transcript confirms the intent that
triggered it.

OUTPUT FORMAT:
A markdown table with columns: Tool | Side-effect class | Verdict |
Confidence threshold | Cancellation policy | Rationale.

Then:
- A short paragraph naming which tools are cleared for speculation and which
  are excluded, and why.
- A "Before you ship" checklist: validate thresholds against a held-out
  transcript set you did NOT use for this analysis, measure the real
  wasted-call rate against the target threshold, and confirm the runtime
  never surfaces a speculative result before confirmation.
- If step 6 applies, a PROVISIONAL banner at the top naming the affected
  tools.

GUARDRAILS — do not violate these:
- Never mark a payment, irreversible-commitment, outbound-notification, or
  compliance-sensitive-write tool as speculate-eligible, no matter what the
  transcripts show.
- Never invent a side-effect class or idempotency value I didn't give you —
  ask me instead of assuming a tool is safe.
- Never present this as a validated production policy — it's a design
  recommendation that needs a real pilot measurement before shipping.
- Never recommend surfacing a speculative result to the caller before
  confirmation, even for a low-risk tool.

Here is my tool manifest:
<paste tool manifest here>

Here are my example transcripts:
<paste transcripts here>

(Optional) my latency/wasted-call targets:
<paste targets here, or say "use defaults">
```

## What you get back

A per-tool table classifying each tool as `NEVER_SPECULATE`, `SPECULATE`, `SPECULATE_CONDITIONAL`, or `WAIT`, with a recommended confidence threshold, a cancellation policy, and the reasoning behind each — plus a checklist of what to measure before you actually turn speculative execution on in production. This is the design decision that precedes writing the middleware itself; it does not execute anything.

## Guardrails (why this is safe to run blind)

- No tool that touches money, irreversible commitments, outbound messages, or compliance-sensitive writes will ever come back marked eligible for speculation, regardless of what's in your transcripts.
- The output always tells you what you'd need to measure before trusting it in production — it is a starting policy, not a finished one.
- If your transcripts don't cover a tool, the prompt will say so rather than silently guessing a threshold for it.
