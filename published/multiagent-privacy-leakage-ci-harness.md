# LeakCheck CI: Turning a One-Time Privacy Benchmark Into a PR-Blocking Gate for Multi-Agent Systems

A "Show HN" post with three points looked, at first glance, like just another weekend project. It wasn't. Behind it sat a peer-reviewed IEEE Access 2026 paper and a working benchmark that measured something most teams building multi-agent systems have never actually checked: how often one agent's context leaks into another agent's scope where it doesn't belong. The number was 68.8%. That's not a typo, and it's not the final-output leak rate everyone already worries about — it's the rate at which sensitive data crosses *internal* agent-to-agent boundaries, more than double the 27.2% leak rate measured at the point users actually see.

## The Gap

The signal came from an engine-sourced Hacker News item, "Show HN: AgentLeak – open-source privacy testing for multi-agent LLM systems" (2026-11-13, 3 points, github.com/Privatris/AgentLeak), posted the same day it was picked up — essentially zero community validation at first glance. Digging past the HN score told a different story: Privatris/AgentLeak is an IEEE Access 2026 paper and benchmark repo (40 stars, created 2025-12-24, pushed 2026-10-05), paired with a companion tool, yagobski/agentleak — a Python SDK/CLI/MCP server (11 stars, pushed 2026-11-06) that actually runs the thing. Together they measured 1,000 scenarios across 7 distinct data channels and 5 LLMs, landing on that 68.8% inter-agent leak rate.

What doesn't exist is anyone wrapping that benchmark into something a team actually keeps running. Right now AgentLeak is a report you can read once. It is not a gate that fires the moment a pull request quietly removes a redaction step or widens what context one agent hands to the next. No second, independent implementation of that gating layer turned up in the search — just the one fresh paper-and-SDK pairing, a real measurement substrate with nobody yet building the CI muscle around it.

## The Project

The fix borrows a shape every engineer already trusts: the lint gate, the coverage gate, except for cross-agent data leakage instead of code quality. On every pull request that touches agent context-passing logic, a GitHub Action re-runs a representative, risk-weighted sample of AgentLeak's 1,000-scenario benchmark against the current build. If the inter-agent leak rate regresses past a declared threshold, the build fails — and a PR comment names exactly which scenarios leaked and which agent-to-agent hop was responsible, so the fix is immediate rather than requiring a separate audit sweep weeks later.

Four pieces do the work: a GitHub Action wrapping the yagobski/agentleak CLI; a sampling strategy that runs a risk-weighted subset rather than the full 1,000 scenarios on every push (full coverage is too slow for CI, so this project has to design the sampling itself, not inherit one); a configurable leak-rate threshold; and a PR-comment reporter that turns a benchmark score into an actionable finding. A companion skill extends the same idea earlier in the lifecycle — before any CI harness exists, before any code is even written — by reviewing a pasted description of a multi-agent system's handoffs against AgentLeak's own taxonomy of leak channels and flagging the likely trouble spots in advance.

## Tangible Impact

**Population**: Teams shipping multi-agent LLM products that pass user PII or other sensitive data between specialized sub-agents — a customer-support triage agent handing off to a billing agent, a multi-agent HR assistant with role-scoped sub-agents — the exact class of system AgentLeak's benchmark measured, where a single inter-agent leak of regulated personal data is a reportable incident under GDPR/CCPA, not a cosmetic bug.

**Mechanism**: Today AgentLeak is a report a team can read once; wrapping it in CI means a change that reintroduces a leak (e.g. removing a redaction step, or widening what context a handoff passes) is caught and blocked at PR time, the same way a regression test catches a broken feature, instead of being discovered in production or during an external audit.

**Measure**: (1) inter-agent leak rate on the benchmark, tracked per build over time (target: no regression above the declared threshold); (2) time-to-detection — a leak-introducing change caught at PR time versus discovered later in production or audit; (3) instrumentation coverage — number of inter-agent handoffs in the target system actually tested versus the total number present, closing blind spots over time.

## Try It

A companion skill, `skills/multiagent-privacy-leakage-ci-harness/`, is already written for the design-time half of this that needs no CI setup at all: *"Reviews a described (not-yet-built) multi-agent system's handoffs for likely cross-agent privacy leak paths, scored against the AgentLeak benchmark's 7 named data channels. Use before writing code or wiring a CI leak-rate gate, whenever a multi-agent design passes sensitive fields between specialized sub-agents (support→billing, intake→scheduling, etc.)."*

To use it, paste a description of your multi-agent system's roster, handoffs, and declared redaction steps into any AI chat tool using the skill's `README.md` as the prompt template — or, if you're running Claude Code, drop the whole `skills/multiagent-privacy-leakage-ci-harness/` folder into `~/.claude/skills/`. It will classify every described handoff against AgentLeak's 7 leak channels, flag crossings with no declared mitigation, and propose a concrete fix for each — but it's a static read of what you describe, not a substitute for running the actual benchmark CLI once code exists.

## The honest caveat

AgentLeak/Privatris is itself brand-new — a 3-point HN post for a companion tool under a month old — so if its methodology turns out to have gaps, or the maintainers move on, this project's foundation weakens with it; worth a go/no-go check-in at the three-month mark. Passing the benchmark also doesn't certify a system leak-free outside its 7 tested channels — it has to be marketed and used strictly as a regression gate, never as a safety guarantee. And enterprise teams in healthcare or finance, the ones with the most at stake, may already run bespoke internal red-teaming; this needs to clearly beat "good enough homegrown checks," not just be the only named benchmark on the market.

Surfaced from `research/2026-11-13-multi-agent-architectures.md`, pattern `P8`.
