---
name: rag-agent-memory-leakage-benchmark
description: Classifies a suspected cross-user/cross-session privacy leak in a RAG + agent-memory system as retrieval-layer, memory-layer, compound, or unresolved, and recommends the layer-matched fix. Use this when a leak incident, red-team probe, or audit finding needs root-cause attribution before anyone starts patching.
---

# Leak Layer Classifier: Retrieval vs. Agent Memory

## When to use this

Reach for this skill the moment someone has a concrete leak incident in hand — a support ticket, a red-team probe result, or an audit finding showing that information from one user or session appeared where it shouldn't in another user's or session's response — in a system that combines document RAG with persisted agent memory (chat history summaries, vector memory, or a structured fact store). The trigger is specifically needing to know *which layer* caused the leak before anyone writes a fix, not building a full leakage test suite and not reviewing code in the abstract.

Do not use this for: general code-level memory leaks (RAM/heap), generic prompt-injection review, or systems that have only one of the two layers (pure RAG with no persisted memory, or pure memory with no document retrieval) — in a single-layer system there's nothing to disambiguate.

## Inputs

For each incident, gather and hand over:

1. **The leaked content** — the exact text or fact that surfaced where it shouldn't (a quote, a diagnosis, a contract term, a name — whatever crossed the boundary).
2. **The receiving context** — which user/session/tenant the leak appeared in, and when.
3. **What was retrieved for that query** — the list of document chunks the RAG layer actually retrieved for the query that produced the leak, each with whatever access-control metadata exists (owner, tenant, ACL tag). If this list isn't available, say so explicitly rather than skipping it.
4. **What was in the memory store for that session** — the memory entries (raw turns, summaries, vector-memory hits, or structured facts) available to the agent at the time, each with provenance if known (which user/session wrote it, when).
5. Optional but useful: the memory architecture (summarized-history / vector-memory / structured-fact-store) and whether retrieval and memory share an embedding space or index.

If any of items 3 or 4 is missing or incomplete for an incident, proceed anyway but flag that incident's classification as provisional per the Guardrails below — never invent the missing evidence.

## Procedure

Work one incident at a time, in this order:

1. **Retrieval-layer check.** Search the retrieved-chunk list for text that matches the leaked content verbatim or as a close paraphrase. If found, check whether that chunk's access-control metadata belongs to a different user/tenant than the one who received the answer. A match with a mismatched ACL (or missing ACL enforcement) → mark this incident **RETRIEVAL**.
2. **Memory-layer check.** Independently of step 1, search the memory-store contents available to the session for an entry (raw, summarized, or structured) that traces back to a different user's/session's prior interaction and contains the leaked content or the fact it's derived from. A match → mark this incident **MEMORY**.
3. **Combine.**
   - Matched in step 1 only → **RETRIEVAL**.
   - Matched in step 2 only → **MEMORY**.
   - Matched in both → **COMPOUND** (both layers independently carried the same leak; both need fixing, and fixing only one will look like a fix while the leak persists through the other path).
   - Matched in neither, because the content truly isn't traceable to any item in either list → **UNRESOLVED — not reproducible from evidence given**.
   - Matched in neither, because the required evidence (chunk list, ACL tags, or memory provenance) was missing or incomplete → **UNRESOLVED — insufficient evidence**, and name exactly which input is missing.
4. **Assign the matching fix** (never a generic "add more guardrails"):
   - RETRIEVAL → access-control-aware retrieval: enforce tenant/owner filtering before the similarity search runs (pre-filter, not post-filter), audit whether the vector index was built with per-document ACL metadata at all.
   - MEMORY → memory-write/read isolation: scope memory storage and retrieval by user/session/tenant ID, audit whether summarization or embedding steps merge content across users before it's written.
   - COMPOUND → both fixes above, called out as two separate workstreams with the shared root incident noted.
   - UNRESOLVED → do not recommend a fix; state the specific evidence needed to resolve the classification (e.g., "need the ACL tag on chunk #14" or "need provenance on memory entry written 2026-10-02").
5. **Tally and prioritize** across all incidents in the batch: count by classification, and call out which layer has more incidents (that's the fix to prioritize first) and whether any COMPOUND incidents exist (those are the highest-priority fix regardless of count, since a single-layer patch won't close them).

## Output format

A single markdown report:

```
## Leak Classification Report

| ID | Leaked content (short) | Surfaced in | Classification | Evidence | Recommended fix |
|----|------------------------|-------------|-----------------|----------|------------------|
| 1  | ...                    | ...         | RETRIEVAL       | chunk #.. ACL=.. | ... |

### Detail — Incident 1
[2-4 sentences citing the exact chunk or memory entry matched, or the exact missing input.]

### Tally
- Retrieval: n
- Memory: n
- Compound: n
- Unresolved: n

### Priority recommendation
[1-2 sentences: which layer to fix first and why, or what evidence to collect first if anything is unresolved.]
```

## Guardrails

- Never classify an incident without citing the specific chunk ID/text or memory-entry ID/text that matched. A classification with no cited evidence is invalid — use UNRESOLVED instead.
- Never force RETRIEVAL or MEMORY when evidence is missing just to give a clean answer. Missing-evidence incidents must be UNRESOLVED with the specific missing input named.
- Never recommend a generic fix ("tighten guardrails", "add more filtering") — the fix must name the specific layer and mechanism (ACL pre-filter vs. memory-write scoping).
- Never collapse a COMPOUND incident into a single-layer classification — report both and both fixes, or a team will "fix" one path and ship with the leak still live through the other.
- This skill classifies and prescribes; it does not generate synthetic leakage tests or run a benchmark sweep across memory architectures — that's a larger project, not this one-off diagnostic pass.
- Do not treat this skill's output as a compliance sign-off. It's a root-cause triage aid for engineers deciding what to patch first, not a legal or audit certification.
