# RAG Seam Test Case Drafter

A paste-into-any-AI-chat-tool prompt that reviews your RAG (Retrieval-Augmented Generation) pipeline's retriever-to-generator handoff and drafts concrete test cases for failure modes that your separate retriever tests and generator tests structurally can't catch.

## Why this exists

Most RAG teams past the prototype stage have two kinds of test coverage: tests that score the retriever (recall@k, precision@k) and tests that score the generator against an idealized, hand-picked context. Neither tests the actual handoff — what happens when the generator receives the retriever's real, messy top-k output: a relevant chunk next to a near-duplicate-but-wrong chunk, or two chunks that disagree with each other. That handoff — the "seam" — is where a lot of production answer-quality bugs live, and it has no standard test layer. This isn't a claim that nothing exists anywhere; general RAG architecture-review skills and audit checklists exist, but none frame the handoff itself as a named, independently-testable failure class with ready-to-adapt test cases. This prompt fills that specific gap.

This is a **one-time design review that drafts test cases for you to adopt**, not a working CI harness. It doesn't run code, doesn't install anything, and doesn't replace tools like Ragas or DeepEval — it produces the seam-specific test cases those tools don't give you out of the box.

## When to use this

- You have retriever tests and generator tests, but a production bug slipped through both because it was a handoff problem, not a component problem.
- You're about to ship a RAG pipeline change and want seam-level test cases before you add them to CI.
- You want a second opinion on what's actually at risk in your specific pipeline's retriever/generator handoff, grounded in your actual architecture rather than a generic checklist.

## What to hand over (Data source: Manual)

This is manual input — you paste a description of your own pipeline. There's no external connector here; the entire point is testing your own code against your own content, so nothing needs to be "connected."

Paste or describe:

1. **Your retriever**: dense, sparse, or hybrid; whether you rerank; your top-k value; your chunking strategy (chunk size, overlap, and whether chunks can end up mid-sentence or as raw HTML/table fragments).
2. **Your generator**: the prompt template, specifically how retrieved chunks get inserted into it, and whether the prompt gives any instruction for handling irrelevant or conflicting context.
3. **What you already test**: what your retriever tests check, what your generator tests check, and whether your generator tests use hand-picked "ideal" context or the retriever's live output.

Optional but genuinely useful:

4. A real query plus the actual top-k chunks your retriever returned for it (plain text is fine) — this lets the test cases be built from your real noise/contradiction patterns instead of invented examples.
5. Any production incident where the answer was wrong even though both your retrieval and generation tests passed.

If you don't have item 1 or 2 fully worked out, say so — the review will note what it can't assess rather than guessing.

## The prompt

Paste this into your AI tool along with your answers to the inputs above:

> You are reviewing the retriever-to-generator handoff ("seam") in my RAG pipeline — the point where my generator receives my retriever's actual output, as opposed to my retriever and generator being tested separately. Based on what I describe below, do the following:
>
> 1. Summarize my pipeline shape in a few bullets (retriever type, chunking, generator prompt structure, existing test coverage).
> 2. Score each of these five seam failure modes as High / Medium / Low / Insufficient-information risk for my specific pipeline, citing the exact detail from my description that justifies each rating (never guess a rating without a reason tied to what I told you):
>    - Noise poisoning — a borderline-relevant or near-duplicate chunk leaks into the answer.
>    - Chunk-misuse / faithfulness-to-actual-retrieval — my generator tests use idealized hand-picked context instead of my retriever's real output.
>    - Contradiction-blindness — two retrieved chunks disagree and my generator silently picks one instead of flagging it.
>    - Structural mismatch — my chunking can produce mid-sentence cuts, orphaned table cells, or raw HTML my generator was never tested against.
>    - Attribution erasure — my answer sounds grounded but could be coming from the model's own memory rather than my retrieved context.
> 3. For every mode you rate High or Medium, draft one concrete test case: a small fixture set of 2-4 chunks illustrating the failure (built from my real example chunks if I gave you any — otherwise clearly label the chunks as illustrative placeholders, never pretend they're real), the query being asked, the exact context mix fed to the generator, a specific assertion that names the mechanism being tested (never a generic "is this correct" assertion), and pytest-style pseudocode for that assertion.
> 4. List any mode you marked "insufficient information" and tell me exactly what detail you'd need from me to assess it.
> 5. End with one line stating plainly that this is a design review producing draft test cases, not a working test harness — I'd still need to wire these into my own test runner and maintain the fixture corpus myself.
>
> Do not invent details about my architecture I didn't give you — mark gaps as open questions instead. Do not fall back on generic RAG metrics like precision@k, recall@k, or an overall faithfulness score — stay scoped to the handoff itself.
>
> Here is my pipeline:
> [paste your retriever description, generator prompt template, existing test coverage, and optionally a real query + its retrieved chunks and any relevant incident]

## What you get back

A structured review with: a pipeline snapshot, a risk table across the five seam failure modes with reasons, one draft test case per High/Medium-risk mode (fixtures, query, context mix, mechanism-named assertion, pseudocode), an open-questions list for anything under-specified, and a one-line scope reminder that this is a draft for you to adopt, not installed infrastructure.

## What this won't do

- It won't run your code, access your actual retriever/vector store, or install anything — everything comes from what you paste.
- It won't replace component-level eval tools (Ragas, DeepEval, LangSmith) — those already score retrieval and generation quality separately; this fills the gap between them.
- It won't invent a plausible-sounding architecture if you give it too little to work with — expect "insufficient information" on anything you didn't describe.
- It won't produce a maintained fixture corpus or CI integration — that's real engineering work this review is scoped to kick off, not finish.
