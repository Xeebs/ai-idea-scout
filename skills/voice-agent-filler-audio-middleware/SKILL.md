---
name: voice-agent-filler-audio-middleware
description: Designs the filler-audio (holding-phrase) policy for a voice agent's slow tool calls — which tools need it, what to say, and when to cancel — from a pasted tool/latency manifest, before anyone wires it into the runtime.
---

# Filler Coverage Designer

## When to use this

Use this when a team is building or auditing a voice agent (phone bot, voice assistant) that calls backend tools/functions mid-conversation — a database lookup, an order-status check, a third-party API, a transaction — and callers experience dead air while that call is in flight. The trigger moment is specifically *before* anyone writes the runtime sequencing code: this skill produces the design decision (which tools need a spoken filler, what it should say, when it cancels) that a developer then wires into their voice framework. It is not a replacement for that runtime wiring, and it is not useful once the policy is already implemented — at that point you're debugging the middleware itself, not designing the policy.

Do not reach for this for latency problems that aren't tool-call related (e.g., slow STT/TTS round-trip, network jitter) — this skill only covers the "tool call is pending and the caller is hearing silence" gap.

## Inputs

**Data source**: Manual — the parent idea's runtime middleware (the "Hold Line" project this skill is a companion to) is Connected: it hooks live into a voice-agent framework's (LiveKit Agents or Pipecat) tool-execution and TTS-playback-queue events. This skill is different — it runs at design time, before that wiring exists, so it has nothing to connect to. The user must paste:
1. A **tool manifest**: for each tool/function the agent can call, its name, a one-line description of what it does, and latency data — ideally p50/p95 observed from real logs, or a typical/worst-case range if that's all they have (e.g., "lookup_order_status: ~400ms typical, up to 2.5s on slow days" is fine; a bare guess with no number at all is not).
2. Optionally: the target language(s), any brand-voice constraints (e.g., "never sound chipper," "formal tone only"), and whether their framework currently has reliable barge-in/interruption detection (if unknown, say so — this changes the guardrail flagging below).

If the user has no latency numbers at all for a tool, they must say "no data" explicitly rather than let the skill guess — see Guardrails.

## Procedure

1. **Parse the manifest** into one row per tool: name, description, latency figures as given.
2. **Classify each tool** into one of four categories based on its description: `lookup` (read-only data fetch, e.g. account balance), `transaction` (a mutating action, e.g. "cancel my order"), `search` (open-ended/variable-time query, e.g. "find flights matching..."), `external-passthrough` (calls a third-party API outside the team's control, e.g. a payment processor or shipping carrier). If a tool's description is too thin to classify confidently, mark it `UNCLASSIFIED` and ask the user for a one-line clarification rather than guessing.
3. **Apply the filler-worthy threshold.** Default threshold: p50 ≥ 700ms OR worst-case ≥ 1.5s. If the user supplied their own threshold, use that instead and say so. Any tool whose latency figures are entirely below threshold gets `No filler needed` — do not invent a reason to add one.
4. **For every tool that crosses the threshold**, assign a phrase set from the category's library (below), written in the user's requested tone if specified. Never reuse the exact same phrase as the tool's immediate acknowledgment and its escalation line — they must read as a progression, not a loop.
5. **Build the escalation ladder** for tools whose worst-case/p95 latency exceeds 3x the *worst-case threshold* (default 1.5s, or the user's custom worst-case threshold) — not 3x the p50 threshold, which is a much smaller number and would over-trigger ladders on merely-above-threshold tools. Concretely: initial filler at the p50-threshold crossing, then one escalation line if the wait passes the second checkpoint (3x the worst-case threshold, e.g. 4.5s by default), and a final fallback line ("offer a callback" / "let the caller know this is taking longer than usual") if it passes the tool's own stated worst-case figure entirely. Tools that cross the p50 threshold but whose worst-case stays under that 3x checkpoint get a single filler line only, no ladder.
6. **Write the cancellation policy.** State explicitly: filler playback must stop the instant either (a) the tool call resolves and the real response is ready to speak, or (b) the caller barges in (starts speaking over the filler). Name the two framework-level signals this depends on (tool-result-ready event; barge-in/VAD interrupt event) without implementing them — that's the runtime middleware's job, not this skill's.
7. **Flag risk conditions**: any `UNCLASSIFIED` tool, any tool with "no data" instead of real latency numbers, and — critically — if the user said barge-in detection is unreliable or unknown in their stack, flag every tool in the output with a warning that filler audio risks talking over the caller until that's fixed.
8. **Produce the output** in the format below.

## Output format

A single markdown report with these sections, in order:

1. **Coverage table** — columns: Tool | Category | Latency (as given) | Threshold used | Filler needed? (Yes/No/Flagged)
2. **Phrase library** — one subsection per category that has ≥1 flagged tool, 3-5 example filler phrases for that category plus one escalation line and one fallback line, written in the requested tone.
3. **Escalation ladders** — one short ladder (initial → escalation → fallback, with the trigger timing for each step) per tool that needed one per step 5.
4. **Cancellation policy** — a short, explicit spec: the two trigger signals, and the stated target of stopping filler playback within ~150ms of either trigger (flag this as a number to validate against the user's actual framework, not a guarantee).
5. **Open flags** — a bulleted list of every `UNCLASSIFIED` tool, every "no data" tool, and the barge-in-reliability warning if applicable. If there are none, write "None."

This output is meant to be handed directly to whoever wires the runtime middleware (LiveKit Agents, Pipecat, or equivalent) as their implementation spec — it should need no further design decisions, only engineering.

## Guardrails

- Never assign a filler phrase to a tool whose latency figures are entirely below the threshold — padding coverage with unnecessary fillers is exactly the "it's broken" perception problem this exists to prevent.
- Never invent latency numbers for a tool the user marked "no data" — flag it as an open risk instead of guessing a figure, since a wrong threshold decision (filler too early, annoying; or too late, dead air) is worse than an honest gap.
- Never write a filler phrase that implies a false state ("found it!", "done!") before the tool has actually returned — that erodes trust worse than silence does.
- Never recommend looping the identical filler clip more than once without escalating the wording — a repeated loop reads as the system being stuck, not working.
- Never skip the barge-in-reliability flag when the user says it's unknown or unreliable — shipping a confident-sounding cancellation policy on top of unreliable interruption detection is the single failure mode called out in the parent idea as the thing that makes filler audio feel broken.
- Never present this skill's output as a replacement for actually building and testing the runtime middleware — this is the design decision, not the engine; say so if the user seems to think pasting a manifest here is the whole project.
