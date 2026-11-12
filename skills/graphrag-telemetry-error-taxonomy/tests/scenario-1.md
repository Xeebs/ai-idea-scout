# Scenario 1 — microsoft/graphrag-based internal knowledge search, collapsed `no_patterns_detected`

## Input given to the skill

> We run microsoft/graphrag on top of a Neo4j store for an internal engineering knowledge-search tool. Pipeline: documents get chunked and entity-extracted at ingest time into the graph (graph construction), then at query time we do a local-search traversal over the graph to find matching entities/communities (traversal/retrieval), assemble the matched community summaries into context, then call our LLM to generate the answer (generation).
>
> Current instrumentation: we only have one flag, `no_patterns_detected`, which our code sets to `true` whenever the local-search step returns an empty community list. We log it and move on — no alerting on it at all today.
>
> The problem (this is the actual incident that prompted this review): last week, a Neo4j connection pool exhaustion caused the traversal query to throw a timeout exception. Our code catches all exceptions from the traversal call and, in the except block, just sets `no_patterns_detected = true` and returns an empty result — so the outage looked identical in our logs to a normal "the knowledge graph doesn't have an answer for this" case. We only found the real cause by manually checking Neo4j metrics after someone complained the search felt "broken" for 20 minutes. Separately, we also know that sometimes a query's embedding search for candidate seed entities returns zero candidates before traversal even starts (e.g. a very obscure acronym with no close embedding match) — that case also currently sets `no_patterns_detected = true`.
>
> We don't have any other codes. No severity/alerting exists for this flag at all currently.

## Pass/fail criteria

- [ ] Output identifies `no_patterns_detected` as a collapsed code citing all three scenarios described: (a) legitimate no-match after successful traversal, (b) Neo4j timeout exception caught and misreported, (c) embedding seed-search returning zero candidates before traversal.
- [ ] Output's stage map includes at minimum: graph construction, traversal/local-search retrieval, context assembly, generation — matching what was described, not inventing extra stages (e.g., should not invent a "community detection" stage as separate since the user didn't describe one as distinct from construction).
- [ ] Recommended taxonomy maps the Neo4j timeout case to a `retrieval_error`-style code with a "page on-call" or equivalent high-severity alert action (this is the exact incident that caused real downtime to go undetected).
- [ ] Recommended taxonomy maps the legitimate no-match case to a `no_pattern_in_graph`-style code with a no-action/informational severity, explicitly distinct from the error case.
- [ ] Recommended taxonomy maps the zero-seed-candidate embedding case to a `retrieval_matched_nothing`-style code (or clearly reasoned equivalent), distinct from both of the above, with an "investigate, don't page" severity.
- [ ] Migration notes name a concrete location for the fix — specifically that the except block around the traversal call needs to stop swallowing the exception into `no_patterns_detected` and instead emit the error code, and that the embedding seed-search step needs its own check before traversal runs.
- [ ] Output does not claim the taxonomy is an official OpenTelemetry or industry standard.
- [ ] Output does not fabricate pipeline stages, codes, or incidents beyond what was stated (e.g., no invented "shard" or "community partial failure" scenario — the user didn't mention sharding).
