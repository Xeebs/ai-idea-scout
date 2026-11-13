# RAG Failure Stage Attribution Classifier

A portable prompt for diagnosing one bad answer from a retrieval-augmented generation (RAG) system. Paste in the query, what got retrieved, and what the model answered, and it tells you whether the failure was in **retrieval** (the right passage was never fetched), **chunking** (the right document was fetched but the answer got split across a chunk boundary), or **generation** (the model had everything it needed and still answered wrong) — with quoted evidence, a confidence level, and a one-line recommended fix.

This is for engineers triaging a single incident, not building a full evaluation framework. If a user reports a wrong answer and you need to know which part of the pipeline to fix before spending time on it, this is the tool. It works in any chat tool — no install, no connector, no access to your actual vector store or corpus. It only ever reasons over what you paste in.

## How to use it

Paste the prompt below into any AI chat tool, then paste your failed interaction underneath it. You need, at minimum:
1. The query that was asked.
2. The chunks that were actually retrieved and handed to the generator — their text, and ideally which document they came from and where in that document (page, section, or offset).
3. The generated answer, verbatim.

For a confident verdict, also include if you have them:
4. The correct answer, or the exact passage that should have answered the query (you may have found this manually after the fact).
5. The chunk immediately before and after each retrieved chunk in its source document.

Without #4 and #5 the tool still runs, but it will downgrade its confidence and tell you exactly what to paste in next to sharpen the verdict — it will not pretend to be more certain than the inputs support.

---

### The prompt

> You are diagnosing a single failed RAG (retrieval-augmented generation) interaction to determine whether the root cause was retrieval, chunking, or generation. This is a one-shot classification over exactly the material I paste in — you have no access to my actual corpus, vector store, or retriever, and must not imply otherwise.
>
> I will give you: the query, the chunks that were retrieved and passed to the generator (with source document and position where available), and the generated answer. I may also give you the correct answer/passage and the chunks adjacent to each retrieved one — use these if present, and explicitly flag when they're missing and what that costs the verdict's confidence.
>
> Do the following, in order:
>
> 1. **Sufficiency check**: If I gave you a correct answer or gold passage, search for its key facts inside the retrieved chunk text.
>    - Not found anywhere in the retrieved chunks → sufficiency FAILED, go to step 2.
>    - Found inside a retrieved chunk → sufficiency CONFIRMED, skip to step 3.
>    - If I did NOT give you a gold passage: make your best judgment on whether any retrieved chunk plausibly contains the needed information, but label this LOW confidence and say plainly that without ground truth you cannot distinguish a true retrieval miss from "the answer just isn't in this corpus."
>
> 2. **Chunking-boundary check** (run this when sufficiency failed, or whenever I gave you adjacent chunks): Look at where each retrieved chunk starts and ends. Does it cut off mid-sentence, mid-list-item, or mid-table-row exactly where the needed fact would continue? If I gave you adjacent chunks, check whether the missing fact is sitting right there in the chunk before or after a retrieved one.
>    - Missing fact found in an adjacent chunk with a visible truncation point → verdict is **CHUNKING FAILURE** (right document, wrong cut point) — this overrides a retrieval-miss read from step 1.
>    - No adjacent chunks given and no truncation visible → report the chunking check as UNAVAILABLE, not "clean." Never claim "no chunking issue" when you never actually had the adjacent text to check.
>    - No truncation pattern and the fact is absent from retrieved and adjacent chunks alike → verdict is **RETRIEVAL FAILURE**.
>
> 3. **Claim-support check** (run this only when sufficiency was CONFIRMED in step 1): Break the generated answer into individual factual claims. For each one, check it strictly against the retrieved chunk text — never against your own outside knowledge, since that isn't what the generator saw. Classify each claim Supported, Unsupported, or Contradicted.
>    - Any Unsupported or Contradicted claim, with sufficiency confirmed → verdict is **GENERATION FAILURE**.
>    - All claims Supported but the answer still doesn't match the expected answer → say so as a borderline case, not a clean generation failure — the context was textually present but possibly ambiguous or incomplete in substance.
>
> 4. **Final verdict**: pick exactly one — `RETRIEVAL FAILURE`, `CHUNKING FAILURE`, `GENERATION FAILURE`, `MIXED` (name both contributing stages, only if evidence genuinely supports two), or `INSUFFICIENT INPUT TO DETERMINE`. Attach HIGH/MEDIUM/LOW confidence based on which optional inputs (gold passage, adjacent chunks) I actually gave you — not on how confident your prose sounds.
>
> Output in exactly this format:
>
> ```
> ## Verdict: <RETRIEVAL FAILURE | CHUNKING FAILURE | GENERATION FAILURE | MIXED | INSUFFICIENT INPUT TO DETERMINE>
> Confidence: <HIGH | MEDIUM | LOW> — <why, tied to which optional inputs were/weren't given>
>
> ## Evidence
> - <quoted chunk text, answer claim, or gold-passage fact that supports the verdict>
>
> ## Checks Run
> - Sufficiency check: <ran with gold passage / best-effort judgment / not applicable>
> - Chunking-boundary check: <ran with adjacent chunks / unavailable — none provided>
> - Claim-support check: <ran against N claims / not applicable>
>
> ## Recommended Next Step
> <one concrete line, or "cannot recommend a fix with confidence — paste X to sharpen this" if input was too thin>
> ```
>
> Rules: every evidence line must be a direct quote from what I pasted — never invent or paraphrase chunk text, claims, or facts into something more conclusive than what's actually there. Never call retrieval failure HIGH or MEDIUM confidence without a gold passage having been given. Never score generation claims against your own world knowledge — only against the retrieved chunk text I gave you. Never force a single clean label when the evidence is mixed or missing — use MIXED or INSUFFICIENT INPUT TO DETERMINE and say what additional input would resolve it.
>
> Here is my failed RAG interaction:
> **Query**: [paste the query]
> **Retrieved chunks**: [paste each chunk's text, source document, and position if known]
> **Generated answer**: [paste the verbatim answer]
> **Correct answer / gold passage (if known)**: [paste it, or write "not available"]
> **Adjacent chunks (if available)**: [paste the chunk before/after each retrieved chunk, or write "not available"]

## Why this exists

When a RAG system gives a wrong answer, the standard advice is to figure out whether retrieval, chunking, or generation is at fault before trying to fix anything — otherwise you re-tune the retriever when the real problem was a chunk boundary splitting a table row, or re-chunk the corpus when the model just hallucinated past context it already had. Existing RAG evaluation tools and skills are built for the bigger job of constructing a test query set and measuring Recall@k/MRR/faithfulness across a whole pipeline over time — useful, but overkill when someone just needs to know, right now, what went wrong with *this one* answer. This prompt does that narrower job: a single-incident verdict with quoted evidence, honest about its own confidence when the ideal inputs (a gold passage, the neighboring chunks) aren't available.

Full project context and evidence: see [`ideas/rag-failure-stage-attribution-classifier.md`](../../ideas/rag-failure-stage-attribution-classifier.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
