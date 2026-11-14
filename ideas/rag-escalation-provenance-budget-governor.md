# Budget Gate: An Opt-In, Provenance-Tracked RAG Escalation Governance Layer

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: RAG techniques
- **Source**: research/2026-11-13-rag-techniques-ii.md · P1
- **Maturity verdict**: PARTIAL — narrow point-solutions exist (`ctxbudgeter`: token-budgeted context assembly with an auditable "Context Bill of Materials" + CI risk-budget gate; `Provena`: provenance hash-chaining with a policy engine that can block unprovenanced context) but neither defaults retrieval to opt-in/off, and no project combines provenance-tracking + context-budget-cap + opt-in-escalation as one governance layer.
- **Format**: BOTH
- **Data Sources**: CONNECTED — middleware that wraps whichever external retrieval source the team already has (a vector DB client, or a web-search API such as Tavily/Exa/Bing Search API). These connectors already exist maturely; this project adds a governance/audit layer on top of calls to them rather than building a new retrieval connector itself.

## The Gap

A GitHub issue on `YourAKShaw/irisveil` (#10, 2026-11-10, 2 reactions) describes a verification/fact-checking agent whose default mode is deliberately quote-grounded against first-party sources, not RAG — and the team is now designing an *opt-in* external-source layer with per-request provenance tracking and a hard context-budget cap, rather than just flipping retrieval on. Most RAG tooling treats "turn retrieval on" as binary; this issue frames retrieval as a bounded, auditable escalation path for a system that otherwise avoids it. No general framework for this governance shape surfaced elsewhere in the digest, and the two closest point-solutions found (`ctxbudgeter`, `Provena`) each cover one piece, not the combination.

## The Project

A middleware library that sits between an agent and its existing retrieval source(s) and turns "call external RAG" into a governed, auditable decision instead of an always-on retriever. The core loop: (1) a policy layer decides, per query, whether first-party/quote-grounded evidence is sufficient or escalation to external retrieval is warranted; (2) if escalating, a hard context-budget cap bounds how much external content can be pulled in; (3) every retrieved passage is tagged with provenance (source, retrieval timestamp, which generated claim it backed) and written to an append-only audit log; (4) the escalation decision itself, and the budget spent, are logged alongside the output.

Key components: a pluggable escalation-trigger policy (e.g., "first-party search returned fewer than N supporting quotes"), a token/context-budget accountant, a provenance tagger that survives into the final generated response (so each claim can be traced to its source), and a queryable audit store. The novel pattern is treating retrieval as a logged, bounded *exception* rather than a default pipeline stage — the opposite orientation from almost all RAG tooling.

## Tangible Impact

**Population**: Teams building trust-sensitive verification and research agents — sales/prospect fact-checkers, compliance research assistants, journalism and due-diligence bots — where the product's entire value proposition rests on not hallucinating, and where adding broader coverage via external retrieval today means either skipping it (losing coverage) or bolting on generic RAG (losing the auditability that earned user trust in the first place). No reliable headcount estimate exists for this specific segment, but it spans the fast-growing set of funded AI sales-intelligence, legal/compliance research, and fact-checking startups that advertise "grounded, no-hallucination" as a core claim.

**Mechanism**: By making external retrieval an opt-in, budgeted, provenance-tracked escalation rather than an always-on pipeline, these teams can expand coverage to questions their first-party-only verification couldn't answer, while giving a reviewer, auditor, or end customer a claim-by-claim trace of exactly which external source backed each statement — preserving the auditability that distinguishes them from a generic RAG wrapper.

**Measure**: (1) % of claims in escalated responses with a complete, resolvable provenance chain (target near 100%); (2) unsupported/hallucinated-claim rate before vs. after enabling escalation on a held-out claim set (should stay flat, not rise); (3) context-budget overrun incidents per week under the cap (target ~0); (4) % of previously-refused queries now answerable once escalation is available, without exceeding budget.

## Why Now

The IrisVeil issue (Nov 10, 2026) shows a real team hitting this exact design problem live, and the building blocks that would have required bespoke research two years ago — token-budget accounting (`ctxbudgeter`) and provenance hash-chaining with a blocking policy engine (`Provena`) — now exist as separate, usable open-source components. The gap isn't invention, it's integration: nobody has combined these into the single opt-in-escalation governance layer the IrisVeil team is describing, which is exactly the kind of assemblable-today gap this pipeline looks for.

## Skill Angle

A companion skill that, given a description of an agent's current retrieval setup (quote-grounded, generic RAG, or none) and its risk profile, drafts a concrete escalation policy: trigger conditions, a recommended context-budget cap, and a provenance schema the team can wire into their own pipeline. This differs from the project itself — the project is the runtime middleware that enforces the policy at request time; the skill is a one-shot design/review aid that produces the policy spec a team would hand to an engineer (or feed straight into the project's config) before any infrastructure gets built.

## MVP Sketch

A Python/TS middleware wrapper around one open web-search API (e.g., Tavily) and one agent framework (LangChain or a bare verification-bot harness): enforce a token-budget cap using existing token-counting libraries, tag each retrieved source with provenance metadata, log every escalation decision and budget spend to a hash-chained SQLite log. Validate against ~50 synthetic verification queries split between "first-party sufficient" and "needs escalation," measuring provenance-chain completeness and budget adherence. Buildable in 2–4 weeks by 1–2 people; multi-retriever support is a fast-follow.

## Risks & Open Questions

- Thin originating evidence — a single GitHub issue with 2 reactions — risks this staying a bespoke pattern for one project rather than a generalizable gap.
- Risk of being seen as "just a LangChain callback" or an observability-tool feature rather than a standalone product; differentiation against generic tracing/observability tooling needs to be sharp.
- The escalation-trigger policy itself ("when is first-party evidence insufficient?") is a domain-specific judgment call that may resist one-size-fits-all defaults.
- `ctxbudgeter` or `Provena`'s own maintainers could combine their two tools directly, closing this gap faster than a new entrant could.
- Unclear willingness to pay: teams might build a one-day in-house version rather than adopt infra for this — needs validation before over-building.
