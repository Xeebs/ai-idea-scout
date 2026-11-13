---
name: parallel-voice-agent-dispatch-middleware
description: Reviews a voice agent's serial triage-then-handoff architecture description and drafts a parallel-dispatch redesign plan — which specialists are safe to fire concurrently, where arbitration should commit, and where cancellation risks a side effect. Use when a team is deciding whether to migrate a voice routing layer off serial triage to cut handoff dead-air, before they build the migration.
---

# Parallel-Dispatch Redesign Auditor for Voice Agent Handoffs

## When to use this
A team has (or is designing) a voice agent that routes an incoming call or utterance to one of several specialist agents — billing, technical support, sales, scheduling, etc. — via a triage agent that classifies intent first and then hands off *serially* (classify, then start the specialist). They've noticed or suspect that this serial step is adding audible dead air before the right specialist starts responding, and they're weighing whether to redesign the dispatch to fire multiple candidate specialists in parallel and arbitrate. The trigger moment is "should we parallelize our handoff, and if so how, without reproducing the wasted-call problem" — not a request to build or run the dispatch coordinator itself. This is a one-shot design review, done before any migration work starts.

## Inputs
**Data source**: Manual — the user pastes a description of their existing or planned voice agent architecture: the framework or platform in use (e.g. OpenAI Agents SDK, Vapi, Pipecat, LiveKit Agents, LangGraph, a custom build), the triage agent's role and how it currently classifies intent, and a list of the specialist agents it can hand off to with a one-line description of what each one does and any action it takes (e.g. "Billing agent: looks up account balance via internal API, can also issue a refund"). Optionally they also paste current latency numbers (time-to-first-specialist-response, call volume) if they've measured any. There is no connector or live system access — this is a static review of text the user provides, not a runtime integration, log pull, or benchmark execution.

If the specialist list omits which agents take side-effecting actions (writes, payments, outbound messages) versus which are purely read-only/informational, ask for that distinction before producing the cancellation protocol — it is the single fact that determines whether parallel dispatch is safe for that specialist at all.

## Procedure
1. **Extract the current architecture**: name the framework/platform, the triage mechanism (what model/logic classifies intent, what signal it uses — full utterance, partial transcript, DTMF, etc.), and the serial handoff sequence as currently described.
2. **Classify every specialist** into exactly one of:
   - **Read-only / idempotent** (FAQ lookup, intent clarification, status check with no write) — safe to fire speculatively and cancel cleanly.
   - **Side-effecting, reversible** (starts a lookup that itself has no external side effect, e.g. a balance query) — safe to fire speculatively, but flag if the *lookup call itself* has a cost (rate limit, metered API) worth counting as wasted-call overhead.
   - **Side-effecting, irreversible or costly to cancel** (payment initiation, CRM write, outbound SMS/email, call transfer to a human) — NOT safe to fire until arbitration has committed; these must wait for commitment or be gated behind an explicit confirmation step even inside a "parallel" design.

   If a single specialist performs multiple actions at different risk levels (e.g., a read-only balance lookup plus a separate refund capability), classify that specialist by its highest-risk action for the "fire in parallel?" column, but note the lower-risk action separately in the reasoning so the team can see which part could be split into its own safely-parallelizable specialist later.
3. **Design the pre-filter, not a blind fire-all-N**: if there are more than 3 candidate specialists, recommend a cheap first-pass classifier (keyword/intent heuristic or a small fast model) that narrows the field to 2-3 plausible candidates before firing them in parallel — firing all N specialists for every call is exactly the shape of CallSphere's benchmarked failure (18% latency gain, not 60%, plus increased wasted calls). Name this narrowing step explicitly in the output; never recommend parallel-firing an unfiltered candidate set.
4. **Set an arbitration policy**: recommend a confidence threshold (e.g., a specialist's self-reported confidence or a lightweight classifier score) at which the system commits to one specialist and cancels the rest, and state the latency/wasted-call tradeoff of setting that threshold higher versus lower in qualitative terms — never assert a specific percentage improvement unless the user supplied real benchmark numbers to base it on.
5. **Write the cancellation protocol per specialist**, keyed to the classification from step 2: read-only/idempotent specialists get a simple "stop and discard" instruction; reversible side-effecting specialists get a "stop, and if the call already landed, discard the result without acting on it" instruction; irreversible specialists get an explicit "do not fire until commit" instruction — never a cancellation instruction, because there is nothing to safely cancel.
6. **Call out the CallSphere failure mode explicitly** as a named check: state whether the proposed design (with pre-filtering and the arbitration threshold) plausibly closes the gap between CallSphere's observed 18% and the theoretical 60%, or whether the specialist count/side-effect mix in this specific architecture makes that unlikely — and say which.
7. **Give a Go / No-Go / Narrower-Scope recommendation**: if more than half the specialists are irreversible side-effecting, recommend scoping the parallel-dispatch redesign to only the read-only/reversible subset rather than the full specialist roster, and say so plainly rather than forcing the full vision onto an unsuitable architecture.
8. **Recommend the validation step**: a small benchmark (replicating CallSphere's conditions as closely as feasible — same call volume shape, same specialist count) the team should run before committing to the migration, naming the two metrics that matter (time-to-first-specialist-response, wasted-call rate).

## Output format
A **Parallel-Dispatch Redesign Review**:

```
## Architecture Reviewed
<one-paragraph restatement of the input: framework, triage mechanism, specialist count>

## Specialist Classification
| Specialist | Action taken | Classification | Fire in parallel? | Cancellation instruction |
|---|---|---|---|---|
<one row per specialist>

## Pre-Filter Recommendation
<whether/how to narrow candidates before parallel fire, and why given the specialist count>

## Arbitration Policy
<threshold recommendation and the latency/wasted-call tradeoff in qualitative terms>

## CallSphere Failure-Mode Check
<explicit statement: does this design's pre-filter + arbitration plausibly beat the naive 18%-and-worse result, or not, and why>

## Recommendation
Go / No-Go / Narrower-Scope — <reasoning, including which specialists if any are excluded from the parallel redesign>

## Suggested Validation Benchmark
<what to measure before migrating for real: metrics, rough call volume/shape to test against>
```

## Guardrails
- Never recommend firing more than 3 specialists in parallel without a pre-filter step — cite the CallSphere benchmark's wasted-call failure explicitly when flagging this.
- Never mark a side-effecting, irreversible specialist (payment, CRM write, outbound message, human transfer) as safely cancellable — always route it to "do not fire until commit."
- Never invent a specific latency-improvement percentage or cost number unless the user supplied real measured data; give qualitative tradeoffs otherwise and say plainly that no measurement was provided.
- Never present this as a working coordinator, a benchmark result, or a deployed system — this is a one-shot design review of a pasted description, not code execution or live measurement.
- If the specialist list doesn't distinguish read-only from side-effecting actions, ask before producing the cancellation protocol rather than guessing a classification.
- Always include the CallSphere Failure-Mode Check section — skipping it is how a naive "just parallelize everything" recommendation slips through.
