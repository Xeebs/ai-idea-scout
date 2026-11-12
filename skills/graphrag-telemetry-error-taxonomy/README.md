# GraphRAG Telemetry Taxonomy Review

Paste this whole prompt into any AI chat tool when you need it. No other context required.

## What this does

If your GraphRAG (graph-based retrieval-augmented generation) pipeline has one or a few generic flags for "nothing came back" or "retrieval failed" — the kind of thing that fires the same code whether the graph genuinely has no answer, the retrieval step broke, or there's a real outage — this prompt reviews your described pipeline, names exactly which codes are collapsing distinct failure modes, and drafts a replacement reason-code taxonomy with severity/alerting guidance for each code.

This produces a **written review and a taxonomy table**, not working code. It does not install an OpenTelemetry library, write instrumentation for you, or claim to be an adopted industry standard — no widely adopted GraphRAG-specific reason-code standard exists today. It's a design document you then implement yourself, or hand to whoever owns the instrumentation.

## When to use it

- You're running GraphRAG in production (microsoft/graphrag, a Neo4j-backed pipeline, LlamaIndex's PropertyGraphIndex, or a custom graph-retrieval stack) and on-call can't tell from an alert whether a graph query legitimately has no answer, retrieval is misconfigured, or the system is down.
- You're about to instrument a new GraphRAG pipeline's observability and want a reasoned set of reason codes before writing logging/alerting code, instead of inventing codes ad hoc as failures show up.
- A postmortem found that one code (e.g. `no_patterns_detected`, `empty_result`, `retrieval_failed`) fired for multiple unrelated root causes, and you want that collapse named and split cleanly.

## What to hand over

Before running this, gather:

1. **Pipeline shape** — which framework or custom stack you're on (microsoft/graphrag, Neo4j + custom query layer, LlamaIndex PropertyGraphIndex, other), and the rough stage sequence: e.g. graph construction/indexing → query parsing → traversal/community retrieval → context assembly → generation.
2. **Current instrumentation** — every reason code, error flag, or log event that exists today, in your own words, and the condition(s) each one actually fires under — as specifically as you can state it, including any case you already know of where the same code fired for genuinely different underlying causes.

Optional but helpful:
3. Specific incidents or postmortems where a code's ambiguity wasted investigation time or let a real outage hide.
4. Current alerting/severity setup — what pages on-call today vs. what's only logged.
5. Who else consumes these codes (dashboards, SLOs, other teams).

If you can't provide (1) or (2) in detail, say so up front — the review will proceed on what you give it and flag the gaps instead of guessing at your architecture.

## The procedure (what the AI will do with your input)

1. **Build a stage map** from what you described: each pipeline stage in sequence, and where a failure or empty result could originate at each one.
2. **Catalog your current codes** in a table: code name, stated firing condition(s), which stage(s) it maps to.
3. **Flag collapsed codes** — a code is collapsed if it fires under two or more conditions that deserve different on-call responses (one is "legitimate no-match, no action," another is "investigate config," another is "page on-call, it's down"). Every flag will cite a specific scenario you actually described — not a guess based on the code's name sounding generic.
4. **Map each collapsed or missing condition onto a reference taxonomy**, adapted to your naming conventions:
   - `no_pattern_in_graph` — retrieval completed successfully; the graph genuinely has no match for this query. No action needed.
   - `retrieval_matched_nothing` — the retrieval/index lookup itself returned zero candidates before pattern-matching even ran. Possible index/config issue — investigate, don't page.
   - `retrieval_error` — exception, timeout, or connection failure during retrieval. Genuine system fault — page on-call.
   - `graph_construction_stale` — the graph index is known out of sync with source data. Data-freshness issue — check ingestion.
   - `traversal_budget_exceeded` — the query needed more traversal depth/cost than the configured budget allowed, so results were truncated. Tuning issue, not an outage.
   - `partial_community_result` — some but not all expected subgraphs/communities came back (e.g. a shard was down). Degraded-mode warning.
   - `downstream_generation_error` — retrieval succeeded, generation failed to produce an answer from the retrieved context. Keep this separate from retrieval failures entirely.
   
   If something you described doesn't fit this list, the review will propose a new code specific to your situation rather than forcing a bad fit — and say explicitly that it's a new addition.
5. **Assign a severity/alert action** to every recommended code: no-action/informational, investigate (ticket, not page), or page on-call.
6. **Write migration notes** — for each code being split, exactly where in your pipeline (which stage, based on your stage map) the distinguishing check needs to live.
7. **Self-check** — every "collapsed" call must trace to a scenario you actually described; no taxonomy claim is presented as an adopted standard.

## Output format you should expect

```markdown
# GraphRAG Telemetry Taxonomy Review — <your pipeline name>

## Stage Map
- <stage>: <where failures/empty results can originate>

## Current Codes
| Code | Stated firing condition(s) | Stage | Collapsed? |
|---|---|---|---|

## Recommended Taxonomy
| New code | Fires when | Replaces | Severity / alert action |
|---|---|---|---|

## Migration Notes
- <old code> → split into <new codes>: add the distinguishing check at <specific stage/function>.

## Open Questions
<what wasn't provided that would sharpen this review>
```

## Guardrails — what this will refuse to do

- It will not flag a code as collapsed without citing a scenario you actually described.
- It will not claim this taxonomy is an adopted OpenTelemetry standard or industry convention — it's a team-specific recommendation.
- It will not invent your framework, pipeline stages, or existing codes if you didn't describe them — missing pieces go under Open Questions.
- It will always assign a severity/alert action to every recommended code, and always separate "legitimate negative result" from "system fault" explicitly.
- It produces a review document, not instrumentation code, not a deployed library, and not a running alerting pipeline.
- If your description shows fewer than two genuinely distinct conditions being collapsed into one code, it will say so plainly instead of manufacturing an unnecessary split.
