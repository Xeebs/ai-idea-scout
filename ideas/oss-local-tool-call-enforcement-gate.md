# Open Gate: A Maintained, Fully Local Open-Source Enforcement Gate for Agent Tool Calls

- **Status**: EXPLORING (promoted 2026-11-14 cycle 69: evidence density — ≥2 independent threads, shield-kya/veldt-kya/Aegis/LexShield/ShadowAudit/toolgovern-cli/agent-airlock are 7 independent OSS entrants all showing the same logging-only-enforcement-is-paid shape, plus the lone enforcement-capable cupcake going stale)
- **Date**: 2026-11-14
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-14-ai-safety-and-guardrails-in-production.md · P3
- **Maturity verdict**: PARTIAL — `eqtylab/cupcake` (303 stars, Apache 2.0, backed by Trail of Bits) compiles OPA/Rego to local Wasm and genuinely blocks/modifies/pauses agent tool calls in-process, but is stale (last push 2026-03-02, >8 months); `toolgovern-cli` (0 stars) is unproven and `agent-airlock` (18 stars) only does argument type-validation. Every actively-marketed newer entrant (Shield KYA, Veldt Labs' KYA, Aegis, LexShield, ShadowAudit) gates real enforcement behind a paid hosted backend and only logs locally for free.
- **Format**: BOTH
- **Data Sources**: CONNECTED — intercepts tool calls at the agent framework's own tool-call hook/middleware layer (e.g. MCP server-side middleware, LangChain callback handlers, or an Anthropic tool-use pre-call hook), which are mature, documented extension points already present in the major agent frameworks; no new data source needs to be invented, just a policy-evaluation layer wired into an existing hook.

## The Gap
A wave of "audit trail / gate for AI agent tool calls" OSS projects launched in the last 30 days (Shield KYA on Show HN, 2026-11-04, plus a crowded field of near-duplicates) advertise themselves as the open-source safety layer for agentic tool use — but every one's free tier only records a local, offline audit log; real blocking/human-approval enforcement requires a paid hosted workspace. The one genuine fully-local enforcement project, `eqtylab/cupcake`, is real but hasn't shipped a commit in over 8 months, leaving no maintained, actively-developed, fully-free enforcement gate for a team to adopt today.

## The Project
A maintained fork/successor to the `cupcake` approach: an OPA/Rego-to-Wasm policy compiler wired into the major agent frameworks' tool-call hooks (MCP middleware first, LangChain/CrewAI callbacks second), running entirely in-process with no network call and no hosted backend required for enforcement. It ships a small library of common policy templates (destructive-file-op gate, outbound-network-call gate, PII-field-access gate) so teams don't start from a blank Rego file, and a lightweight local dashboard showing block/allow/pause decisions for audit — closing the exact "logging-only, enforcement-paid" pattern the digest's evidence names.

## Tangible Impact
**Population**: solo developers and small startups building agentic tools who adopt free OSS safety tooling specifically because they can't justify a paid vendor backend — evidenced directly by Shield KYA's Show HN traction and the crowded field of similarly-scoped free-tier-logging-only entrants, a population in the thousands based on the volume of competing GitHub launches in this single 30-day window alone.
**Mechanism**: gives this population real local blocking/approval enforcement (not just a log they read after the fact) without requiring a paid account, directly closing the "every OSS entrant leaves enforcement as a paid add-on" gap; fewer tool calls that should have been blocked actually execute.
**Measure**: % of policy-violating tool calls actually blocked vs. logged-only (target: 100% blocked for any installed team, vs. 0% today without paying); adoption (stars/installs) relative to `cupcake`'s current 303; time from "policy written" to "enforced" (target: minutes, no deployment of a hosted backend required).

## Why Now
`cupcake`'s own staleness plus the fresh wave of November 2026 launches (Shield KYA and five+ overlapping competitors) show live, current demand for exactly this category — but the market has converged on "log free, enforce paid" as the default business model, leaving the fully-free enforcement niche open and undersupplied right when adoption interest is at a 30-day peak.

## Skill Angle
A companion skill takes a plain-English description of a safety rule a user wants enforced (e.g. "never let the agent delete files outside /tmp without confirmation") and drafts the corresponding OPA/Rego policy rule plus a test case, lowering the barrier to using the gate without requiring Rego fluency — a one-shot drafting task, separable from the always-running enforcement gate itself.

## MVP Sketch
Fork `cupcake`'s Wasm-compilation core, wire it into one framework (MCP server middleware, since that's the fastest-growing integration point) with three starter policy templates, and validate against a scripted test: an agent attempts a destructive file-delete tool call, the gate blocks it with no network call made, confirmed via a packet sniff showing zero outbound traffic during enforcement. Buildable by 1-2 people in 2-4 weeks starting from cupcake's existing codebase rather than from scratch.

## Risks & Open Questions
- Reviving a stale codebase (cupcake) carries unknown technical debt and a dependency on EQTY Labs' continued willingness to accept contributions or relicense if forked.
- Policy authoring (even with the skill's help) remains a real adoption barrier versus a vendor's polished no-code UI — the UX gap, not the enforcement gap, may be what actually drives teams to paid options.
- Strongest case this is already solved: if `cupcake` resumes active maintenance (a single new commit) before this ships, the differentiation narrows to the framework-hook breadth and starter-template library specifically.
