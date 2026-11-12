# Tier Gate: A Severity-Tiered Fail-Open/Fail-Closed Guardrail Composer

- **Status**: EXPLORING
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production.md · P1
- **Maturity verdict**: PARTIAL — mature general-purpose guardrail toolkits exist (NeMo Guardrails 7.5k stars, Guardrails AI 7.6k stars, LLM Guard 3.2k stars) and a TrueFoundry gateway ships an "enforce but ignore on error" per-validator mode, but none exposes severity-tiered fail-open/fail-closed composition as a named, reusable feature — only cascading-latency and per-hook failure-mode guidance in vendor blogs.
- **Format**: BOTH

## The Gap
Vendor engineering writeups (a GMI Cloud post on an 86M-param fast gate ahead of an 8B hazard classifier, an Openlayer how-to on layered enforcement) describe the tiered fail-open/fail-closed pattern as the emerging 2026 norm, and `opendatahub-io/opendatahub-tests` PR #2670 shows a live team refactoring their own NeMo Guardrails call-pattern tests to model it. But every description is a single vendor's blog post or one team's internal refactor — there is no shared benchmark or reusable library for deciding which severity tier fails open vs. closed, or for validating that the composition math is correct.

## The Project
A declarative policy composer that sits on top of existing guardrail toolkits (NeMo Guardrails, Guardrails AI, LLM Guard) rather than replacing them: teams define severity tiers per category in a YAML policy (e.g., `safety: fail-closed`, `compliance: fail-closed`, `tone: fail-open`, `formatting: fail-open`) and the composer orchestrates classifier calls, resolves conflicting verdicts according to the declared tier ordering, and logs every composition decision. The centerpiece is a benchmark of mixed-severity scenarios (adversarial-high-severity mixed with benign-low-severity flags in the same response) used to prove a given policy's false-block rate on low severity and missed-hazard rate on high severity, instead of teams discovering their composition logic was wrong in production.

## Tangible Impact
**Population**: engineering teams at mid-size AI product companies (customer support bots, internal copilots, agent platforms) running layered guardrail stacks — a proxy for scale is the combined ~18k GitHub stars across NeMo Guardrails, Guardrails AI, and LLM Guard, implying thousands of teams already composing multiple checks by hand.
**Mechanism**: today teams hand-roll ad hoc code deciding which failing check blocks a whole response vs. logs-and-continues; mistakes in this logic either over-block (user frustration, support cost) or under-block (safety incident). A declarative composer with a validated benchmark replaces bespoke glue code with testable policy and lets teams catch composition bugs before shipping, not after an incident review.
**Measure**: false-block rate on low-severity benchmark cases at equal-or-better missed-hazard rate on high-severity cases, compared against each team's current naive "block on any failure" logic; time to implement/change a severity policy (before vs. after adoption); count of production incidents traced to guardrail composition bugs post-adoption.

## Why Now
2026 vendor writeups (GMI Cloud, Openlayer, Splunk, Coralogix) converge on tiered guardrail pipelines as the dominant production architecture, and the underlying toolkits (NeMo Guardrails, Guardrails AI) are mature and actively maintained (both pushed 2026-11-11) — the composition layer on top of them is the piece nobody has shared yet.

## Skill Angle
Trigger: a team hands over their guardrail categories and current block/allow behavior for each. The skill reviews the setup and drafts a recommended severity-tier policy (which categories fail-open vs. fail-closed, and in what composition order) as a one-shot judgment, flagging any category left ambiguous. The project is the runtime policy engine that enforces the resulting policy live against real traffic and the benchmark that validates it — the skill is a design/review aid that precedes committing to the infrastructure.

## MVP Sketch
A Python library that treats NeMo Guardrails/Guardrails AI/LLM Guard outputs as pluggable classifier signals, a YAML severity-tier config format, and a 50–100 case benchmark of mixed-severity adversarial + benign inputs scored for false-block and missed-hazard rates. Single experiment: run the benchmark through naive "block on any failure" logic vs. the tiered composer and show the delta in both error rates.

## Risks & Open Questions
- A guardrail vendor (NeMo, Guardrails AI) could add native severity-tier composition in a point release, absorbing this as a feature rather than leaving it a gap.
- The composition math might turn out to be simple threshold logic not worth productizing as a separate library.
- Without real production traffic from multiple teams, validating "better" composition stays benchmark-only and may not generalize.
- Teams may resist another policy DSL layered on top of already-complex guardrail stacks.
