# Agent Run VCR: Deterministic Replay & Diff for Agent Behavior

- **Status**: PROPOSED
- **Date**: 2026-06-10
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-06-10-agentic-ai-autonomous-agents.md · P3
- **Maturity verdict**: PARTIAL — GitHub search finds only small or stale attempts: AnshKanyadi/culpa (13★), Sangkwun/sandy (13★), Jarvis2021/agent-vcr (7★), amosjyng/vcr-langchain (82★, last commit 2024). LangGraph Studio's checkpoint time-travel is the only maintained prior art and is framework-locked; no one has shipped the git-style record/diff/rewind workflow as a serious product.
- **Format**: PROJECT — recording/replay requires SDK-boundary hooks and a runtime, not a prompt.

## The Gap
A Show HN ("Version Control for AI Agents", cognatoai.com, 2026-06-07) and an r/AgentsOfAI workflow-visualizer thread (2026-06-08) both circle the same complaint: agent failures are timing-sensitive and disappear when you add logging, so they can't be reproduced. Laminar/Braintrust 2026 observability roundups name deterministic replay as the only reliable way to diagnose these bugs, yet describe it as emerging, not default. The existing attempts are single-builder demos with single-digit stars or two-year-stale cassette libraries.

## The Project
A recorder + replayer for agent executions: capture every LLM call, tool I/O, and timestamp at the HTTP/SDK boundary into a portable "cassette," then replay the run deterministically with zero live LLM calls — so a production failure becomes a reproducible test case. The git-style workflow is the centerpiece, not a bolt-on: commit cassettes, `diff` two runs of the same agent across a prompt or model change (which steps diverged, where, and why), and `rewind` to any step to fork an alternate continuation against a live model. Framework-agnostic by recording at the OpenAI/Anthropic SDK and MCP transport layer rather than inside LangGraph.

Components: SDK-boundary recorder (Python first); cassette format (content-addressed, diffable); replay engine with strict/fuzzy matching; `agentvcr diff` / `agentvcr rewind` CLI; pytest fixture for regression suites.

## Tangible Impact
**Population**: Engineers on incident-response and QA duty for production agent fleets at mid-size companies — the cohort behind Gartner's 2026-05-29 prediction that 40% of enterprises will demote or decommission autonomous agents over reliability failures, and the 129-comment r/AI_Agents thread ("the framework you pick barely matters... the thing that kills them is something else"); realistically the several-thousand teams worldwide with agents serious enough to have an on-call rotation.
**Mechanism**: Today a timing-sensitive agent bug costs repeated live re-runs (paying tokens each attempt) and often vanishes under instrumentation; a recorded cassette makes the first occurrence the permanent reproduction, and diffing runs turns "the agent got worse after the prompt change" from a vibe into a step-level report — cutting both debugging time and regression-escape rate.
**Measure**: (1) Share of production agent bugs reproducible offline on first attempt rises from near-zero to >70% on pilot teams' incident logs. (2) LLM token spend attributable to debug re-runs drops ≥80% for recorded agents. (3) Prompt/model upgrades gated by cassette regression diffs catch at least one real behavioral regression per pilot team per month.

## Why Now
Three independent demos of this exact shape surfaced within the 30-day window (culpa, sandy, the Cognato Show HN) — duct-tape convergence without a winner. Observability vendors are publicly naming replay the missing capability, and MCP's standardized transport makes tool I/O newly easy to intercept uniformly across frameworks.

## MVP Sketch
A Python package that monkeypatches the Anthropic and OpenAI SDKs to record/replay, a JSON-lines cassette format, and a CLI with `record`, `replay`, and `diff` (step-aligned, showing first divergence). Experiment: take three real flaky failures from one pilot team's agent; if all three replay deterministically and the diff pinpoints the divergent step, the hypothesis stands — if cassettes go stale on every minor prompt edit and matching is constant toil, kill it. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- LangSmith/Braintrust/Laminar already store full traces; any of them could ship replay-from-trace and own this — the strongest already-solved risk.
- Fuzzy matching is the hard part: replay breaks the moment a prompt differs by a timestamp; cassette brittleness killed VCR-style tools in other domains.
- Non-LLM nondeterminism (external API state, time, randomness) may dominate real failures and isn't captured at the SDK boundary.
- Cassettes contain full prompts/outputs — storing them raises data-retention and PII issues for exactly the regulated teams who most need replay.
