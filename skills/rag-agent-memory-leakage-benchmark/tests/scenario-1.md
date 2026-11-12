# Scenario 1 — Mental-health companion app, cross-user memory leak

## Setup

"Mindly" is a consumer AI companion app. It uses a vector-memory store that keeps per-user "profile facts" extracted and summarized from past conversations, plus a document-RAG layer over a static wellness-content library (no user data in the document corpus). A user named Priya reports: during a session, the assistant said "Last time you mentioned your diagnosis of generalized anxiety disorder, how has that been?" — but Priya has never told the assistant she has any diagnosis. Support escalates this as a possible cross-user leak.

## Incident data handed to the skill

**Leaked content**: "diagnosis of generalized anxiety disorder"
**Receiving context**: Priya's session, 2026-11-10, user_id=priya_8841

**Retrieved document chunks for this query** (RAG layer, static wellness library, no per-user content):
1. chunk_wellness_12 — "Understanding anxiety: common triggers and coping strategies" — ACL: public, no owner tag
2. chunk_wellness_47 — "When to talk to a professional about anxiety" — ACL: public, no owner tag

**Memory store contents available to Priya's session** (vector-memory, profile-facts store):
- mem_9031 — text: "User has a diagnosis of generalized anxiety disorder, prefers gentle check-ins." — provenance: written 2026-10-22, source_session=user_5502 (a different user, not Priya) — a known bug ticket (#4471) notes the profile-fact extraction job was accidentally deployed without a user_id partition filter for 48 hours around that date, causing facts from multiple users to land in a shared global index.
- mem_9032 — text: "User prefers morning check-ins over evening ones." — provenance: written 2026-11-05, source_session=priya_8841 (Priya's own prior session)

## Expected output (pass/fail criteria)

An evaluator should check that the report:

- [ ] Classifies this incident as **MEMORY** (not retrieval, not compound) — the leaked diagnosis text is not present in either retrieved document chunk, but matches mem_9031 verbatim.
- [ ] Explicitly cites `mem_9031` as the matched evidence, including that its provenance (`source_session=user_5502`) differs from the receiving session (`priya_8841`).
- [ ] Does NOT flag the retrieval chunks (chunk_wellness_12/47) as implicated — they contain no user-specific or diagnosis-specific text.
- [ ] Recommended fix names memory-write/read isolation specifically — e.g., restoring the user_id partition filter on the profile-fact extraction job, auditing the 48-hour window from bug #4471 for other cross-user merges — and does NOT recommend generic "add more guardrails" or a retrieval-layer fix (document ACLs, chunk filtering).
- [ ] Tally shows 1 Memory, 0 Retrieval, 0 Compound, 0 Unresolved.
- [ ] Priority recommendation correctly identifies the memory-write isolation bug as the thing to fix, not the RAG layer.

**FAIL** if the report recommends tightening document retrieval access control, if it cites either wellness chunk as evidence, or if it produces a vague fix without naming the partition-filter bug or an equivalent memory-isolation mechanism.
