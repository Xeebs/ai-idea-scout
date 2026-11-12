---
name: graphrag-telemetry-error-taxonomy
description: Reviews a described GraphRAG pipeline's current telemetry/error codes for collapsed or ambiguous flags (e.g. one generic "retrieval_failed_or_empty" covering a legitimate no-match, a broken retrieval, and a real outage), and drafts a team-specific reason-code taxonomy with severity/alerting guidance. Use before or after building GraphRAG observability, or when an on-call engineer can't tell from an alert whether a graph query genuinely has no answer or the pipeline is actually broken.
---

# GraphRAG Telemetry Taxonomy Review

## When to use this

Reach for this when:
- A team running a GraphRAG pipeline (microsoft/graphrag, a Neo4j-backed pipeline, LlamaIndex PropertyGraphIndex, or a custom graph-retrieval stack) has one or a small handful of generic flags for "nothing came back" or "retrieval failed," and on-call engineers can't tell from an alert alone whether the graph legitimately has no answer, retrieval broke, or there's a real outage.
- Someone is about to instrument a new GraphRAG pipeline's observability and wants a reasoned reason-code taxonomy before writing logging/alerting code, instead of inventing codes ad hoc as failures show up in production.
- A postmortem or incident review found that a specific code (e.g. `no_patterns_detected`, `empty_result`, `retrieval_failed`) was firing for multiple unrelated root causes, and the team wants that collapse named and split.

This is a **one-time design review that produces a written taxonomy and migration notes**, not working instrumentation code, not an OpenTelemetry library, and not a claim that any taxonomy here is an adopted industry standard — as of this writing no widely adopted GraphRAG-specific reason-code standard exists. If the user wants the instrumentation actually built, say so explicitly and scope that as a separate follow-on task.

## Inputs

Required — ask for anything missing rather than assuming it:
1. **Pipeline shape**: which framework or custom stack (microsoft/graphrag, Neo4j + custom query layer, LlamaIndex PropertyGraphIndex, other), and the rough stage sequence (e.g. graph construction/indexing → query parsing → traversal/community retrieval → context assembly → generation).
2. **Current instrumentation**: every reason code, error flag, or log event that exists today, in the team's own words, plus the condition(s) each one actually fires under — as specifically as the team can state it, including any known cases where the same code fired for different underlying causes.

Optional, sharpens the review:
3. Specific incidents or postmortems where a code's ambiguity caused wasted investigation time or a missed outage.
4. Current alerting/severity setup (what pages on-call vs. what's logged silently).
5. Downstream consumers of these codes (dashboards, SLO definitions, other teams).

If required input 1 or 2 is missing, proceed on what's given but mark the gap under Open Questions — never invent a pipeline architecture or a plausible-sounding set of existing codes the team didn't describe.

## Procedure

1. **Build the stage map** from what was given: list each pipeline stage in sequence and name where a failure or empty result could originate at each one (e.g. "traversal/community retrieval" can fail because the index has no matching nodes, or because the traversal budget was exceeded, or because the backing store errored).

2. **Catalog current codes** as a table: code name → stated firing condition(s) → stage(s) it maps to.

3. **Flag collapsed codes.** A code is collapsed if the team's own description shows it firing under two or more conditions that have different correct on-call responses (one is "no action, legitimate negative result," another is "investigate retrieval config," another is "page on-call, system is down"). Name the specific scenarios from the input that collapse into it — never flag a code as collapsed without a concrete example from what was given.

4. **Map each collapsed (or missing) condition onto a reference taxonomy**, adapting names to the team's existing conventions rather than forcing their naming into this list verbatim:
   - `no_pattern_in_graph` — traversal/retrieval completed successfully; the graph genuinely has no matching entity/relationship/community for this query. Legitimate negative result, no action.
   - `retrieval_matched_nothing` — the retrieval/index lookup step itself returned zero candidates before any pattern-matching logic ran (e.g. embedding search or graph index query came back empty). Possible index or config issue — investigate, don't page.
   - `retrieval_error` — an exception, timeout, or connection failure during retrieval (store unreachable, malformed query, corrupted index). Genuine system fault — page on-call.
   - `graph_construction_stale` — the graph index exists but is known out of sync with source data at query time. Data-freshness issue — investigate ingestion pipeline.
   - `traversal_budget_exceeded` — the query needed deeper/wider traversal than the configured depth/cost budget allowed, so results were truncated rather than exhaustive. Config/tuning issue, not an outage.
   - `partial_community_result` — some but not all expected subgraphs/communities were retrieved (e.g. a shard was down, a partial timeout). Degraded-mode warning — investigate, escalate if sustained.
   - `downstream_generation_error` — retrieval succeeded and returned context, but the generation step failed to produce an answer from it. Separate from retrieval entirely — don't let it masquerade as a retrieval failure.
   
   If a scenario the team described doesn't fit any of these, propose a new team-specific code rather than force-fitting it — state plainly that it's a new addition, not from the reference list.

5. **Assign severity/alert action** to every code in the recommended taxonomy: no-action/informational, investigate (ticket, not page), or page on-call — grounded in whether the condition represents a legitimate outcome, a config/data issue, or a system fault.

6. **Write migration notes**: for each collapsed code being split, name concretely where in the pipeline (which stage/function, based on the stage map) the distinguishing check needs to live to emit the correct new code instead of the old collapsed one.

7. **Write the report** (format below).

8. **Self-check before returning**: confirm every "collapsed" call cites a specific scenario the team actually described, confirm no severity/alert recommendation was assigned to a code without stating why, and confirm the report doesn't claim this taxonomy is an adopted standard anywhere.

## Output format

A single markdown report, in this order:

```markdown
# GraphRAG Telemetry Taxonomy Review — <team/pipeline name if given, else "GraphRAG pipeline">

## Stage Map
- <Stage 1>: <where failures/empty results can originate>
- <Stage 2>: ...
(as many stages as the team described)

## Current Codes
| Code | Stated firing condition(s) | Stage | Collapsed? |
|---|---|---|---|
| ... | ... | ... | Yes/No — if Yes, name the distinct scenarios it conflates |

## Recommended Taxonomy
| New code | Fires when | Replaces | Severity / alert action |
|---|---|---|---|
| ... | ... | ... | no-action / investigate / page |

## Migration Notes
- <Old code> → split into <new codes>: add the distinguishing check at <specific stage/function>, checking <the specific condition>.
(one bullet per split; omit this section's intro if no code needed splitting — say so plainly instead)

## Open Questions
What wasn't provided that would sharpen this review (e.g. pipeline framework unconfirmed, no example of a specific collapsed incident, alerting setup not described).
```

## Guardrails

- Never flag a code as "collapsed" without citing a specific scenario from the team's own description — don't assume ambiguity exists just because a code name sounds generic.
- Never claim the recommended taxonomy is an adopted OpenTelemetry semantic convention or industry standard — state plainly it's a team-specific recommendation, since no widely adopted GraphRAG reason-code standard exists as of this review.
- Never invent the team's framework, pipeline stages, or existing codes if they weren't described — list missing pieces under Open Questions instead of filling them with a generic microsoft/graphrag assumption.
- Always assign a severity/alert action to every recommended code, and always distinguish "legitimate negative result" from "system fault" explicitly — collapsing that distinction is the exact problem this review exists to fix.
- This produces a written taxonomy and migration notes only — not instrumentation code, not a deployed OTel wrapper library, and not a running alerting pipeline. Say so if the user expects more.
- If the team's description shows fewer than two genuinely distinct conditions being collapsed into one code, say that plainly — don't manufacture a taxonomy split that isn't justified by what was given.
