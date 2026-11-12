# Soft Landing: A Graceful Degradation Controller for Guardrail Latency Budgets

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production-pass2.md · P5
- **Maturity verdict**: PARTIAL — one vendor (Waxell) claims an alternative deterministic enforcement layer at ~0.045ms p95 versus "hundreds of milliseconds" for judge-based checks, and the broader detection/enforcement literature (Weaviate, Arize) implicitly recommends cheap deterministic checks in the hot path with LLM judges reserved for sampled/async review. These are single-vendor claims and general best-practice advice, not an independently evaluated, widely-adopted "graceful degradation under SLO" product.
- **Format**: BOTH

## The Gap
A futureagi.com glossary entry on LLM guardrails puts the pre- and post-processing guardrail latency budget at roughly 250-500ms p99, and states plainly that teams disable guardrails entirely once that budget is exceeded, rather than optimizing or shifting checks async. This is a binary on/off failure mode: a team either eats the full latency cost of every check or drops all guardrail coverage, with nothing in between documented as a shipped pattern.

## The Project
A runtime control layer that sits in front of a team's existing guardrail checks (classifiers, judges, rule engines) and, when real-time latency telemetry shows the request-time budget is about to be breached, degrades coverage in a declared order — dropping the most expensive/lowest-marginal-value checks first, falling back cheaper deterministic checks, or deferring non-blocking checks to async/sampled review — instead of disabling guardrails wholesale. The centerpiece is a policy language for declaring degradation order plus a live dashboard showing what coverage was actually in effect for every request, so "guardrails were off" never happens silently.

## Tangible Impact
**Population**: engineering teams running latency-sensitive production LLM agents (customer support, voice, real-time chat) who today face the binary choice futureagi describes — full guardrail latency tax or no guardrails — a proxy population is any team on the ~18k combined GitHub-star guardrail-toolkit base (NeMo Guardrails, Guardrails AI, LLM Guard) operating under a hard p99 SLO.
**Mechanism**: without a declared degradation order, a latency spike forces an all-or-nothing decision that either breaches the SLO or drops all safety coverage; a degradation controller keeps the cheapest, highest-value checks running under load instead of zero, and makes the degraded state visible and auditable rather than a silent toggle.
**Measure**: percentage of requests under load that retain at least baseline-tier coverage versus the team's current binary-disable baseline; SLO breach rate with the controller active versus without; number of "silent full-disable" incidents (guardrails off with no record of why) before versus after adoption.

## Why Now
The 250-500ms latency-tax framing and the disable-under-pressure behavior are both named explicitly in current 2026 guardrail literature, and deterministic low-latency alternatives (sub-millisecond per the Waxell claim) are now mature enough to serve as credible fallback tiers rather than hypothetical.

## Skill Angle
Trigger: a team hands over their current guardrail checks, each one's measured latency, and their p99 SLO. The skill drafts a recommended degradation order (which checks drop first, which deterministic fallbacks substitute for which expensive checks) as a one-shot design review, flagging any check for which no cheap fallback exists. The project is the runtime controller enforcing that order live against real traffic and telemetry; the skill is the one-time policy-design pass that precedes committing to the infrastructure.

## MVP Sketch
A lightweight proxy wrapping 2-3 guardrail checks of varying cost (one classifier, one rule-based filter, one LLM-judge call), instrumented with real latency telemetry and a declared degradation policy (YAML ordering of what to drop first). Single experiment: replay a traffic trace with an injected latency spike and compare total guardrail coverage retained (checks still running) under the degradation controller versus a naive "disable everything over budget" baseline.

## Risks & Open Questions
- This is adjacent to severity-tiered composition (Tier Gate) and to judge-distillation (Fast Lane) — the differentiator is reacting to real-time load/latency pressure specifically, not static severity policy or judge conversion; risks blending into either if not kept narrow.
- Evidence is a single glossary claim plus one vendor's unverified latency number; needs a real production trace to validate the disable-under-pressure behavior actually happens as described.
- Declaring a "safe" degradation order is itself a safety-critical decision — a poorly chosen order could silently drop the highest-severity check instead of the lowest.
- A gateway vendor could add adaptive degradation as a built-in feature quickly once the pattern is named.
