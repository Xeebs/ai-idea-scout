---
name: rag-failure-stage-attribution-classifier
description: Given one failed RAG (retrieval-augmented generation) interaction — the query, what got retrieved, and the generated answer — classifies whether the failure originated in retrieval, chunking, or generation, with quoted evidence and a confidence level. Use when someone pastes a single bad RAG answer and asks "why did this happen" or "which part of my pipeline is broken" rather than a full evaluation-framework build.
---

# RAG Failure Stage Attribution Classifier

## When to use this
Someone has exactly one bad answer from a RAG system — a wrong, incomplete, or unsupported response — and wants to know, right now, whether the root cause was retrieval (the right passage was never fetched), chunking (the right document was fetched but the answer-bearing text was split across a chunk boundary), or generation (the model had everything it needed and still answered wrong). This is a single-incident triage call, not a build-an-evaluation-framework exercise — use it before deciding whether to re-tune the retriever, re-chunk the corpus, or re-prompt the generator for this one case.

Do not reach for this when the user wants ongoing/batch monitoring across many failures, a full retrieval-metrics evaluation (Recall@k, MRR, NDCG), or help designing a chunking strategy from scratch — those are broader RAG-evaluation tasks this skill deliberately does not attempt.

## Inputs
**Data source**: Manual — the user pastes the failed interaction directly into the conversation. No connector, trace-export API, or corpus access is read; this skill only ever sees what gets pasted. (A connected version that pulls traces automatically from LangSmith/Langfuse for continuous batch monitoring is a separate, larger system — out of scope here.)

Required, for every run:
1. **The query** the user asked the RAG system.
2. **The retrieved chunks** that were actually passed to the generator — each with its text, and (if the user has it) its source document name/identifier and its position within that document (page, section, paragraph number, or character offset).
3. **The generated answer**, verbatim.

