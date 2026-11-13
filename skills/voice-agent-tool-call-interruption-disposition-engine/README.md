# Tool Hold: Mid-Tool-Call Interruption Disposition Reviewer

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then paste your tool manifest where indicated. No other setup is required.

## What this does

You're building or hardening a voice agent (phone support bot, IVR, voice assistant) that calls backend tools mid-conversation — looking up an account, rescheduling an appointment, processing a refund, checking order status. Callers interrupt ("barge in") constantly, including while one of these tool calls is still running on the backend. Most teams handle the audio side of that interruption (stop the text-to-speech) but never decide what happens to the backend call itself: does it keep running? Get cancelled? Get cached for later? Get re-confirmed before anyone trusts it?

This produces a **design-time recommendation**, not working code — a policy table you hand to whoever wires up the actual interruption-handling logic in your voice framework (LiveKit Agents, Pipecat, Vapi, Retell, or a custom stack).

## What to hand over (data source: manual paste, nothing is connected automatically)

List every tool your voice agent can call, with as much of the following as you know. If you genuinely don't know a field, say "unknown" rather than guessing — the review treats unknown fields conservatively (see below) and will flag them rather than silently picking an answer.

For each tool, provide:
1. **Name** and a one-line description of what it does.
2. **Effect type**: is it read-only/idempotent (just fetches data, no side effects, safe to re-run) or side-effecting (writes, charges, books, cancels, mutates something)?
3. **Cost/latency**: roughly how expensive or slow is it (a fast local lookup vs. a slow third-party API call vs. something that costs real money to redo)?
4. **Cacheable / staleness tolerance**: if it's a read, how long does the result stay useful — seconds, minutes, hours?
5. **Cancellable pre-commit?**: if it's side-effecting, can the call be aborted before it actually writes, or does it commit the instant it's invoked?
6. **Idempotency key support?**: for side-effecting tools, does retrying with the same key avoid creating a duplicate effect (duplicate booking, duplicate refund, duplicate RMA)?

## The procedure

1. For each tool missing its effect type, mark it `NEEDS CLASSIFICATION` and stop there for that tool — list exactly what's missing. Don't recommend a disposition without knowing whether it's idempotent or side-effecting.
2. For every tool with enough information, apply this order:
   - **Idempotent + cheap/fast** → `finish silently, discard`. It's cheap to re-run, so there's nothing worth preserving.
   - **Idempotent + slow/expensive** → `finish-and-cache` with a TTL matching the stated staleness tolerance (use the shortest number given if a range was provided; if no tolerance was given at all, flag that as a gap instead of inventing a number).
   - **Side-effecting + explicitly cancellable before it commits** → `cancel-and-discard`. Abort it before it writes; nothing to clean up afterward.
   - **Side-effecting + not cancellable (stated as not cancellable, OR simply unknown — treat unknown the same as "not cancellable," conservatively) + idempotency-key-backed or genuinely low-harm if duplicated** (e.g., a confirmation text where sending it twice is harmless) → `finish silently, discard`, unless the result itself could be wrong after the caller's correction, in which case use the next bucket instead.
   - **Side-effecting + not cancellable + no idempotency key + meaningfully harmful if wrong or duplicated** (a booking, reschedule, cancellation, or anything a caller might have interrupted specifically to correct) → `finish-then-confirm`. Let the call complete, but the agent must explicitly confirm the resulting state with the caller before treating it as final — this is the exact scenario where a caller interrupts to change something and a silently-committed wrong action is the worst outcome.
   - **Side-effecting + not cancellable + financial or irreversible + not enough detail to be confident any of the above is actually safe** (e.g., a payment capture with no stated idempotency key and no stated cancellability) → `UNSAFE — must resolve before launch`. Name exactly what's missing (an idempotency key, cancellability info, a pre-commit confirmation step, or redesigning the action to be reversible/two-phase) rather than forcing it into a bucket that isn't actually justified.
3. Never recommend `cancel-and-discard` for an action that has already committed — cancellation is pre-commit only. If a tool commits the instant it's called, route it through the `finish-then-confirm` or `UNSAFE` buckets instead, and say so explicitly.
4. Write a one-line justification per tool, naming the specific attributes (effect type, cost, cancellability, idempotency-key support, harm-if-wrong) that drove the call.
5. Pull every `UNSAFE` and `NEEDS CLASSIFICATION` tool into its own "must resolve before launch" list.

## Output format

Produce exactly this structure:

```
## Tool Disposition Recommendations

| Tool | Effect Type | Disposition | TTL/Cache | Justification |
|------|-------------|--------------|-----------|----------------|
| ...  | idempotent / side-effecting | finish-silently / finish-and-cache / cancel-and-discard / finish-then-confirm | ... | ... |

## Needs Classification
- <tool>: missing <field(s)>

## Must Resolve Before Launch (UNSAFE)
- <tool>: <why nothing safe applies yet> — suggested fix: <specific fix>

## Notes
This is a design-time recommendation. Making it real requires wiring a barge-in listener and this policy table into your voice framework's tool-execution hooks (e.g., a LiveKit Agents or Pipecat plugin) — that implementation work is separate from this review.
```

## Guardrails — the AI running this must not

- Guess a tool's effect type, cancellability, or idempotency-key support when it wasn't stated. Put it under "Needs Classification" instead.
- Assign `cancel-and-discard` to anything that has already committed — that's a rollback/compensation problem, not a cancellation problem, and this review only flags it, it doesn't design the rollback.
- Let a financial or irreversible tool default to the easy "finish silently, discard" bucket just because information is missing — missing cancellability/idempotency info on a high-harm tool is itself grounds for `UNSAFE`, not a tiebreaker toward the simplest answer.
- Present the output as working software. It is a policy table for a human engineering team to implement, not executable code.
- Invent any cost, latency, cacheability, or idempotency fact that wasn't supplied, even to fill in a table cell.
