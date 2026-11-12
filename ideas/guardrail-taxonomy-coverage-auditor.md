# Coverage Map: A Nine-Category Guardrail Taxonomy Auditor

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production-pass2.md · P1
- **Maturity verdict**: PARTIAL — WebSearch found overlapping but non-identical taxonomies (an academic SoK at arxiv.org/abs/2506.10597, Mozilla's `any-guardrail` taxonomy, Gravitee's and multiple vendor blogs' input/output/tool-authorization/resource/audit groupings). No shared standard has converged, and no tool maps a team's actual implementation against any such taxonomy to surface uncovered categories — a build here is consolidation/differentiation, not greenfield.
- **Format**: BOTH

## The Gap
`awslabs/open-agentic-platform` issue #144 (opened 2026-11-05, 8 comments) shows a platform team's own audit discovering that "guardrails" had covered tool authorization, reachability, egress, and sandboxing in depth while having zero inbound or outbound content inspection — despite the platform looking fully guardrailed from the outside. The team only found this gap by manually enumerating categories against their implementation; no tool did it for them.

## The Project
A static-plus-runtime auditor that takes a team's guardrail configuration (gateway plugin configs, agent framework middleware, declared tool policies, classifier configs) and maps each piece against a canonical nine-category enforcement taxonomy (inbound content, outbound content, topic scope, tool authorization, reachability, egress, spend/rate limits, sandboxing, post-hoc audit), producing a coverage report that flags categories with zero or thin enforcement. Unlike the academic SoKs and vendor taxonomies, which only describe categories, the auditor ingests a real config/architecture and tells a specific team exactly where their blind spots are — the thing the OAP team had to discover manually.

## Tangible Impact
**Population**: platform engineering teams operating agent gateways or guardrail stacks who believe their system is "guardrailed" — the same category of team represented by `awslabs/open-agentic-platform` and the second project it cross-references ("Dogwood") — a proxy population is the combined ~18k GitHub stars across NeMo Guardrails, Guardrails AI, and LLM Guard, implying many teams assembling partial coverage from these pieces.
**Mechanism**: teams invest heavily in some guardrail categories (often the ones with mature OSS tooling, like tool authorization) while silently having zero coverage in others (content inspection, in OAP's case) because nothing forces an explicit accounting against the full category set. A coverage report surfaces this before an incident, the way OAP's team found it only through a manual design-review audit.
**Measure**: number of zero-coverage categories surfaced per audited deployment that the team did not already know about (validated via follow-up interview); time from "we think we're guardrailed" to an accurate category-by-category coverage map (target: hours, not a multi-week internal audit like OAP's); reduction in incidents traced to an unaudited blind category, post-adoption.

## Why Now
Multiple 2026 taxonomies (academic SoK, Mozilla, Gravitee) have independently converged on roughly the same category set without anyone building the auditing tool on top of them, and the OAP thread is live, current evidence that even sophisticated platform teams miss whole categories without one.

## Skill Angle
Trigger: a team pastes or links their guardrail/gateway configuration, middleware list, and a short description of what each piece does. The skill maps each item against the nine-category taxonomy and returns a coverage table with explicit "no coverage found" flags, as a one-shot design-review audit before committing to build the always-on version. The project is the continuous auditor wired into CI/deploy pipelines that re-checks coverage on every config change; the skill is the point-in-time human-readable version of the same judgment.

## MVP Sketch
A rubric + prompt-driven classifier that takes a structured description of a team's guardrail stack (which gateway, which plugins, which classifiers, which policies) and outputs a category-by-category coverage table with confidence levels and specific missing-coverage flags. Validate against OAP's own documented state (tool authorization: covered; content: uncovered) as a known-answer test case. Single experiment: run the auditor against 3-5 public OSS agent-platform repos' documented guardrail setups and check whether it reproduces maintainer-acknowledged gaps (like OAP's) without being told the answer in advance.
## Risks & Open Questions
- The taxonomy itself isn't standardized yet; the auditor risks enforcing one opinionated category split that teams dispute.
- Static config analysis can't fully verify runtime behavior (a configured check could be silently misfiring) — this complements but doesn't replace the admission-time validation gap (see the companion idea on agent tool/MCP grant admission).
- A guardrail vendor could ship this as a built-in dashboard feature, absorbing the gap quickly once named.
- Risk of false confidence: a "covered" category might still be weakly implemented (a checkbox, not a robust classifier) — the auditor needs to grade depth, not just presence.
