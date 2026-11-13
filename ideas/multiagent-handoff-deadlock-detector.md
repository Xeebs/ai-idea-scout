# Stall Watch: A True Deadlock Detector for Multi-Agent Task-Handoff Chains

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-13-multi-agent-architectures-ii.md · P1
- **Maturity verdict**: PARTIAL — AgentSonar ships a `cyclic_delegation` detector for LangGraph/CrewAI/Claude Code (closed beta) but lists true mutual-wait deadlock detection as "coming soon"; Shinraya-Tech-Labs/AgentWatch's own open GitHub issue (#750, 2026-10-19) confirms even a dedicated observability tool built to fill exactly this gap hasn't shipped it.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the host framework's own execution/event trace (LangGraph callback handlers, CrewAI task-event listeners, AutoGen message logs, or a generic OpenTelemetry GenAI span consumer as fallback). These trace/event emission points already exist maturely in each framework today; this idea builds the new cycle/deadlock-classification layer consuming them, not the event source itself.

## The Gap
An open, unimplemented GitHub issue on AgentWatch — a tool whose explicit purpose is agent observability — asks for exactly this capability. The gap-analyst's own check found AgentSonar already flags *cyclic delegation* (a message loop) but explicitly defers true *deadlock* (mutual wait where two or more agents are each blocked on the other) as a future feature, and it's closed-beta. Nobody ships a tool that tells an operator, in real time, that a running multi-agent swarm has genuinely stalled rather than just looped.

## The Project
A lightweight instrumentation library that hooks into a running orchestration framework's own event/callback stream, builds a live directed task-handoff graph, and classifies suspicious patterns into either a benign cycle (already covered by AgentSonar) or a genuine mutual-wait deadlock. On detecting the latter, it fires a configurable policy — alert, auto-timeout-and-retry one leg, or apply a tie-breaking priority rule — instead of leaving the operator's only signal as a wall-clock timeout or a runaway API bill.

Components: framework adapters (LangGraph callback handler first, then CrewAI task-event listener, AutoGen message-log tailer, generic OpenTelemetry GenAI span consumer as a fallback); a live graph builder plus a wait-state/timeout-based deadlock classifier distinct from simple cycle detection; a policy engine for auto-break actions.

## Tangible Impact
**Population**: engineering teams running production multi-agent systems on LangGraph, CrewAI, or AutoGen — frameworks with hundreds of thousands of monthly downloads/stars between them — who today, per AgentWatch's own open issue, have no tooling for this and only discover a stalled run via a fixed timeout or a cost spike.
**Mechanism**: consuming the framework's own trace in real time lets a team catch a genuine deadlock the moment the mutual-wait condition forms rather than waiting out a timeout, and an auto-break policy can resolve many stalls without paging a human at all.
**Measure**: median time-to-detect a genuine deadlock vs. current timeout-based detection (often 5–30 minutes); false-positive rate on benign cyclic-delegation patterns in a synthetic benchmark; wasted compute/API spend avoided per incident.

## Why Now
Multi-agent frameworks matured into production use through 2026, and OpenTelemetry's GenAI semantic conventions now give a standard trace format to hook into, making a framework-agnostic deadlock detector buildable without a bespoke integration per framework.

## Skill Angle
A companion skill takes a pasted or uploaded architecture description (agent roles and handoff rules — e.g. a LangGraph graph definition, or a written description of who hands off to whom) and statically reviews it for deadlock-prone handoff cycles before the system ever runs. Output: a list of potential mutual-wait cycles in the declared handoff graph, each with a suggested breaking rule (priority order, timeout, or escalation). This is the design-review counterpart to the project's live runtime detection — it never touches a live run.

## MVP Sketch
Build one framework adapter first (LangGraph), instrument it to emit a task-handoff event stream, build a graph-cycle/wait-state classifier, and validate against 15 synthetic multi-agent graphs (5 true deadlocks, 5 benign cycles, 5 clean) to measure classification accuracy. Stack: Python, the LangGraph callback API, networkx for the live graph, a CLI plus optional webhook alert. Single experiment: does the detector separate benign cyclic delegation from true deadlock with near-zero false positives on clean graphs?

## Risks & Open Questions
- AgentSonar's closed beta may ship full deadlock detection before this does, closing the gap — check its public roadmap before committing.
- Separating "genuinely stuck" from "just slow" is a real-time heuristic problem; a wrong timeout threshold either triggers false alarms or misses real stalls.
- Framework-specific event schemas differ enough that a truly framework-agnostic adapter layer may take longer than a single-framework MVP suggests.
- Auto-break actions (killing/retrying a leg) risk double side effects if not paired with idempotency guarantees — likely needs to compose with this repo's existing agent-side-effect-idempotency-ledger idea rather than act alone.
