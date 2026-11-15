# Budget Gate: An Opt-In, Provenance-Tracked RAG Escalation Governance Layer

Most retrieval-augmented systems treat "turn on RAG" as a light switch: off means the model only sees what's in its prompt, on means it's pulling in external sources on every query. That binary works fine until the thing you're building has staked its entire credibility on *not* hallucinating — and then "on" starts to look less like a feature and more like a liability. A fact-checking agent, a compliance researcher, a due-diligence bot: the moment it reaches past its first-party, quote-grounded sources, someone needs to know exactly which external source backed which claim, and exactly how much of the model's attention got spent doing it. Almost nothing in the RAG ecosystem is built for that moment.

## The Gap

The evidence for this gap is concrete, if narrow: a GitHub issue on `YourAKShaw/irisveil` (#10, opened 2026-11-10, 2 reactions) describes a verification/fact-checking agent whose current design is deliberately *not* retrieval-augmented — it only fetches a prospect's own first-party pages and quotes them directly, precisely so it stays grounded. The team's next step, as laid out in that issue, is designing an opt-in external-source layer with per-request provenance tracking and a hard context-budget cap — not just flipping a generic retriever on.

That's a governance pattern, not a retrieval algorithm, and a search across GitHub and the wider web turned up only two close relatives, each covering one half of the problem: `ctxbudgeter` (token-budgeted context assembly with an auditable "Context Bill of Materials" and a CI risk-budget gate) handles the budget side; `Provena` (provenance hash-chaining with a policy engine that can block unprovenanced context) handles the audit side. Neither defaults retrieval to opt-in, and nothing combines provenance-tracking, context-budget-capping, and opt-in-escalation into one layer the way the IrisVeil issue describes. The gap-analyst's verdict was PARTIAL, not OPEN, for exactly this reason — the pieces exist, the assembly doesn't.

## The Project

The idea is middleware, not a new retriever: a layer that sits between an agent and whatever retrieval source it already has — a vector DB client, a web-search API like Tavily or Exa — and turns "call external RAG" into a governed, auditable decision instead of an always-on pipeline stage.

The core loop has four steps. First, a policy layer decides, per query, whether the agent's first-party or quote-grounded evidence is sufficient, or whether escalation to external retrieval is warranted. Second, if it escalates, a hard context-budget cap bounds exactly how much external content gets pulled in — no open-ended retrieval. Third, every retrieved passage gets tagged with provenance (source, retrieval timestamp, and which generated claim it actually backs) and written to an append-only audit log. Fourth, the escalation decision itself — fired or not, and why, plus the budget spent — gets logged alongside the output.

The components that make this work: a pluggable escalation-trigger policy (e.g., "first-party search returned fewer than N supporting quotes"), a token/context-budget accountant, a provenance tagger that survives all the way into the final generated response so each claim stays traceable, and a queryable audit store. The pattern underneath all of it is the inversion that makes this interesting: retrieval becomes a logged, bounded *exception*, not a default pipeline stage — the opposite orientation from almost every other RAG framework out there.

## Tangible Impact

**Population**: Teams building trust-sensitive verification and research agents — sales/prospect fact-checkers, compliance research assistants, journalism and due-diligence bots — where the product's entire value proposition rests on not hallucinating, and where adding broader coverage via external retrieval today means either skipping it (losing coverage) or bolting on generic RAG (losing the auditability that earned user trust in the first place). No reliable headcount estimate exists for this specific segment, but it spans the fast-growing set of funded AI sales-intelligence, legal/compliance research, and fact-checking startups that advertise "grounded, no-hallucination" as a core claim.

**Mechanism**: By making external retrieval an opt-in, budgeted, provenance-tracked escalation rather than an always-on pipeline, these teams can expand coverage to questions their first-party-only verification couldn't answer, while giving a reviewer, auditor, or end customer a claim-by-claim trace of exactly which external source backed each statement — preserving the auditability that distinguishes them from a generic RAG wrapper.

**Measure**: (1) % of claims in escalated responses with a complete, resolvable provenance chain (target near 100%); (2) unsupported/hallucinated-claim rate before vs. after enabling escalation on a held-out claim set (should stay flat, not rise); (3) context-budget overrun incidents per week under the cap (target ~0); (4) % of previously-refused queries now answerable once escalation is available, without exceeding budget.

## Try It

There's a companion Claude Code skill for this: [`skills/rag-escalation-provenance-budget-governor/`](../skills/rag-escalation-provenance-budget-governor/). Its own description: "Drafts a concrete, enforceable policy spec — escalation trigger conditions, a context-budget cap, and a provenance schema — for a team deciding whether/how to let a quote-grounded or no-RAG agent escalate to external retrieval. Use when a team is designing (not yet building) the rules for an opt-in, auditable retrieval-escalation layer, before any infrastructure gets written."

It's a design step, not the runtime middleware described above — it produces the spec an engineer would then build against, or feed straight into this project's config. To use it: paste the skill's `README.md` into any AI chat tool and hand it your retrieval posture, risk profile, and context-window constraints, or drop the whole `rag-escalation-provenance-budget-governor/` folder into `~/.claude/skills/` if you're running Claude Code.

Worth knowing going in: the originating evidence here is thin (one GitHub issue, 2 reactions), so this risks staying a bespoke pattern for one project rather than a generalizable gap — and there's a real chance `ctxbudgeter` or `Provena`'s own maintainers simply combine their two tools directly, which would close this faster than a new entrant could build it from scratch. It could also get dismissed as "just a LangChain callback" rather than a standalone layer unless the differentiation from generic tracing/observability tooling stays sharp.

Surfaced from `research/2026-11-13-rag-techniques-ii.md`, pattern `P1`.
