# Tool Hold: A Mid-Tool-Call Interruption Disposition Engine for Voice Agents

- **Status**: EXPLORING
- **Date**: 2026-11-13
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-13-voice-multimodal-agents.md · P2
- **Maturity verdict**: PARTIAL (dedicated barge-in/turn-taking libraries exist — `rogerchappel/bargekit`, `rmsdev0/telnyx-onset`, `Suman1108-beep/livekit-barge-in-agent` — and framework docs (Pydantic AI realtime, Smallest.ai, NVIDIA's voice-agent blueprint) all cover general barge-in/TTS-stop, but they explicitly disagree or stay silent on what happens to an in-flight tool call specifically: Smallest.ai lets it finish, one SDK's docs say cancel-and-discard, NVIDIA's blueprint doesn't address tool calls at all; no single implementation resolves the mid-tool-call decision)
- **Format**: BOTH
- **Data Sources**: CONNECTED — the runtime engine hooks directly into a voice-agent framework's own call-state and tool-execution APIs (LiveKit Agents' or Pipecat's Python SDKs, both mature and widely deployed today) to observe in-flight tool-call state and VAD/ASR barge-in events live; no data is pasted during operation. The framework SDKs already exist; the per-tool disposition policy engine itself is the new piece this idea builds.

## The Gap
Soniox's wiki states plainly that "the orchestrator has to handle an interruption that arrives while a tool call is still in flight," and FutureAGI's barge-in guide puts a hard number on the user-facing half of the problem: TTS audio must stop within 60ms of barge-in or the agent reads as broken. But stopping the audio is only half the job — nobody has standardized what happens to the backend tool call itself. Smallest.ai's docs let it finish silently; another SDK cancels and discards it; NVIDIA's reference blueprint doesn't mention tool calls at all. Multiple vendor blogs in 2026 are each re-explaining this problem from scratch, which the gap-analyst reads as a shared unsolved gap, not a shared solution — several turn-taking libraries exist, but none resolves the specific decision of what to do with the tool call itself.

## The Project
A disposition engine that sits alongside a voice agent's tool-execution layer and, on every barge-in event, looks up a per-tool policy (declared at config time, not improvised at runtime) to decide: let the in-flight call finish silently and cache the result for later use, cancel it immediately and discard any partial result, or let it finish but re-ask before using the result if context has since changed. The policy is driven by tool metadata the team already has to declare anyway (idempotent vs. side-effecting, cheap vs. expensive, cacheable vs. not) rather than a blanket rule, and every disposition decision is logged so a team can audit why a given call was cancelled or kept.

Components: a tool-metadata schema (idempotency, cost, cacheability, staleness tolerance), a disposition-decision engine that consumes barge-in events and in-flight call state, a result cache with TTL for "finish silently, use later if still relevant," and a decision log for post-call debugging.

## Tangible Impact
**Population**: callers to AI voice agents that execute backend lookups or transactions mid-call — account lookups, appointment rescheduling, order-status checks, benefits eligibility checks — in the same high-volume segment PolyAI measures a roughly 1-in-5 barge-in rate for, and which Forrester's 2026 Wave reports now carries ~19% of inbound contact-center volume (up from 6% in 2024). The overlap of "calls with a barge-in" and "calls where a tool was mid-flight when it happened" is the population this specifically targets — a meaningful slice of every deployment that both performs real backend actions and gets interrupted regularly.
**Mechanism**: today a mishandled mid-tool-call interruption either silently discards a cheap, still-useful lookup result (wasting the latency/cost already spent and forcing a repeat round-trip) or, worse, commits a side-effecting action the caller just tried to correct (e.g., proceeding with a reschedule to the wrong time after the caller interrupted to change it). A declared per-tool policy stops both failure modes by making the disposition decision explicit and testable instead of accidental.
**Measure**: rate of "wasted re-fetch" (a cancelled call that, re-run, returns an identical result) before vs. after; rate of a side-effecting action completing after a caller's correction attempt (the safety-critical failure mode, target: zero in a labeled test suite); call-completion time delta on calls involving at least one mid-tool-call interruption.

## Why Now
Voice-agent frameworks (LiveKit Agents, Pipecat) now expose the hooks needed to observe tool-call lifecycle and barge-in events in the same event loop, which is what makes a cross-cutting disposition policy implementable as middleware rather than a framework fork. The 2026 proliferation of vendor-specific, mutually contradictory answers to this exact question (Smallest.ai vs. the unnamed cancel-and-discard SDK vs. NVIDIA's silence) is itself the signal that the decision has become common enough to need standardizing, not rare enough to keep improvising.

## Skill Angle
A companion skill, "tool disposition policy reviewer," takes a pasted tool manifest (function names, whether each is idempotent/side-effecting, approximate cost/latency) and produces a recommended per-tool disposition policy (finish-and-cache / cancel-and-discard / finish-then-confirm) with a one-line justification per tool, plus flags any side-effecting tool that has no safe disposition and needs a design change before launch. This is the design judgment a team makes once, before wiring up the runtime engine; the project is the live engine that executes the resulting policy during calls.

## MVP Sketch
Build the disposition engine as a LiveKit Agents plugin: a tool-metadata config schema, a barge-in-event listener that checks in-flight call state against the policy table, and a result cache with a short TTL. Test against a labeled set of ~30 simulated calls spanning both idempotent lookups and one side-effecting action, each with a scripted mid-tool-call interruption. The single experiment: does a declared per-tool policy eliminate the side-effecting "wrong action proceeds after correction" failure in the test suite, and does it measurably cut wasted re-fetches versus a naive cancel-everything baseline?

## Risks & Open Questions
- Getting the side-effecting/idempotent classification wrong for even one tool is the dominant risk — a misclassified payment or booking tool that's allowed to "finish silently" is the exact harm this exists to prevent.
- Caching a finished-but-discarded result and reusing it later risks staleness if the caller's intent genuinely changed between the interruption and the next turn; the "finish-then-confirm" policy exists for this but adds a conversational step some teams will want to skip.
- A framework vendor (LiveKit, Pipecat) could ship an opinionated default disposition policy before an independent, configurable engine gains adoption — differentiation has to be the per-tool declarative policy, not just "we handle it."
- This assumes barge-in detection itself is already reliable; if it isn't (a known adjacent gap), the disposition engine inherits that upstream error rate.
