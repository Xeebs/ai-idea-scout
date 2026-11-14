# Common Board: An Open Blackboard Protocol Spec for Cross-Framework Multi-Agent Shared State

- **Status**: EXPLORING (promoted 2026-11-13 cycle 63: evidence density — 3 independent infra-vendor sources within the digest, sentra.app, Cockroach Labs, and Blck Alpaca, all converging on the same no-standardized-shared-memory gap)
- **Date**: 2026-11-13
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-13-multi-agent-architectures.md · P4
- **Maturity verdict**: PARTIAL — GitHub search turns up many independent point implementations of the blackboard pattern (whiteducksoftware/flock, 126 stars, actively maintained, pushed 2026-11-03, is the most mature; others are 0–4-star student/toy projects), but each is its own framework-specific convention. WebSearch confirms neither MCP (agent-to-tool) nor A2A (agent-to-agent) defines shared memory, and no standards-body spec exists as of 2026 — three independent infra vendors (Sentra, Cockroach Labs, Blck Alpaca) converge on the same "DIY, hand-rolled, not standardized" characterization. Point implementations exist, standardization doesn't.
- **Format**: PROJECT — a protocol spec plus reference server is infrastructure that must stay up and be integrated at runtime, not a one-shot judgment task.
- **Data Sources**: CONNECTED — the reference implementation ships as an MCP server, so any MCP-compliant client agent gets blackboard read/write/subscribe access through the already-mature, Anthropic-backed MCP transport and auth layer, with no bespoke integration required beyond a standard MCP connection. The MCP ecosystem itself already exists and is actively growing; this project builds a new *spec and server on top of it*, not a new transport layer.

## The Gap
Sentra's "MCP vs A2A" piece states plainly that neither protocol defines shared memory and that no standard agent-memory protocol has foundation backing yet. Cockroach Labs' blog makes the same point from the infra side: "the coordination point is the database, not the task message, and that's exactly what the protocol leaves undefined." A Blck Alpaca knowledge-base article describes teams manually implementing the blackboard pattern as a workaround, recommending hybrid shared-state-plus-messaging with single-threaded writes — three independent vendors converging on the same unfilled gap, with only fragmented, framework-locked point implementations (the best, whiteducksoftware/flock, is still a single project's convention, not a cross-ecosystem spec) filling it today.

## The Project
An open, versioned blackboard protocol — typed key/record read/write, subscribe-on-change, and single-threaded-write locking per key — plus a reference server exposed two ways: as a standalone HTTP/gRPC API, and as an MCP server so any agent already carrying an MCP client gets blackboard access for free. The spec is the centerpiece: a small, cross-framework contract any orchestration runtime (LangGraph, CrewAI, AutoGen) can target, the same role OpenAPI plays for REST or a shared schema registry plays for event buses, but for agent coordination state specifically instead of long-term memory or conversational history.

Components: a minimal spec document (schema, locking semantics, subscription model); a reference server (SQLite-backed to start); an MCP server wrapper exposing the spec as MCP resources/tools; thin client adapters for LangGraph and a raw function-calling loop to prove cross-framework interop; a migration note for teams currently using a hand-rolled Postgres/Redis table.

## Tangible Impact
**Population**: Engineering teams building cross-vendor, cross-framework multi-agent systems that use both MCP (for tool access) and A2A or an equivalent agent-to-agent protocol in the same deployment — the exact overlap Sentra's comparison piece addresses — who today each independently reinvent a Postgres- or Redis-backed shared-state table specifically because neither spec defines one for them.
**Mechanism**: Instead of every team designing and maintaining its own bespoke shared-state schema and locking logic from scratch, a new agent joining a blackboard-coordinated pipeline gets coordination state for free through its existing MCP connection — turning a multi-day custom-schema-and-glue-code task into a standard integration.
**Measure**: (1) integration time for a new agent to join an existing blackboard-coordinated pipeline (target: under an hour via the reference MCP server, versus the multi-day hand-rolled builds the digest's sources describe); (2) number of independently-built frameworks (LangGraph, CrewAI, a raw function-calling loop) demonstrated coordinating through one shared blackboard instance in a reference demo; (3) adoption proxy — stars/forks/downstream integrations of the reference server versus the fragmented point-implementations it targets replacing (whiteducksoftware/flock's 126 stars as the bar to clear).

## Why Now
MCP became a de facto cross-vendor standard through 2026, with both OpenAI- and Anthropic-ecosystem tools adopting it — giving this project a real, already-mature, already-trusted transport and auth layer to build a shared-state spec on top of, which the earlier, pre-MCP blackboard-pattern attempts the digest found never had and had to reinvent themselves.

## MVP Sketch
Define the minimal spec (get/set/subscribe over MCP resources and tools, single-threaded per-key write lock, versioned reads); build a SQLite-backed reference server with an MCP wrapper; write a thin LangGraph adapter. Experiment: wire two independently-built toy agents — one LangGraph pipeline, one raw OpenAI function-calling loop — to coordinate a simple shared task queue through the same blackboard server, and confirm both can read/write/subscribe with no custom glue beyond the standard adapter. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- Protocol-adoption ideas are hard to get adopted without major vendor backing; a small team's spec risks becoming "one more incompatible point-implementation," the exact irony the digest's own sources flag.
- MCP's resource/subscription model may not cleanly support single-threaded-write guarantees without an extension, which would require upstream coordination this project doesn't control.
- A2A's own steering effort could ship an official shared-memory extension first and obsolete this — the digest's May 2026 source explicitly says this is "unknown," so timeline risk is real.
- Hand-rolled Postgres/Redis solutions are already "good enough" for most single-team, single-framework deployments; the value is concentrated specifically in the cross-vendor/cross-framework case.
