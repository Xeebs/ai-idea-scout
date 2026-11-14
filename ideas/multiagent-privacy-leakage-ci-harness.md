# LeakCheck CI: A Maintained, CI-Integrated Privacy-Leakage Regression Harness for Multi-Agent Systems

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-13-multi-agent-architectures.md · P8
- **Maturity verdict**: PARTIAL — Privatris/AgentLeak (the IEEE Access 2026 paper/benchmark repo, 40 stars, created 2025-12-24, pushed 2026-10-05) and its companion tool yagobski/agentleak (Python SDK/CLI/MCP server, 11 stars, pushed 2026-11-06) form a real benchmark — 1,000 scenarios, 7 channels, 5 LLMs, reporting a 68.8% inter-agent leak rate versus 27.2% in final outputs — but it is a single, fresh implementation/paper pairing, not yet a widely adopted or CI-integrated testing harness. No second independent tool covering the same ground was found (other "agentleak"-named repos are an unrelated naming coincidence).
- **Format**: BOTH — a CI-runnable harness that re-executes benchmark scenarios on every PR is PROJECT-shaped infrastructure; reviewing a described multi-agent architecture for likely inter-agent leak paths before any code exists is a separable one-shot design-review task.
- **Data Sources**: CONNECTED (project) — wraps the already-published AgentLeak benchmark corpus and the yagobski/agentleak CLI/SDK, both of which exist today and this project reuses rather than re-deriving a new adversarial scenario corpus from scratch. MANUAL (skill) — user pastes a description or diagram of their multi-agent system's context-sharing design (which agent sees which fields or tool outputs at which handoff).

## The Gap
An engine-sourced Hacker News item, "Show HN: AgentLeak – open-source privacy testing for multi-agent LLM systems" (2026-11-13, 3 points, github.com/Privatris/AgentLeak), looked like a brand-new, unvalidated tool at first glance. Verification found it is actually a substantial IEEE Access 2026 paper and benchmark with a companion Python SDK, measuring a 68.8% inter-agent leak rate across 1,000 scenarios and 7 channels — meaning the risk this names is systemic and measured, not anecdotal, but the only thing that exists today is a benchmark a team can run once and read, not a continuously-enforced gate that catches a regression the moment it's introduced.

## The Project
A CI-integrated gate that wraps the AgentLeak benchmark and SDK: on every pull request that touches agent context-passing logic, it re-runs a representative sample of the 1,000-scenario benchmark against the current build and fails if the inter-agent leak rate regresses beyond a declared threshold — the same role a test-coverage or lint gate plays today, applied to cross-agent data leakage instead of code quality. A companion PR comment lists which scenarios leaked and the specific agent-to-agent hop responsible, so a fix is actionable immediately rather than requiring a separate audit pass.

Components: a GitHub Action wrapping the yagobski/agentleak CLI; a scenario-sampling strategy (risk-weighted subset, not the full 1,000 every run, to keep CI time reasonable); a leak-rate threshold config; a PR-comment reporter naming the leaking scenario and responsible hop; a companion skill that reviews an architecture description for likely leak paths before any benchmark run is wired up.

## Tangible Impact
**Population**: Teams shipping multi-agent LLM products that pass user PII or other sensitive data between specialized sub-agents — a customer-support triage agent handing off to a billing agent, a multi-agent HR assistant with role-scoped sub-agents — the exact class of system AgentLeak's benchmark measured, where a single inter-agent leak of regulated personal data is a reportable incident under GDPR/CCPA, not a cosmetic bug.
**Mechanism**: Today AgentLeak is a report a team can read once; wrapping it in CI means a change that reintroduces a leak (e.g. removing a redaction step, or widening what context a handoff passes) is caught and blocked at PR time, the same way a regression test catches a broken feature, instead of being discovered in production or during an external audit.
**Measure**: (1) inter-agent leak rate on the benchmark, tracked per build over time (target: no regression above the declared threshold); (2) time-to-detection — a leak-introducing change caught at PR time versus discovered later in production or audit; (3) instrumentation coverage — number of inter-agent handoffs in the target system actually tested versus the total number present, closing blind spots over time.

## Why Now
The underlying benchmark and SDK were published within the last 30 days with a concrete, peer-reviewed-adjacent methodology (IEEE Access 2026) and a specific measured leak rate (68.8% at the inter-agent boundary) — giving this idea a credible, already-built measurement substrate to wrap in CI tooling today, rather than requiring the harness-builder to invent the adversarial scenario corpus itself.

## Skill Angle
Given a pasted description or diagram of a multi-agent system's context-sharing design — which agent receives which fields or tool outputs at each handoff, and what redaction (if any) happens between them — review it against AgentLeak's 7 known leak channels and flag the specific handoffs most likely to leak sensitive data, with a suggested redaction or scoping boundary for each. This is useful before any code exists or the CI harness is wired up, as a design-time check.

## MVP Sketch
Build a GitHub Action that pulls the yagobski/agentleak CLI, runs a fixed 50-scenario subset against a target multi-agent app's staging endpoint, computes the inter-agent leak rate, and fails the build above a configurable threshold, with a PR comment listing which scenarios leaked. Experiment: run the action against 2–3 open-source multi-agent demo repos (e.g. a CrewAI customer-support sample app), deliberately remove a redaction step on a test branch, and confirm the gate catches the regression. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- AgentLeak/Privatris is itself brand-new (a 3-point HN post, under a month old as a companion tool) — if its methodology has gaps or the maintainers abandon it, this idea's foundation weakens; worth a go/no-go check-in at three months.
- Running 1,000 scenarios on every PR is likely too slow/expensive for CI; this project must design a smart risk-weighted sampling strategy itself, not just inherit one.
- Passing the benchmark doesn't guarantee no leaks exist outside its 7 tested channels — must be marketed and used as a regression gate, not a certification of safety.
- Enterprise teams with the most at stake (healthcare, finance) may already run bespoke internal red-teaming; this needs to clearly beat "good enough homegrown checks," not just be the only named benchmark available.
