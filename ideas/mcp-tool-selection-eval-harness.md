# Route Check: A Standard Evaluation Harness for MCP Tool-Selection Failures

- **Status**: EXPLORING (promoted 2026-11-13 cycle 66: recurrence)
- **Date**: 2026-11-12
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-12-tool-use-mcp-ecosystem.md · P1
- **Maturity verdict**: PARTIAL — `accenture/mcp-bench` (516★) exists but hasn't been pushed since 2025-10-07 (>6 months stale); PyPI's `mcp-tool-selection-bench` is a narrow CI package scoped to the GitHub Copilot SDK; GitHub Engineering's internal offline-eval pipeline for the GitHub MCP Server and Apify's `actors-mcp-server` evals folder (exact-match + LLM-judge) prove the methodology works but aren't published, general-purpose tools. Academic benchmarks (BFCL-style, arXiv 2605.07112) measure general function-calling accuracy, not the specific "every tool passes its own tests, routing still fails" diagnostic workflow.
- **Format**: BOTH

## The Gap

r/modelcontextprotocol, "MCP tools all passed testing but the agent keep choosing wrong one. How to test tool selection?" (2026-10-13): "all the rest of tools were callable and direct tests passed all good. But when agent was asked a brand sentiment it selected another tool instead of relevant capability... How i test for this kind of failure? Do you use predefined evaluation scenarios, automated tests or end to end testing with real prompts?" The question got no answer pointing to an existing tool — a direct "has anyone built this" signal with no established methodology a practitioner can find by searching, even though a handful of large orgs have solved it privately.

## The Project

A standalone evaluation harness that treats tool-selection as its own testable layer, separate from per-tool functional tests. A developer defines a scenario set — natural-language intents mapped to the expected tool (or explicit "none of these" / "ask for clarification") — against their actual registered MCP toolset. The harness runs each scenario through the live tool-selection step (same descriptions, same system prompt, same model), scores exact-match plus a confusion matrix of which tool was wrongly picked instead, and fails CI when a new tool addition or a description edit silently increases misroutes on existing scenarios. Components: a scenario-definition format (YAML: intent → expected tool, with near-miss distractor scenarios deliberately designed to probe overlapping tool descriptions), a runner that calls the harness model/host directly, a confusion-matrix reporter, and a CI integration (GitHub Action) that gates merges on regression.

## Tangible Impact

**Population**: Teams running production agents with growing MCP toolsets (the official MCP Registry listed roughly 20,000–30,000 servers by September 2026, and any agent wiring up more than a handful at once hits overlapping-capability ambiguity) — concretely, developers who, like the Reddit poster, have individually-passing tools but a routing layer with no test coverage. Indirectly, the end users of those agents who experience a wrong action (wrong data pulled, wrong integration called) as a silent failure with no error message.
**Mechanism**: Today, tool-selection regressions ship invisibly because every per-tool unit test still passes — the harness turns an invisible routing regression into a failed CI check before merge, the same way an integration-test suite catches a contract break that unit tests miss.
**Measure**: Tool-selection accuracy (% of scenarios routed to the expected tool) tracked per release; number of misroute regressions caught in CI before reaching production vs. after (baseline: zero, since no test existed); median time for a developer to diagnose a reported misrouting incident using the confusion-matrix output vs. ad hoc log reading.

## Why Now

MCP toolsets are scaling fast enough (20k+ registered servers, agents routinely wiring up 10+ tools) that selection ambiguity is now a recurring, unanswered community question, while the pieces needed to build this — structured tool-call APIs, cheap enough inference to run scenario suites in CI, and existing (if scattered) internal precedent at GitHub/Apify — already exist.

## Skill Angle

A "diagnose this misroute" skill: hand it a transcript (user intent + the tool the agent picked + the tools it should have considered, with their descriptions), and it returns a structured diagnosis — which tool descriptions overlap enough to cause ambiguity, a suggested rewording to disambiguate, and 2–3 new scenario cases to add to a regression suite to catch the same failure again. This is useful standalone without ever running the full harness, and differs from the project by being a one-shot forensic review rather than a continuously-run test suite.

## MVP Sketch

2–4 weeks, 1–2 people: build the YAML scenario format, a runner against Claude's or GPT's native tool-calling API, and a confusion-matrix reporter. Experiment: take a real MCP toolset with 10+ overlapping-capability tools (e.g. a support/CRM bundle), hand-write 30 scenarios including deliberate near-miss distractors, and measure whether the harness catches a misroute that the per-tool unit tests miss when one tool's description is edited.

## Risks & Open Questions

- Any individual large org (Anthropic, a major MCP host) could publish their internal eval pipeline generally and absorb this space quickly — the pattern is a known internal practice, not an unsolved research problem.
- Scenario sets require ongoing hand-maintenance as a toolset evolves; without a way to auto-generate near-miss distractors, upkeep cost could exceed the value for small toolsets.
- Routing failures partly depend on the host/model's own tool-calling implementation, so results may not transfer cleanly across hosts (Claude Code vs. Cursor vs. a custom harness).
- Risk that this is "just write more tests," making the differentiator thin unless the confusion-matrix diagnostics and distractor-scenario tooling are genuinely better than a team's own ad hoc pytest suite.
