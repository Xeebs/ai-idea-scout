# Scenario 2 — Commercial real estate legal/compliance team, lease + amendment corpus

## Input

**Corpus profile:**
"Our compliance team manages roughly 800 commercial lease contracts, each 40-80 pages, plus their amendments and guarantor/assignment agreements — so each 'deal' is really a base lease plus several linked documents that modify or reference it (amendments override specific clauses, guarantor agreements name the parties responsible if a tenant defaults, assignment riders govern consent when a landlord sells or a tenant subleases). Terminology is dense legal/real-estate jargon but fairly consistent across our own templates. Redundancy is low — each lease is unique — but most share boilerplate clause structure from a handful of master templates. New amendments get added periodically, not daily. Getting an answer wrong here has real legal and financial exposure, so precision matters a lot. These example queries are real questions pulled from our compliance team's internal request queue over the past month."

**Example queries (7, real/logged):**
1. "What is the current rent escalation clause for the lease at 450 Main St after the 2024 amendment?"
2. "Which guarantor is responsible if Tenant X defaults under the sublease agreement?"
3. "What's the standard notice period for lease termination?"
4. "Does the indemnification clause in the Jones Properties master lease extend to its subsidiary tenants?"
5. "What insurance coverage minimums are required under section 9?"
6. "If the landlord sells the building, which assignment clauses from the original lease and all amendments govern tenant consent requirements?"
7. "What's the force majeure definition used across our standard lease templates?"

## Pass/Fail Criteria

- [ ] **Corpus Profile** restates the base-lease-plus-linked-amendments/guarantor/assignment structure, low redundancy with shared template boilerplate, periodic (not daily) updates, and the stated legal/financial precision stakes. Notes these are real logged queries (stronger evidence than hypothetical).
- [ ] **Query Mix** classifies queries 1, 2, 4, 6 as multi-hop/relational (each requires tracing a base document plus a linked amendment, guarantor, or assignment rider) and flags at least 1, 2, 4, 6 as precision-critical given the stated legal/financial exposure. Queries 3 and 5 are tagged exact-lookup (standard clause, numbered section). Query 7 is tagged conceptual/comparison (comparing a definition across templates). Fails if the multi-hop queries (1, 2, 4, 6) are misclassified as simple exact-lookup, or if none of them are flagged precision-critical.
- [ ] **Architecture Scoring** gives Graph-RAG serious consideration given the stated interlinked entity structure (leases, amendments, guarantors, assignment riders) and the strong multi-hop signal in the query mix — and explicitly flags entity-resolution/maintenance cost in the same breath it's discussed, per this skill's guardrail. Fails if graph-RAG is dismissed with no reasoning, or recommended with no cost caveat at all.
- [ ] **Architecture Scoring** also calls for a reranker layer given the precision-critical queries, regardless of which base retriever is scored highest, and names the latency/cost tradeoff.
- [ ] **Recommendation** ties its primary pick and runner-up explicitly to this corpus's interlinked document structure and the specific queries (e.g., references the lease/amendment/guarantor chain, not generic "legal documents are complex" language). Graph-RAG and Hybrid+Reranker should each appear as either the primary or the runner-up, given the evidence — fails if the recommendation ignores the multi-hop/interlinked signal entirely and picks BM25-alone or dense-alone with no reranking as the uncontested top choice.
- [ ] **Confidence & Validation** notes the queries are real/logged (raising confidence on the query-mix read) but still recommends validating the graph-RAG entity-resolution overhead against a real sample before committing, given its cost.
- [ ] No recall@k, latency, or cost figures are presented as if measured — only heuristic reasoning grounded in the stated corpus and query characteristics.
