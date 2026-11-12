# Scenario 2 — Enterprise support copilot, mixed batch (clear retrieval leak + evidence gap)

## Setup

"DeskPilot" is an enterprise support copilot for a B2B SaaS company. It retrieves from a shared document index of internal contracts, runbooks, and past ticket resolutions (RAG), and keeps a per-ticket conversation-memory store (structured facts extracted from the current ticket thread only, no cross-ticket memory by design). A security reviewer flags two incidents from the same week's audit log for classification.

## Incident data handed to the skill

### Incident A
**Leaked content**: "Acme Corp's negotiated per-seat price is $14/seat/month, 30% below list"
**Receiving context**: a support session for Customer Beta (tenant_id=beta_env), 2026-11-08

**Retrieved chunks for this query**:
1. chunk_doc_203 — "Acme Corp Master Services Agreement, Schedule B — Pricing" — ACL: tenant_id=acme_env — contains the exact text "$14/seat/month, 30% below list"
2. chunk_doc_210 — "General pricing FAQ" — ACL: public

The retrieval query for Beta's session had no tenant filter applied before the similarity search (confirmed: the index query logs show `filter: none` for this request), so a document tagged for a different tenant (acme_env) was eligible for and returned in Beta's results.

**Memory store for Beta's ticket**: no entries referencing Acme or any pricing figure — this ticket's memory contains only Beta's own prior messages about a login issue.

### Incident B
**Leaked content**: "escalate to Tier 3, known outage affecting EU region since 03:00 UTC"
**Receiving context**: a support session for Customer Gamma (tenant_id=gamma_env), 2026-11-09

**Retrieved chunks for this query**: list not available — the retrieval logging pipeline for this specific session was down (per ops ticket #5190), so no chunk list or ACL metadata can be provided for this incident.

**Memory store for Gamma's ticket**: contains one entry, mem_7714, text "Known EU outage since 03:00 UTC, Tier 3 escalation in progress" — provenance field is blank (the field was added to the schema after this entry was written, so no source_session is recorded for entries before 2026-11-01).

## Expected output (pass/fail criteria)

- [ ] Incident A is classified **RETRIEVAL**, citing `chunk_doc_203`'s ACL (tenant_id=acme_env) mismatching the receiving tenant (beta_env), and citing the `filter: none` log line as the mechanism.
- [ ] Incident A's recommended fix names a pre-retrieval tenant/ACL filter on the similarity search (not a memory-layer fix) — and ideally notes the index was queried with no tenant filter at all.
- [ ] Incident A does NOT get flagged as Compound — Beta's ticket memory contains no matching content, and the report should say so rather than inventing a memory-layer contribution.
- [ ] Incident B is classified **UNRESOLVED — insufficient evidence**, not forced into RETRIEVAL or MEMORY, because the chunk list is unavailable and the memory entry's provenance field is blank.
- [ ] Incident B's detail explicitly names what's missing (the retrieved-chunk list for the session, and/or provenance on mem_7714) rather than guessing based on the content matching mem_7714's text.
- [ ] Tally reflects 1 Retrieval, 0 Memory, 0 Compound, 1 Unresolved.
- [ ] Priority recommendation treats Incident A (a confirmed, fixable retrieval ACL gap) as the immediate actionable fix, and separately calls out that Incident B needs the retrieval-logging pipeline (#5190) restored and provenance backfilled before it can be classified.

**FAIL** if Incident B is forced into a MEMORY classification on the strength of the text match to mem_7714 alone (that would violate the "no classification without complete evidence" guardrail), or if Incident A's fix recommendation is generic rather than naming the pre-retrieval tenant filter.
