# Deploy Trail: Cross-Service Root-Cause Attribution for Agent Failures

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-11-llm-evaluation-observability.md · P4
- **Maturity verdict**: OPEN — genuine multi-channel search (GitHub + web + papers) found only discussion and partial building blocks: a 127-failure-log academic benchmark where the best attribution method identified the responsible agent only 53.5% of the time, and the finding that GenAI tracing SDKs generally don't propagate W3C Trace Context across services. No credible implementation of cross-service, cross-deploy causal attribution found.
- **Format**: PROJECT — requires cross-service trace-context propagation and a persistent deploy-change ledger; inherently runtime infrastructure.

## The Gap
On Show HN "Superlog (YC P26) – Observability that installs itself and fixes bugs" (74 points / 49 comments, 2026-05-19), user `tuo-lei` asked whether the product "can link an error to a config change made several deploys earlier, across services" — directly naming this gap against a funded, instrumented observability product. The founder's reply claimed only that the investigation agent "can access telemetry from all services," stopping short of claiming the capability. No vendor (Elastic APM, Monte Carlo, Gravitee, TrueFoundry, Diagrid) or IETF draft (draft-pei-opsawg-agentops-observability-00) demonstrates it either.

## The Project
A correlation layer that (1) requires or infers trace-context propagation across the service boundaries an agent's tool calls cross, (2) maintains a timestamped deploy/config-change ledger per service fed by CI webhooks, and (3) on a reported agent failure, walks the causal trace graph plus the deploy ledger to produce a ranked list of candidate upstream changes in the window preceding the failure — rather than just surfacing the immediate failing span, which current tools already do.

Components: deploy-event ingester (CI webhook → per-service ledger); trace-context propagation shim for services that don't natively emit it; service-dependency graph config; a ranking heuristic (recency + blast radius) over the ledger at failure time.

## Tangible Impact
**Population**: Platform/SRE teams running multi-service agent systems — an agent that calls three or more internal microservices/tools — at companies already paying for an observability product like Superlog or Datadog. A narrower slice of the broader production-agent population, but a real one: specifically the teams whose agents regress because of an *upstream* service change rather than their own prompt edits, which the Superlog thread shows even funded, fully-instrumented teams currently can't debug.
**Mechanism**: Today, diagnosing "why did my agent start failing" when the true cause is a config change in a different service several deploys back requires manual cross-team log archaeology — the 53.5%-accuracy academic baseline and the unanswered Superlog question both confirm this. The correlation layer turns that hunt into a ranked shortlist of candidate deploys, cutting the investigation from a multi-team Slack thread to a single query.
**Measure**: (1) the correct upstream change appears in the tool's top-3 ranked candidates ≥80% of the time on a labeled benchmark (vs. the 53.5% single-agent-attribution baseline); (2) median cross-team investigation time for "agent broke, cause unclear" incidents drops from days to under an hour; (3) share of such incidents resolved without looping in the upstream service's team at all.

## Why Now
OTel's GenAI semantic conventions and the 2026 IETF draft on a shared "root-cause event" vocabulary are only now giving teams a common language for this; funded players like Superlog are already collecting multi-service telemetry but have publicly admitted the gap. The building blocks exist — nobody has wired trace propagation and deploy ledgers together for this specific causal-attribution use case.

## MVP Sketch
A thin service ingesting deploy/config-change events from CI into a per-service timestamped ledger; trace-context propagation (or timestamp+dependency-graph inference where context is missing); on a reported failure, query the ledger across the agent's declared service dependencies and rank candidates by recency and blast radius. Experiment: replay 10 historical incidents from a pilot team where the true cause is already known and check whether the top-3 ranked list contains it. 4 weeks, 2 people.

## Risks & Open Questions
- A funded observability vendor (Superlog itself) could close this exact gap first — they're already building the adjacent product and are visibly aware of the ask.
- Requires cooperation from every upstream service team to emit deploy events and propagate trace context — an adoption problem as much as a technical one.
- The 53.5% baseline is for single-agent-system failure attribution, not specifically cross-service config causality — adjacent evidence, not a direct precedent for this mechanism.
- The recency + blast-radius heuristic may not generalize; a labeled benchmark may be needed earlier than planned to validate it before a full build.
