---
name: regulated-orchestration-pattern-benchmark
description: Recommends which multi-agent LLM orchestration pattern (sequential, parallel, hierarchical, or reflexive) to use for a regulated document-extraction pipeline, grounded in published cost-accuracy benchmark data, before a team commits engineering time to building or benchmarking one from scratch.
---

# Orchestration Pattern Advisor for Regulated Document Extraction

## When to use this
A team is about to build (or is reconsidering) an LLM pipeline that extracts structured fields from a regulated or compliance-sensitive document type — financial statements, healthcare prior-authorization forms, insurance claims, legal contracts, loan files, KYC/AML documents — and needs to choose between sequential, parallel, hierarchical, or reflexive (self-correcting) multi-agent orchestration before investing weeks in building the pipeline or running their own 100+ configuration benchmark. This is a one-shot advisory pass, not a replacement for actually running a benchmark on the team's own corpus — it exists to give an evidence-informed starting point instead of a guess.

## Inputs
**Data source**: Manual — the user pastes/describes: (1) the document domain and type (e.g. "healthcare prior-authorization forms", "commercial loan agreements"), (2) the target field list with which fields are high-stakes vs. low-stakes to get wrong, (3) a small labeled sample — 3 to 15 real or representative documents with ground-truth field values, pasted as text or described field-by-field, and (4) any known cost/latency/accuracy constraints (e.g. "must stay under $0.05/doc", "needs sub-5-second turnaround", "false negatives on denial-relevant fields are unacceptable"). There is no connector here — no API or MCP integration currently reaches into a document-management or claims system to pull this automatically; everything is hand-provided by the requester for this pass.

## Procedure
1. **Classify domain match.** Determine whether the document type is financial-document extraction (direct benchmark coverage from Kulkarni, arXiv 2603.22651) or an adjacent regulated domain — healthcare, legal, insurance, KYC/AML (no direct benchmark; recommendation will be extrapolated and must be flagged as such).
2. **Characterize the field set.** Count fields, classify each as simple key-value lookup vs. long-form/reasoning-dependent extraction (e.g. "does this clause trigger an indemnification obligation" is reasoning-dependent; "policy number" is not). Note whether fields are independent of each other (favors parallel fan-out) or depend on earlier extracted values (favors sequential or hierarchical).
3. **Characterize error-cost asymmetry.** For each high-stakes field, determine whether a false negative (missed/wrong value silently accepted) or a false positive (flagged for human review unnecessarily) is costlier in this domain. A missed denial-trigger field in a prior-auth form is a different risk profile than an extra manual review step — this asymmetry, not raw accuracy, drives the recommendation for regulated domains specifically.
4. **Map against the benchmark reference table** (below) to produce a ranked recommendation with a stated Pareto rationale.
5. **Set a confidence level**: HIGH only if the domain is financial-document extraction (direct benchmark match); LOW-MODERATE for any other regulated domain, with an explicit note that the cost-per-field metric's cross-domain transfer is an open research question, not a proven fact.
6. **Always propose a lightweight validation step** using the user's own labeled sample: run the current/baseline pattern and the top recommendation on just those 3–15 documents and compare field-level accuracy and estimated cost before committing to the recommendation at production scale.

### Benchmark reference table (source: Kulkarni, arXiv 2603.22651 — financial-document extraction, 25 field types, 5 models, 500 configurations)
| Pattern | Field-level F1 | Relative cost vs. sequential baseline | Best for |
|---|---|---|---|
| Sequential | baseline | 1.0x | Low-stakes fields, tight cost budget, fields with strict order dependency |
| Parallel fan-out | ~baseline, faster wall-clock | ~1.0–1.2x | Independent fields, latency-sensitive extraction |
| Hierarchical (supervisor-worker) | 0.921 | 1.4x | Best accuracy-per-dollar point on the Pareto frontier; default recommendation when stakes are moderate-to-high |
| Reflexive (self-correction) | 0.943 | 2.3x | Highest-stakes fields where missed/wrong values are unacceptable and budget allows it |
| Hybrid (caching + model routing + adaptive retry) | ~0.93 (recovers ~89% of reflexive's accuracy gain over sequential) | 1.15x | High-stakes fields under a real cost ceiling — usually the pragmatic choice over pure reflexive |

## Output format
A short recommendation memo with these sections, in this order:
1. **Recommendation** — the single pattern (or hybrid combination, e.g. "hierarchical for routine fields, reflexive only on the 3 highest-stakes fields") recommended for this document type.
2. **Rationale** — 2-4 sentences tying the recommendation to the field characterization, error-cost asymmetry, and the benchmark table row(s) used.
3. **Confidence** — HIGH (direct finance-domain benchmark match) or LOW-MODERATE (extrapolated to a non-finance regulated domain), stated explicitly, never omitted.
4. **Validation plan** — the exact lightweight experiment to run on the user's own 3-15 document sample before trusting this at production scale.
5. **Caveats** — anything that could invalidate the recommendation (e.g. "if your fields are mostly reasoning-dependent rather than key-value, lean more toward reflexive than this table alone suggests").

## Guardrails
- Never state or imply that benchmark numbers exist for a non-financial domain — they do not. Any recommendation for healthcare, legal, insurance, or other non-finance regulated domains must be explicitly labeled an extrapolation from the finance-only study, with confidence set to LOW-MODERATE.
- Never fabricate benchmark figures beyond the table above. If asked for numbers outside what Kulkarni reported, say so plainly rather than inventing a plausible-sounding figure.
- Never skip the error-cost asymmetry step (Procedure step 3) — recommending by raw accuracy alone defeats the purpose of a regulated-domain advisor, where the cost of a false negative and false positive are rarely symmetric.
- Never present this one-shot recommendation as a substitute for actually benchmarking on the team's own corpus at production scale — always include the validation-plan step, and say explicitly that it is the next required step, not optional polish.
- Never recommend reflexive or hybrid patterns by default for low-stakes, cost-sensitive, independent-field extraction — match the pattern to the actual stakes and field characteristics gathered in steps 2-3, not to whichever pattern has the highest accuracy in the table.
