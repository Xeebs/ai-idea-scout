# Scenario 1 — Datadog to Langfuse, considering a side-by-side pilot

## Setup
A platform team at a ~150-engineer company runs their LLM product's core traces through Datadog APM already, and recently started emitting eval scores for a RAG assistant using Datadog's LLM Observability SDK. Leadership wants to pilot Langfuse for eval/dataset tooling specifically (better prompt-versioning UX) without ripping out Datadog, so both backends need to show the same eval scores during the pilot.

## Input given to the skill

Current vendor: Datadog

Sample (actual code as currently shipped):
```python
from ddtrace.llmobs import LLMObs

LLMObs.submit_evaluation(
    span_context={"span_id": span_id, "trace_id": trace_id},
    label="faithfulness",
    metric_type="score",
    value=0.82,
    ml_app="rag-assistant",
    tags={"model": "claude-sonnet-5", "dataset": "support-tickets-eval-v3"},
)

LLMObs.submit_evaluation(
    span_context={"span_id": span_id, "trace_id": trace_id},
    label="hallucination_flag",
    metric_type="categorical",
    value="fail",
    ml_app="rag-assistant",
)
```

Target vendor: Langfuse

Volume: ~4,000 scores/day across 2 metrics, no backfill needed — new scores going forward only.

## Pass criteria

- [ ] Report lists the fields actually present in the sample verbatim: `span_id`, `trace_id`, `label`, `metric_type`, `value` (both as numeric 0.82 and categorical "fail"), `ml_app`, `tags.model`, `tags.dataset` — does not invent fields not shown (e.g. does not claim an `explanation`/`comment` field exists in this sample, since none was given).
- [ ] Maps `label` -> `eval.name`, the numeric `value` -> `eval.score.value`, the categorical `value` -> `eval.score.label`, `span_id`/`trace_id` -> `eval.target_ref`, and routes `ml_app`/`tags.*` to `eval.metadata` (no first-class canonical slot).
- [ ] Correctly identifies that Datadog has no first-class `explanation` field in this sample and does not claim a CLEAN explanation mapping — since none was emitted, there's nothing to map on that field (report should either omit it or state "not present in sample, not applicable").
- [ ] On the canonical-to-Langfuse hop, maps `eval.name` -> `name`, `eval.score.value` -> `value` (dataType NUMERIC), `eval.score.label` -> `value` (dataType CATEGORICAL) and flags this as a type-branching nuance (Langfuse's single `value` field serves both score types depending on `dataType`) rather than a clean 1:1 rename.
- [ ] Produces a translation-completeness verdict (HIGH/MEDIUM/LOW) with a percentage, consistent with its own table (metadata/tags fields routed to a catch-all should pull the score down from HIGH unless justified).
- [ ] Includes a doc-verification checklist naming Langfuse's `scores` API reference and Datadog's `submit_evaluation` docs specifically (not generic "check the vendor docs").
- [ ] Produces a YAML draft adapter config with `source`/`canonical`/`target`/`transform` keys for each mapped field, explicitly labeled as a planning artifact, not executable/credentialed code.
- [ ] Gives an hours-vs-weeks effort estimate tied to the number of LOSSY/metadata-routed fields (2 metrics, few tags → should land toward the lower end, e.g. low hours to low days, not weeks) and says why.
- [ ] Does not claim to have called Langfuse's or Datadog's API, and includes the disclaimer that this is a one-time assessment from a pasted sample.

## Fail criteria (any of these sinks the scenario)
- Inventing a Datadog `explanation`/`comment` field that wasn't in the sample.
- Claiming the categorical `value="fail"` and numeric `value=0.82` map to Langfuse with zero type-handling nuance (treating `metric_type` switching as irrelevant).
- Proposing production code that actually calls `langfuse.score(...)` with live credentials instead of a declarative mapping artifact.
- Omitting the doc-verification checklist or effort estimate.
