# Golden Eval-Set Drift Monitor

A one-time audit prompt for teams that maintain a fixed "golden" eval set for an LLM or agent product. Paste your golden set and a sample of recent production traffic into any AI chat tool, and it tells you whether your eval set still looks like what users are actually doing — and which specific production examples to add if it doesn't.

## When to use this

Reach for this when:
- Your CI eval score keeps passing but users are hitting failure modes your eval set never tests.
- You just shipped a pivot, a new feature, or opened up to a new user segment, and haven't touched the golden set since.
- It's time for a quarterly or release-gate review of whether the eval set is still relevant.
- Someone on the team asks "when did we last update our golden set?" and nobody has a good answer.

This is a **one-shot audit**, not a monitoring service. It does not set up infrastructure, schedule anything, or modify CI. It produces a report you read once and act on. If what you actually want is a nightly job that re-runs this automatically and alerts on drift, that's a different, infrastructure-level build — this prompt only does the point-in-time check.

## What you need to provide

**Data source: Manual.** You paste or upload two things directly into the chat — there is no live API, database, or observability-platform connection involved.

1. **Your current golden eval set** — a list of eval examples (query/prompt text, and ideally the expected output or task label) as CSV, JSON, JSONL, or a markdown table. Any size is fine.
2. **A sample of recent production queries or traces** — same formats, ideally 100+ rows pulled from the last 1–4 weeks. Sample randomly or chronologically across that window — do not hand over a filtered error log or a single day's traffic, since that will bias the result (the audit will flag this if it looks that way, but a representative sample gives you a trustworthy answer the first time).

Optional, if you have them:
3. Known intent/category labels already attached to the production rows.
4. Volume/frequency counts per row, if the production export has been deduplicated — this lets the audit weight cluster sizes correctly instead of treating each unique row as equal weight.

## The prompt

Copy everything below the line, replace the bracketed placeholders with your actual pasted data, and send it to any capable AI chat tool (Claude, ChatGPT, etc.).

---

You are auditing whether a golden eval set for an LLM/agent product still represents current production traffic. I will give you two datasets. Follow this procedure exactly:

1. Parse both datasets. Count the golden-set examples (N_golden) and the production sample rows (N_prod). State both counts up front in your report.
2. Cluster the production sample by intent or task, using your own semantic judgment — do not attempt literal vector math. Group rows into 5–15 natural-language-named clusters (for example: "refund status lookup," "multi-leg itinerary replanning," "ambiguous follow-up with no prior context"). Estimate each cluster's share of the sample by row count, weighted by frequency counts if I provided them.
3. For each production cluster, check whether the golden set covers it: does at least one golden-set example closely match that cluster's task shape and intent? Classify each cluster as **Covered**, **Partial** (the golden set touches the topic but misses a key variant, e.g. covers single-leg itineraries but not multi-leg), or **Uncovered**.
4. Compute an overall coverage read: the percentage of the production sample falling into Partial + Uncovered clusters. This is a qualitative estimate from semantic clustering, not a statistical divergence score (no Jensen-Shannon divergence, no MMD, no p-values) — say so explicitly in your report.
5. For each Uncovered or Partial cluster, select 2-3 actual rows from the production sample that best represent the gap. Quote them verbatim — never invent or paraphrase example text as if it were real input. State why each one would improve coverage.
6. Never recommend removing or editing existing golden-set entries. If an entry looks clearly obsolete, flag it as a staleness observation only — leave the removal decision to a human.
7. If my production sample is small (under ~100 rows), spans less than a week, or looks pre-filtered (e.g. all error cases or all complaints), say so explicitly and note that the coverage read is lower-confidence as a result.

Produce your report in exactly this structure:

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

Here is my golden eval set:
[PASTE GOLDEN SET HERE — CSV/JSON/JSONL/markdown table]

Here is my production traffic sample:
[PASTE PRODUCTION SAMPLE HERE — CSV/JSON/JSONL/markdown table, note the date range/source if known]

---

## Guardrails (built into the prompt, don't skip these when adapting it)

- Never fabricate a production example, golden-set example, cluster, or percentage that isn't directly derivable from the pasted input. If the input is ambiguous, the report should say so instead of guessing.
- Never present the coverage percentage as a rigorous statistical metric — it is qualitative LLM clustering, not vector-space divergence math, and every report should say that plainly.
- Never recommend deleting or rewriting existing golden-set entries — only propose additions.
- Never skip the data-quality caveat when the production sample is thin, narrow in time window, or pre-filtered to errors/complaints only.
- Never treat a one-shot report as a substitute for an ongoing monitoring system — if you want nightly drift detection, that needs to be built as actual scheduled infrastructure, not run as this prompt repeatedly by hand.
- Cap the cluster table at roughly 15 rows; if traffic is far more diverse, ask for a coarser first pass and offer a deeper second pass separately rather than dumping an unreadable wall of clusters.

## Limitations

- This produces a triage signal from LLM judgment, not a certified statistical measurement — don't cite the coverage percentage in a compliance or regulatory context without separate validation.
- Quality depends entirely on how representative your production sample is. A sample skewed toward recent error reports, a single day, or a single customer segment will produce a misleading read even though the tool will flag the caveat.
- It cannot see anything you don't paste in — it has no access to your actual logging, warehouse, or observability platform.