Strongly recommended, because they directly gate which checks can run at meaningful confidence:
4. **The expected/correct answer, or the exact passage that should have answered the query** — if the user already knows it (they found it manually afterward, or it's in a known doc). Without this, the retrieval check is a judgment call, not a verified miss.
5. **The chunk(s) immediately before and after each retrieved chunk** in their source document — needed to detect an answer split across a chunk boundary. Without this, the chunking check cannot run and must be reported as unavailable, not guessed.

If only the query, chunks, and answer are provided (no gold passage, no adjacent chunks), the classifier still runs but must downgrade confidence and say explicitly what additional input would sharpen the verdict — never silently claim a confidence level the inputs don't support.

## Procedure
1. **Parse the four/five inputs.** If the generated answer or the retrieved chunks are missing entirely, stop and ask for them — there is no verdict without both.

2. **Step A — Sufficiency check** (was the information the generator needed actually inside the retrieved chunks?):
   - If a gold passage or expected answer was provided: search for its key facts verbatim or paraphrased inside the retrieved chunk text.
     - Found nowhere in the retrieved chunks → sufficiency FAILED. Proceed to Step B to determine if this is a clean retrieval miss or a chunking split.
     - Found inside a retrieved chunk → sufficiency CONFIRMED. Skip to Step C.
   - If no gold passage was provided: make a best-effort judgment on whether any retrieved chunk plausibly contains information relevant to the query. Label this judgment confidence LOW and state explicitly that, without ground truth or corpus access, a true retrieval miss cannot be distinguished from "the answer simply isn't in this corpus."

3. **Step B — Chunking-boundary check** (only when sufficiency failed in Step A, or whenever adjacent-chunk text was provided):
   - Inspect where each retrieved chunk starts/ends relative to its document position. Look for a chunk ending mid-sentence, mid-list-item, or mid-table-row exactly where the needed fact would plausibly continue.
   - If adjacent chunks were provided: check whether the missing fact appears in the chunk immediately before or after a retrieved one.
     - Missing fact found in an adjacent (non-retrieved, or retrieved-but-separated) chunk, with a visible truncation point → **CHUNKING FAILURE** (right document, wrong cut point) — report even if Step A looked like a retrieval miss; it supersedes "retrieval" once a boundary split is confirmed.
     - No adjacent chunks provided and no truncation visible in the retrieved chunk text itself → chunking check is UNAVAILABLE, not negative. Say so; do not report "no chunking issue found" when the check never actually ran.
   - If no truncation pattern is visible and the fact is absent from both retrieved and adjacent chunks → **RETRIEVAL FAILURE** stands from Step A.

4. **Step C — Generation/claim-support check** (only when sufficiency was CONFIRMED in Step A — the needed information was present in what was retrieved):
   - Break the generated answer into its individual factual claims.
   - For each claim, check it against the retrieved chunk text ONLY — never against outside/world knowledge, since that is not what the generator was given.
   - Classify each claim: Supported (stated in a retrieved chunk), Unsupported (not found anywhere in the retrieved chunks), or Contradicted (retrieved chunks state something different).
   - Any Unsupported or Contradicted claim, given confirmed sufficiency → **GENERATION FAILURE**.
   - If every claim is Supported but the answer still doesn't match the expected answer, the context was textually present but may have been ambiguous or incomplete in substance — report this as a borderline case, not a clean generation failure (see guardrails).

5. **Step D — Synthesize the verdict.** Pick exactly one of: `RETRIEVAL FAILURE`, `CHUNKING FAILURE`, `GENERATION FAILURE`, `MIXED` (name the two contributing stages, e.g. "chunking (primary) + generation (contributing)" — only when evidence genuinely supports both), or `INSUFFICIENT INPUT TO DETERMINE` (when the provided material cannot support any of the above, e.g. no gold passage AND no adjacent chunks AND the answer looks plausible on its face). Attach a confidence level (HIGH / MEDIUM / LOW) tied to which optional inputs were actually provided, not to how confident the prose sounds.

6. **Write the report** in the format below. Every evidence line must be a direct quote from the pasted material — never paraphrase evidence into something more conclusive than what was actually pasted.

## Output format
```
## Verdict: <RETRIEVAL FAILURE | CHUNKING FAILURE | GENERATION FAILURE | MIXED | INSUFFICIENT INPUT TO DETERMINE>
Confidence: <HIGH | MEDIUM | LOW> — <one line on why, tied to which optional inputs were/weren't provided>

## Evidence
- <quoted chunk text, quoted answer claim, or quoted gold-passage fact that supports the verdict>
- <additional evidence lines as needed>

## Checks Run
- Sufficiency check: <ran with gold passage / ran as best-effort judgment / not applicable>
- Chunking-boundary check: <ran with adjacent chunks / unavailable — no adjacent chunks provided>
- Claim-support check: <ran against N claims / not applicable — sufficiency failed>

## Recommended Next Step
<one concrete line, e.g. "Re-chunk around the pricing table in doc X so rows aren't split across the 512-token boundary" or "Add explicit quote-grounding instruction to the generation prompt" or "Cannot recommend a fix with confidence — paste the adjacent chunks or the correct passage to sharpen this verdict.">
```

## Guardrails
- Never quote or paraphrase chunk text, claims, or gold-passage facts that weren't actually in the pasted input — every evidence line must trace to something the user provided.
- Never report `RETRIEVAL FAILURE` at HIGH or MEDIUM confidence without a gold passage or expected answer having been provided — absent that, it's a LOW-confidence judgment call and must say so.
- Never report the chunking-boundary check as "no issue found" when adjacent chunks weren't provided — report it as unavailable and name exactly what input (the neighboring chunks) would let it run.
- Never score generation claims against outside/world knowledge — only against the exact retrieved chunk text that was pasted in, since that's what the generator actually saw.
- Never force a single clean label when the evidence is genuinely mixed, absent, or contradictory — use `MIXED` or `INSUFFICIENT INPUT TO DETERMINE` and state exactly what additional input would resolve it.
- This is a single-incident, one-shot classifier over whatever was pasted — never imply it ran a live re-retrieval against the user's actual corpus, called any API, or evaluated anything beyond the one interaction given.
