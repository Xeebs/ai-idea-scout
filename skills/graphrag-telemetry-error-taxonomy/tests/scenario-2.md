# Scenario 2 — LlamaIndex PropertyGraphIndex compliance search, pre-launch review with sparse/no incident history

## Input given to the skill

> We're about to launch a compliance-document search tool built on LlamaIndex's PropertyGraphIndex, backed by a managed vector store for the entity/relationship embeddings and a Postgres table holding the raw graph triples. We haven't gone to production yet, so we don't have real incidents — we're trying to get the telemetry design right before launch, per a recommendation from a review of our architecture.
>
> Pipeline stages, as far as we've built so far: (1) query comes in, we embed it and do a vector similarity search against the entity embeddings to get candidate seed nodes, (2) we expand from those seed nodes via PropertyGraphIndex's graph traversal to pull in related triples up to a configured depth of 2 hops, (3) we pass the resulting triples as context to the LLM for generation.
>
> Current instrumentation: literally nothing specific to GraphRAG yet — we only have generic LLM-call latency and token-count metrics from our existing LLM observability tool. No reason codes of any kind exist for the retrieval side today.
>
> We know from a design discussion that two things CAN happen but haven't yet: traversal depth could legitimately be capped at 2 hops when a fuller answer would need 3 hops (we chose 2 for cost reasons), and the vector similarity search could return candidates that are all below our relevance threshold, in which case we currently just use whatever is returned anyway with no code distinguishing "good match" from "below-threshold match used anyway."

## Pass/fail criteria

- [ ] Output explicitly notes under Open Questions (or equivalent) that no current codes/incidents exist yet — this is a pre-launch design review, not a review of existing collapsed codes — and does not pretend a `no_patterns_detected`-style existing flag is in use when the user said nothing specific exists.
- [ ] Output does NOT fabricate a "collapsed code" scenario from thin air — since the user described zero existing GraphRAG-specific codes, the "Current Codes" table should either be empty/state "none exist yet" rather than inventing codes, and the review correctly reframes this as a greenfield taxonomy design rather than a "collapse" review when the input doesn't support finding a collapse.
- [ ] Stage map matches exactly what was described: seed-node vector search → graph traversal/expansion (2-hop budget) → generation — without inventing a graph-construction/ingestion stage review, since the user didn't describe ingest-time instrumentation as in scope.
- [ ] Recommended taxonomy includes a code for the 2-hop traversal budget cap scenario (a `traversal_budget_exceeded`-style code) with a severity marked as tuning/config-level, not an outage.
- [ ] Recommended taxonomy includes a distinct code or explicit recommendation for the below-threshold-candidates-used-anyway case, flagging it as a quality/config concern rather than silently treating it as a success — this is the one real "ambiguity" present in the input (quietly degraded results look identical to high-confidence ones) even though no literal failing code exists yet.
- [ ] Output does not claim this taxonomy is an adopted standard.
- [ ] Output does not recommend building or installing an OpenTelemetry wrapper library — the skill's own guardrail says it produces a review/taxonomy document, not instrumentation code.
