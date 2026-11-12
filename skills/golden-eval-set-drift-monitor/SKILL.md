---
name: golden-eval-set-drift-monitor
description: Audits whether an LLM/agent product's golden eval set still represents current production traffic, by comparing a pasted golden-set export against a pasted production-query sample and surfacing uncovered intent clusters plus candidate new golden-set examples. Use when a CI eval gate keeps passing but users are complaining, ahead of a quarterly eval review, or after a product pivot.
---

# Golden Eval-Set Drift Monitor

## When to use this
Reach for this when a team maintaining a fixed "golden" eval set for an LLM or agent product needs a one-time answer to "does our eval set still look like what users are actually doing" — typically:
- CI eval scores keep passing but real users are hitting failure modes the eval set never tests.
- A product pivot, new feature, or new user segment launched since the golden set was last refreshed.
- A scheduled quarterly/release-gate review of the eval set's relevance.
- Someone asks "when did we last update our golden set" and nobody has a good answer.

This is a one-shot audit, not a running service — it does not set up monitoring infrastructure, schedule anything, or modify CI. It produces a report a human reads and acts on.

## Inputs
**Data source**: Manual — the user pastes or uploads (1) their current golden eval set (a list of eval examples: query/prompt text, and ideally expected output or task label, as CSV/JSON/JSONL/markdown table) and (2) a sample of recent production queries or traces (same formats; ideally 100+ rows from the last 1–4 weeks, randomly or chronologically sampled — not a filtered error log). No live API, database, or observability-platform connection is used or required.

Required:
1. Golden eval set export (any size, but note the count).
2. Production traffic/query sample (flag if under ~100 rows or drawn from a single day — see Guardrails).

Optional:
3. Known intent/category labels, if the team already tags production traffic.
4. Volume/frequency counts per production row, if the export is deduplicated (helps weight cluster size estimates).

## Procedure
1. **Parse both inputs.** Count golden-set examples (N_golden) and production sample rows (N_prod). State both counts in the output up front.
2. **Cluster the production sample by intent/task**, using semantic judgment (not a vector-math pipeline) — group rows into 5–15 natural-language-named clusters (e.g., "refund status lookup", "multi-leg itinerary replanning", "ambiguous follow-up with no prior context"). Estimate each cluster's share of the sample by row count (or weighted by frequency counts if provided).
3. **For each production cluster, check golden-set coverage**: does at least one golden-set example closely match this cluster's task shape and intent? Classify each cluster `Covered`, `Partial` (golden set touches the topic but misses a key variant — e.g., covers single-leg but not multi-leg), or `Uncovered`.
4. **Compute an overall coverage read**: the percentage of the production sample falling in `Partial` + `Uncovered` clusters. This is a qualitative estimate, not a statistical divergence score — say so explicitly in the output.
5. **Select candidate additions**: for each `Uncovered` or `Partial` cluster, pick 2–3 actual rows from the production sample (quote them verbatim — never invent example text) that best represent the gap, and state why each would improve coverage.
6. **Never recommend removing or editing existing golden-set entries** — flag staleness if an entry looks clearly obsolete, but leave the removal decision to a human.
7. **Flag data-quality caveats** explicitly if the production sample is small, single-day, or looks pre-filtered (e.g., all rows are error cases) — state that the coverage read is lower-confidence and why.

## Output format
A single markdown report with these sections, in order:

```
# Golden Eval-Set Drift Audit

**Golden set size**: N_golden examples
**Production sample size**: N_prod rows (date range / source, if known)
**Overall coverage read**: X% of the production sample falls in Partial/Uncovered clusters — [LOW / MEDIUM / HIGH] drift concern
**Method**: qualitative LLM clustering, not an embedding-space statistical divergence score — treat as a triage signal, not a CI-grade metric.

## Cluster breakdown
| Cluster | Est. % of sample | Coverage | Notes |
|---|---|---|---|
| ... | ... | Covered/Partial/Uncovered | ... |

## Candidate additions to the golden set
1. **[Cluster name]** — "<verbatim production example>" — why: <reason>
2. ...

## Caveats
- <sample-size / time-window / pre-filtering caveats, if any>
```

## Guardrails
- Never fabricate a production example, golden-set example, cluster, or percentage that isn't directly derivable from the pasted input — if the input is ambiguous, say so instead of guessing.
- Never present the coverage percentage as a rigorous statistical divergence metric (no claiming Jensen-Shannon divergence, MMD, or a p-value) — this skill does qualitative semantic clustering by an LLM, not vector-space math; state that plainly in every report.
- Never recommend deleting or rewriting existing golden-set entries — only ever propose additions. Staleness flags are observations, not actions taken.
- Never skip the data-quality caveat when the production sample is under ~100 rows, spans under a week, or looks like it was pre-filtered to errors/complaints only — a biased or thin sample produces a misleading coverage read, and the report must say so rather than present false confidence.
- Never treat this one-shot audit as equivalent to a running drift-monitoring service — it is a point-in-time check; if asked to "monitor this ongoing" or "run this nightly," say that's a different, infrastructure-level project outside this skill's scope.
- Cap the cluster table at ~15 rows; if production traffic is far more diverse than that, group into a coarser pass and note that a deeper second pass is available on request rather than dumping an unreadable wall of clusters.
