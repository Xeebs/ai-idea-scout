# Score Bridge: A Translation Adapter Between Vendor Eval-Score Schemas and the OTel GenAI Standard

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability-ii.md · P7
- **Maturity verdict**: PARTIAL — the OpenTelemetry GenAI attributes registry does define canonical eval-score fields (`gen_ai.evaluation.name`, `gen_ai.evaluation.score.value`, `gen_ai.evaluation.score.label`, `gen_ai.evaluation.explanation`) and a proposed `gen_ai.evaluation.result` event (per a TrueFoundry write-up), but that spec moved to a separate repo in June 2026 with no official release as of August 2026, while vendors (Datadog's `ml_obs.evaluation.*`, Dash0/Bedrock AgentCore) already ship their own schemas on top — a real standardization effort exists but is unstable/unreleased, leaving a genuine translation gap today.
- **Format**: BOTH — a running translation layer sitting in the telemetry pipeline, actively converting live eval-score emissions, is infrastructure; a one-time "map our current vendor schema to canonical GenAI attributes" audit is a separable task.
- **Data Sources**: CONNECTED — reads from and writes to named observability vendors' APIs/SDKs for eval-score data (Datadog's LLM Observability API, Arize's API, Langfuse's API, New Relic's AI Evaluation preview API — each a mature, documented platform, though the specific eval-score sub-schemas are newer and less stable than core tracing), translating between each vendor's native shape and the draft OTel GenAI evaluation attribute set.

## The Gap
Tracing itself converged on OpenTelemetry/OpenLLMetry as a standard in 2026 (reinforced by ServiceNow's acquisition of Traceloop/OpenLLMetry), but eval-score attachment to traces did not follow — Datadog documents its own `ml_obs.evaluation.count`/`ml_obs.evaluation.score` fields (GitHub PR #40934, 2026-10-22), and separately, Arize, Langfuse, and New Relic's new AI Evaluation preview each define their own eval-metric shape. The OTel GenAI SIG's own canonical attributes for this exist on paper but moved to an unreleased separate repo mid-2026, so there's no stable target to converge on yet — eval data doesn't travel portably between observability backends the way trace spans now do.

## The Project
A translation/adapter library that normalizes eval-score emissions between whichever vendor schema a team currently uses (Datadog, Arize, Langfuse, New Relic) and a documented intermediate canonical schema closely tracking the draft OTel GenAI evaluation attributes, so a team can emit eval scores once and have them land correctly in whichever backend(s) they use — or migrate from one vendor to another — without hand-rewriting every eval-score emission call site.

Components: per-vendor schema adapters (ingest/emit) for Datadog, Arize, Langfuse, New Relic to start; a canonical intermediate schema tracking the draft OTel GenAI eval attributes, versioned so it can be updated when the spec stabilizes; a migration CLI that replays a historical eval-score export from one vendor's shape into another's.

## Tangible Impact
**Population**: Observability/platform engineering teams running LLM products who use more than one eval/observability backend simultaneously (e.g., Datadog for infra plus a specialized LLM eval tool), or who are actively evaluating a vendor switch — a narrower but real population given that multi-vendor observability setups and vendor re-negotiations are common at the 50-500 engineer company stage, where observability spend is big enough to shop around but eval-score re-instrumentation cost is a real deterrent to actually switching.
**Mechanism**: Today, eval-score schemas are vendor-locked by design — switching from Datadog's LLM Observability to Arize, or running both side by side for a comparison period, means rewriting every eval-score emission call site to match the new vendor's field names and shapes. A canonical-schema adapter means a team emits scores once in the intermediate format and the adapter handles the per-vendor translation, turning a multi-week re-instrumentation project into a config change.
**Measure**: (1) time to add or switch an eval-score destination vendor, from weeks of re-instrumentation to hours of adapter configuration, on a pilot team's real codebase; (2) percentage of a vendor's native eval-score fields that round-trip losslessly through the canonical schema without data loss; (3) number of teams able to run a side-by-side vendor comparison (the same eval scores visible in two backends simultaneously) without duplicating instrumentation code.

## Why Now
The draft OTel GenAI evaluation attributes already exist as a documented (if unreleased) target, and the vendor schemas it needs to bridge (Datadog, Arize, Langfuse, New Relic) are all stable, documented, mature APIs today — the canonical target is a moving spec, but bridging between already-shipped vendor schemas doesn't need to wait for that spec to finalize.

## Skill Angle
Trigger: a team is evaluating a vendor switch or multi-vendor setup for eval/observability and wants to know how much re-instrumentation it would actually require. Inputs: a sample of their current eval-score emission code or exported data in their current vendor's schema, and the target vendor(s) they're considering. Output: a field-by-field mapping report showing what translates cleanly, what's lossy, and a drafted adapter config to bridge the two. The skill is the one-time migration-feasibility assessment; the project is the adapter that runs continuously once a team adopts it.

## MVP Sketch
A Python library with pluggable adapter classes for Datadog and Langfuse (the two most documented eval-score APIs) that both read a native eval-score payload into the canonical intermediate schema and write the canonical schema back out to either vendor's format, plus a CLI to replay a historical export. Experiment: take one pilot team's real Datadog eval-score export, round-trip it through the canonical schema into Langfuse's format, and confirm the scores and metadata land correctly and queryably in both backends. 3 weeks, 1-2 people.

## Risks & Open Questions
- The draft OTel GenAI spec could stabilize and vendors could converge on it natively within the next year or two, which would make a third-party bridge a temporary stopgap rather than a durable product — worth tracking spec progress closely.
- Vendor APIs for eval-score fields specifically (as opposed to core tracing) are newer and more likely to change shape without notice, risking adapter breakage that core-tracing bridges (which follow the stable OTel spec) don't face.
- The addressable population (teams running genuinely multi-vendor eval setups, or actively switching) is smaller than the broader observability market, since most teams pick one vendor and stay.
- A well-resourced vendor could add native import/export for competitors' schemas as a sales tactic, undercutting a neutral third-party bridge's value proposition.
