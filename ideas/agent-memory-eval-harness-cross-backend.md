# MemBench Commons: A Practitioner-Facing, Cross-Backend Test Harness for Agent Memory

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents-ii.md · P3
- **Maturity verdict**: PARTIAL — a genuine gold-rush of attempts exists in this exact window (`ProsusAI/MemEval`, `nuk3s/memeval`, `Anupam1612/memeval`, Supermemory's "MemoryBench," MELT, Veracium, mem0's own "DolphinBench") but none has consolidated adoption or cross-backend neutrality — most are <6 months old with near-zero stars, and the one well-resourced one (mem0's) is vendor-run, not independent.
- **Format**: BOTH — the harness is a running cross-backend execution service; drafting a tailored scenario plan for a specific backend/use case is a genuinely separable one-off task.
- **Data Sources**: CONNECTED — the harness executes write/read/query scenarios directly against the memory backend under test via its own SDK/API (Mem0, Letta, Zep, Cognee, Supermemory all ship mature, documented SDKs); no cross-backend-neutral standard currently exists, which is precisely the gap.

## The Gap
A DEV Community 2026 post states plainly: "prompts have LangSmith, RAG pipelines have Ragas, and APIs have Postman, but agent memory lacks an equivalent," proposing a harness that runs standard scenarios against whichever backend a team plugs in. A NeurIPS 2026 abstract separately argues memory evaluation is "stuck in a question-answer format" and should measure the actions agents take instead. Academic benchmarks (MemoryAgentBench at ICLR 2026, MELT) are emerging as research artifacts with code/datasets but are not integrated developer tooling — the complaint is specifically about the missing practitioner-facing product.

## The Project
A pluggable test harness that runs a fixed set of standard scenarios — session persistence across a restart, duplicate-fact deduplication, fact-drift/update detection, and lifecycle/expiry (TTL) correctness — against whichever memory backend a team has adapters for, reporting a pass/fail/partial matrix instead of one self-reported leaderboard number. The novel pattern is the adapter layer plus the scenario suite itself being backend-neutral and reusable across a team's own corpus, not vendor-curated data.

Components: scenario-definition DSL; a shared synthetic + bring-your-own conversation dataset runner; adapters for Mem0, Letta, Zep, Cognee; a pass/fail/partial scoring report; a comparison matrix across tested backends.

## Tangible Impact
**Population**: Engineering teams evaluating or already running a memory backend for a long-horizon or multi-session agent (e.g., a customer-support agent maintaining a persistent user profile across sessions) — mem0's own 68.9k GitHub stars is a direct signal that thousands of teams are already plugging a memory backend into production without an independent way to validate it.
**Mechanism**: Today a team either trusts a vendor's self-reported benchmark (mem0's own DolphinBench, which the vendor itself cautions is from small runs) or validates nothing, so a fact-drift or failed-expiry bug surfaces only when a real user sees stale or contradictory data days or weeks later. A neutral, repeatable harness with standard scenarios run against the team's own conversation data catches that bug in a pre-production test run instead.
**Measure**: (1) percentage of pilot teams whose first harness run catches at least one real bug (drift, dedup, or expiry failure) before it would have reached production; (2) time to validate a candidate backend, dropping from days of ad hoc manual QA to a single repeatable suite run (target: under 2 hours); (3) number of distinct backends reaching a passing conformance result, as a measure of harness adoption and neutrality.

## Why Now
The last30days search found a concentrated gold-rush of fresh attempts (MemEval, the memeval forks, MemoryBench, MELT, Veracium) all within the same 30-day window — the raw scenario ideas and scoring approaches are freshly proven out individually, but none has assembled them into a cross-backend-neutral layer. Building that consolidation layer on top of newly-matured raw material is tractable today; it was not a well-posed problem a year ago when fewer backends existed to test against.

## Skill Angle
Given a description or API docs of a candidate memory backend and the agent's intended use case, Claude drafts a tailored scenario-test plan — which of the four standard scenarios apply, what exactly to assert, and what synthetic data to generate — that an engineer can hand off to wire up against the harness, as a one-off design aid distinct from the harness's own execution engine.

## MVP Sketch
Implement the four standard scenarios as a pluggable harness with adapters for the two most SDK-mature backends (Mem0 and Letta); run against a shared synthetic conversation dataset; publish a pass/fail/partial matrix. Validate by reproducing at least one known reported bug type (e.g., a fact-drift failure) surfaced in the digest's own search results. 3-4 weeks, 1-2 people.

## Risks & Open Questions
- The academic benchmark authors (MemoryAgentBench, MELT) could productize their own work first and absorb this niche.
- Adapter-per-backend maintenance burden grows linearly with every new backend the harness supports.
- "Standard scenarios" may need enough per-use-case customization that the universal-harness framing breaks down in practice.
- A well-resourced vendor (mem0) could ship its own neutral-looking cross-backend mode to pre-empt independent tooling, though its current benchmark is explicitly vendor-run.
