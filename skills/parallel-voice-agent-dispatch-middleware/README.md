# Parallel-Dispatch Redesign Auditor for Voice Agent Handoffs

A paste-in prompt for any AI chat tool. Use it when your team runs a voice agent that routes calls to specialist agents (billing, technical, sales, scheduling) through a triage-then-handoff pattern, and you're deciding whether to redesign that handoff to fire specialists in parallel instead of waiting on serial classification — without reproducing the known failure mode where naive parallel dispatch barely helps and wastes calls.

## When to use this

You have (or are designing) a voice agent with a triage step that classifies the caller's intent and then hands off to one specialist agent at a time. You suspect or have noticed that this serial classify-then-handoff step adds a full round-trip of latency — audible dead air — before the right specialist even starts talking. You're weighing a parallel-dispatch redesign (fire several candidate specialists at once, arbitrate, cancel the losers) but want a structured review of whether it's safe and worthwhile for *your* specific architecture before anyone builds it. This is a design review, not a request to build the dispatch system itself.

## What to hand the AI

Paste all of the following directly into the chat — there's no connector or live system access here, just a text description:

1. **The framework/platform** you're using or planning to use (e.g. OpenAI Agents SDK, Vapi, Pipecat, LiveKit Agents, LangGraph, a custom build).
2. **How triage currently works**: what classifies the caller's intent (a model, keyword rules, DTMF menu), and what signal it uses (full utterance, partial transcript as the caller speaks, etc.).
3. **The list of specialist agents**, each with a one-line description of what it does, and critically, **whether it takes any action with a real-world side effect** (looks up an account read-only vs. issues a refund, sends an SMS, transfers to a human, writes to a CRM).
4. Optionally: any latency numbers you've already measured (time to first specialist response, call volume), though the review works without them.

If you don't know which specialists are read-only versus side-effecting, say so — the AI should ask you to clarify that distinction before it can tell you what's safe to cancel.

## What you'll get back

A structured review with these sections, in order:

1. **Architecture Reviewed** — a one-paragraph restatement of your setup, so you can confirm it understood correctly.
2. **Specialist Classification table** — one row per specialist: what it does, whether it's read-only/idempotent, reversible-side-effecting, or irreversible-side-effecting, whether it's safe to fire in parallel, and exactly what "cancel" means for it (for irreversible ones: "do not fire until commit" — never a false claim that it can be cleanly cancelled).
3. **Pre-Filter Recommendation** — if you have more than 3 specialists, a recommendation for a cheap first-pass narrowing step (rather than firing all of them every time, which is the exact mistake a real production benchmark made and then had to disable).
4. **Arbitration Policy** — a recommended confidence threshold for committing to one specialist and cancelling the rest, with the latency-vs-wasted-call tradeoff explained in plain terms (no invented percentages unless you supplied real measured numbers).
5. **Failure-Mode Check** — an explicit gut-check against the one known real-world attempt at this pattern: a benchmark that tried naive full-parallel dispatch and found it only cut latency 18% (not the 60% theoretically possible) while increasing wasted calls, and was disabled in production as a result. This section says plainly whether your proposed design (with the pre-filter and threshold) plausibly avoids that outcome or not.
6. **Recommendation** — Go, No-Go, or Narrower-Scope (e.g., "parallelize only your 3 read-only specialists, leave the refund and transfer specialists on serial handoff").
7. **Suggested Validation Benchmark** — what to measure (time-to-first-specialist-response, wasted-call rate) before committing engineering time to the full migration.

## Guardrails this review follows

- It will never tell you it's safe to cancel a specialist that issues a refund, writes to a CRM, sends an outbound message, or transfers to a human mid-flight — those are always flagged as "do not fire until the system has already committed to that specialist."
- It will never invent a specific latency-improvement number or cost figure. If you didn't give it real measured data, it gives you qualitative tradeoffs and says so.
- It will never recommend firing more than 3 specialists in parallel without first recommending a cheap filtering step to narrow the field — unfiltered full-parallel dispatch is the documented failure mode this review exists to prevent you from walking into.
- It is a one-shot design review of what you describe, not a working system, a benchmark run, or a measurement of your live call traffic — it will say so if you don't give it real data to work from.
- If you don't tell it which specialists have side effects, it will ask rather than guess.

## Example prompt to paste

"Review our voice agent's handoff architecture for a parallel-dispatch redesign. We use Vapi with a GPT-4-class triage model that classifies the caller's first utterance into one of five intents, then hands off serially: (1) Billing agent — looks up account balance via our internal API, can also issue refunds up to $50 without human approval; (2) Technical support agent — walks through a troubleshooting script, read-only; (3) Sales agent — answers pricing questions, read-only, can also send a follow-up SMS with a quote link; (4) Scheduling agent — books/reschedules appointments by writing to our calendar system; (5) Human transfer — escalates to a live agent queue. We're seeing about 1.5 seconds of dead air between the caller finishing their sentence and the specialist starting to respond, and want to know if parallel dispatch is worth building here, and what it should look like if so."
