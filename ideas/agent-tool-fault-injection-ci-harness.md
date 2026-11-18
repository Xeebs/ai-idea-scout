# Chaos Stub: A Deterministic Failure-Injection CI Harness for Tool-Calling Agents

- **Status**: PUBLISHED
- **Date**: 2026-11-18
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-18-tool-use-mcp-ecosystem.md · P6
- **Maturity verdict**: PARTIAL — found several fault-injection packages beyond the cited practitioner write-up (`deepankarm/agent-chaos`, 35 stars, narrow adoption; `langchain-chaos-middleware`; `balagan-agent`; `agentfuzz`; a chaos-testing module inside AWS's `strands-agents/evals`, 260 stars, actively pushed) — but each is low-adoption, narrow, or a sub-feature of a broader eval SDK rather than a dedicated, widely-adopted CI harness purpose-built for timeout/429/malformed-response injection. No implementation squarely and maturely closes this specific gap.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the harness intercepts the standard MCP tool-call protocol (JSON-RPC over stdio/HTTP, spec-defined and already implemented in every MCP SDK) to inject faults into traffic against a developer's own real or mocked MCP servers; no pasted data is needed for the core harness. The Skill Angle accepts a live `list_tools` read or a pasted tool manifest.

## The Gap
A practitioner write-up (kunalganglani.com, "How to Do Agent Tool Call Failure Testing [2026 CI Harness]") describes hand-building a deterministic stub that injects timeouts, HTTP 429s, and malformed responses in front of a multi-agent publishing pipeline's tools, to verify the agent degrades or recovers safely instead of only being tested on the happy path. This is corroborated by the arXiv paper "Beyond Function Calling: Benchmarking Tool-Using Agents under Tool-Environment Unreliability" (arxiv.org/pdf/2606.25819), which argues "correct function calls are not sufficient." Both sources describe a one-off harness or a benchmark proposal — neither a shared, adopted, open-source implementation.

## The Project
A pytest/CI-integrated Python package that wraps the MCP SDK's transport layer with a small fault-injection DSL — `inject_timeout(tool, after_ms)`, `inject_429(tool, retry_after)`, `inject_malformed(tool, shape)` — placed deterministically in front of any of an agent's real tools, plus an assertion layer that checks the agent's declared recovery behavior per tool (retries with backoff, surfaces a graceful user-facing message, never loops indefinitely, never silently treats a malformed response as valid data). It is the convergence point the evidence says doesn't exist yet: deterministic fault injection plus degradation-behavior assertions, one maintained CI-integrated package instead of a practitioner's bespoke harness, a benchmark proposal nobody shipped, and several narrow/low-adoption point fragments.

Components: fault-injection DSL and transport interceptor · per-tool recovery-policy spec (declares what "safe degradation" means for that tool) · pytest/CI plugin and assertion library · failure-mode report generator.

## Tangible Impact
**Population**: engineering teams shipping tool-calling agents to production that depend on external APIs which can legitimately fail — grounded by LangChain's June 2026 practitioner survey finding 57.3% of respondents already have agents running in production, and by the arXiv/ToolFailBench research line finding agents that perform well against reliable tools fail under recoverable hazards like timeouts and malformed responses. This is a population of tens of thousands of teams now running tool-calling agents live, most of whom — per this digest's own cited practitioner write-up — are relying on happy-path testing alone today.
**Mechanism**: today an agent's tool-calling layer is tested, if at all, against a happy-path mock; teams discover its actual degradation behavior (sane retry vs. infinite loop, graceful failure vs. fabricated result treated as real) only when a real dependency times out or rate-limits in production. A deterministic stub that reliably injects these conditions on command turns "does this agent degrade safely" into a pre-merge, repeatable CI check instead of an incident post-mortem.
**Measure**: (1) count of unsafe-degradation bugs (infinite retry, fabricated-result-treated-as-real, uncaught exception reaching the user) caught in CI pre-merge vs. discovered in production, on pilot teams adopting the harness; (2) time to add a new fault scenario for a given tool vs. the hand-built bespoke harness described in the source write-up; (3) pass/fail stability of the same suite across 2–3 model families, since recovery behavior is partly a model-reasoning property, not purely a transport-layer one.

## Why Now
2026 production surveys (LangChain's 57.3% figure) confirm tool-calling agents are now mainstream production infrastructure, while this cycle's evidence shows five independent partial attempts (a practitioner's one-off CI harness, an arXiv benchmark proposal, and four narrow/low-adoption OSS packages) converging on the same need within the same window — individually de-risked pieces that nothing has yet combined into an adopted, dedicated tool.

## Skill Angle
"Design a fault-injection test plan for this agent's tools": hand the skill a tool manifest (live MCP `list_tools` read or pasted JSON) and it drafts, per tool, the specific fault scenarios worth testing — which calls are safely retryable vs. not, what a safe timeout-degradation response looks like for that tool, which malformed-response shapes are plausible given its real API — a one-shot authoring aid a developer feeds straight into the harness. The project is the persistent CI-integrated stub-and-assertion runner itself.

## MVP Sketch
2–4 weeks, 1–2 people. A Python package wrapping the MCP SDK's transport layer for injection (same integration point as this digest's companion sequence-assertion idea, but orthogonal: faults and recovery, not call ordering), a small fault DSL, and a pytest plugin asserting a declared per-tool recovery policy. Experiment: take a real multi-tool agent, inject each fault type against 3 of its tools, and confirm the harness catches at least one real unsafe-degradation bug the team didn't already know about.

## Risks & Open Questions
- Closely adjacent to this index's own `mcp-agent-tool-call-test-rig.md` ("Test Rig") — must stay clearly differentiated: Test Rig asserts call order/sequence against a recorded transport; this harness injects synthetic failure conditions and asserts recovery/degradation behavior, a different failure class (reliability under faults vs. correctness of sequencing), though the two could share a transport-mocking layer.
- AWS's `strands-agents/evals` chaos module (260 stars, actively maintained) could simply be extracted and generalized by AWS into a standalone package, closing this gap from inside an already-resourced team.
- "Safe degradation" is task-dependent (an infinite retry is sometimes correct) — the harness needs a declarative per-tool recovery-policy spec rather than a one-size-fits-all pass/fail, adding real design complexity beyond a simple stub.
- Fault injection against a live model's actual tool-calling decision is non-deterministic per model/version, cutting against the "deterministic CI gate" pitch unless scoped carefully (deterministic at the transport layer, probabilistic at the model-decision layer).
