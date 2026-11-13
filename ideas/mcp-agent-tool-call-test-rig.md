# Test Rig: A Unified Mock-Transport + Sequence-Assertion Testing Framework for Agent Tool Calls

- **Status**: EXPLORING (promoted 2026-11-13 cycle 56: evidence density — ≥2 independent threads)
- **Date**: 2026-11-13
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-13-tool-use-mcp-ecosystem-2.md · P2
- **Maturity verdict**: PARTIAL — GitHub/web search surfaced real but fragmented point solutions: `AgentProof` (pytest plugin with `assert_tool_order`/`assert_tool_called`/`assert_max_steps`), `assay-core` (Rust crate with exact/subsequence/must-not-call trace assertions), `agentguard` (trace replay + assertion builder), plus `itsPremkumar/mcptest` and `guruambati/agent-tool-call-testing-framework` on GitHub. None combine mocked transport + model-in-the-loop behavior + sequence assertions in one maintained, adopted framework.
- **Format**: BOTH — the test runner (mock transport, assertion engine, CI integration) is persistent CI-integrated infrastructure; drafting a starter scenario suite from a tool manifest is a separable one-shot authoring task.
- **Data Sources**: CONNECTED — the mock-transport layer intercepts the standard MCP tool-call protocol (JSON-RPC over stdio/HTTP, spec-defined and already implemented in every MCP SDK today) to record/replay against a developer's own real MCP servers; no pasted data needed for the core framework. The Skill Angle accepts a live `list_tools` read or, if no live connection exists, a pasted JSON tool manifest.

## The Gap
Several small libraries mock an individual MCP server's responses for unit tests (`zeph-mcp`'s `MockMcpServer`, the `mcpkit-testing` Rust crate, the npm `mcp-server-mock` package, `vaayne/mcphub`'s internal testing package), and a [DEV Community post](https://dev.to/aidevhub/building-an-mcp-tool-call-test-rig-with-the-python-sdk-in-2026-4iln) describes hand-building a tool-call "test rig," while a separate [DEV Community piece](https://dev.to/rupa_tiwari_dd308948d710f/why-testing-mcp-servers-with-real-ai-models-matters-2026-55e9) argues mocks alone "miss how real models behave" because tool-calling habits differ per model family. Five independent fragments exist; nothing combines them.

## The Project
A pytest-style cross-SDK framework with three parts: (1) a mock MCP transport that records real tool-call traffic once and replays it deterministically for CI, (2) a scenario DSL exposing sequence assertions (`assert_tool_order`, `assert_max_steps`, `assert_not_called`, subsequence matching) on the full trajectory of calls an agent makes — not just whether one call was correct — and (3) a multi-model fidelity harness that re-runs the same scenario against 2-3 live model APIs to flag cases where mocked behavior diverges from a real model's actual tool-calling habits. It is the convergence point the evidence says doesn't exist yet: mocked transport + scripted/model-in-the-loop behavior + sequence assertions, one maintained package instead of five incompatible fragments.

Components: mock-transport recorder/replayer · scenario DSL and assertion library · pytest/CI plugin · multi-model fidelity runner · trace-diff reporter.

## Tangible Impact
**Population**: developers building and maintaining MCP-integrated agents with multi-step tool-call sequences — concretely the authors of the five independent fragments found in search (AgentProof, assay-core, agentguard, mcptest, agent-tool-call-testing-framework), each solving one piece of this within the same 30-day window, plus any team shipping an agent where calling tools out of order (e.g., transferring funds before verifying balance) causes a wrong real-world action.
**Mechanism**: today teams either skip testing tool-call sequences entirely (bugs surface only via user reports) or hand-write bespoke assertion helpers per project. A maintained framework combining mocked transport, sequence assertions, and multi-model fidelity checks turns "agent called tools out of order" into a standard, catchable pre-merge CI failure instead of a production incident.
**Measure**: (1) count of real sequencing bugs caught in CI pre-merge vs. post-ship, on pilot teams migrating from no test coverage; (2) time to author a new test scenario vs. a hand-rolled bespoke assertion; (3) divergence rate between mocked-scenario pass/fail and live-model pass/fail across 2-3 model families, validating (or refuting) the "mocks miss real model behavior" concern raised in the evidence.

## Why Now
MCP has crossed into mainstream production agent stacks (92K-star `modelcontextprotocol/servers`), and five independent teams converged on fragments of this fix within one month, each missing a different piece (mocking, or sequencing assertions, or multi-model fidelity). The pieces now individually exist and are de-risked; no one has combined them.

## Skill Angle
"Generate test scenarios from a tool manifest": hand it a tool list with descriptions (live-read or pasted), and it drafts a starter scenario suite including deliberate edge cases — tool pairs that should never fire in a given order, required preconditions, near-miss distractors — a developer drops straight into the framework. This is a one-shot authoring aid; the project is the persistent CI-integrated runner.

## MVP Sketch
2-4 weeks, 1-2 people. Build a Python package wrapping the official MCP Python SDK's transport layer for record/replay, a pytest plugin exposing the four core sequence assertions, and a small multi-model fidelity harness (Claude, GPT, a local Llama). Experiment: take a real 10+ tool MCP agent (a support/CRM bundle), write 15 sequencing-sensitive scenarios, inject a deliberate call-order bug, and confirm the framework catches it where per-tool unit tests don't.

## Risks & Open Questions
- Closely adjacent to this index's existing `mcp-tool-selection-eval-harness.md` ("Route Check"), which also tests MCP tool-call behavior — must stay clearly differentiated: Route Check scores single-call tool-selection accuracy via a confusion matrix; this framework asserts sequence/order/count across multi-call trajectories with a mocked transport for deterministic CI, a different failure class.
- Any of the five existing point solutions could simply add the missing piece and converge first, undercutting this project's reason to exist.
- Multi-model fidelity checking requires live API calls in CI, adding cost/latency/flakiness that could undermine the "deterministic CI gate" value proposition if not carefully bounded (e.g., nightly-only, not per-PR).
- Each MCP SDK language (Python, TS, Rust) needs its own transport-mocking adapter; multi-language parity is a maintenance cost similar to what appears to have stalled several of the existing point solutions.
