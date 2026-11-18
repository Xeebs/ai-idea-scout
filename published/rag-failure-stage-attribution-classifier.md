# Fault Line: Stop Guessing Why Your RAG System Got It Wrong

A RAG system gives a wrong answer. An engineer stares at the trace and has to guess: was the right passage never fetched, was it fetched but chopped in half by a chunk boundary, or was everything there and the model just made something up? Every fix for one of those problems is wasted effort on the other two — and right now, that guess is still made by eyeballing a trace, not by a tool.

## The Gap

Multiple 2026 production-RAG postmortems converge on the same piece of advice: before you touch anything, attribute the wrong answer to retrieval, chunking, or generation. One widely-cited writeup, "Production RAG Systems — 7 Lessons We Learned the Hard Way," along with a separate RAG-evaluation framework guide, both frame this as the first triage step any team should take — and both describe teams "lacking an evaluation framework" who simply don't know their system is broken until a user complains.

Here's the catch: every source describing this as advice also describes it as a manual practice. The closest thing to an automated tool, RAGChecker, does claim-level analysis that separates retrieval from generation — but it has no chunking category at all, and it's sat unmaintained since late 2024. A TU Delft academic failure taxonomy exists, but it's a paper, not tooling. And a LangChain forum thread ("When is it actually a failure? Diagnosing agent behavior beyond LangGraph traces") says it plainly: tools that detect a post-retrieval failure can't trace it back to the specific insufficient chunk that caused it — that runtime attribution layer is missing. No source, across a genuine multi-channel search of GitHub, the web, and papers, names a shipped tool that actually does the three-way classification.

## The Project

Fault Line takes one failed RAG interaction — the query, the retrieved chunks with their source-document spans, and the generated answer — and returns a specific verdict with evidence attached, not a shrug. It checks for a **retrieval failure** (the right passage was never fetched, verified by re-running retrieval against a known-good query reformulation or a labeled gold passage), a **chunking failure** (the right document was fetched, but the chunk boundary sliced the answer-bearing sentence or table row away from its context — caught by inspecting adjacent chunks and the original document span), or a **generation failure** (the context was sufficient and correctly chunked, but the model still answered wrong or unsupported — caught via claim-level support scoring against exactly what was retrieved, nothing else).

It ships two ways. As a CLI/library that ingests a LangSmith or Langfuse trace export and a dashboard that aggregates verdicts across a batch of failures, so a team sees "62% of your failures this week are chunking, not retrieval" instead of re-litigating each incident from scratch. And, because the same underlying logic works on a single pasted trace with no observability-platform integration at all, as a standalone skill for quick one-off triage — see Try It below.

The individual techniques this composes already exist and are validated — claim-level support scoring and "sufficient context" classification are both used independently today (RAGChecker, and Google Research's ICLR 2025 sufficient-context paper), and LangSmith/Langfuse's trace-export APIs matured enough in 2025–2026 to make pulling a structured failure trace trivial. What's missing is wiring those primitives together into one attribution verdict — that's the actual gap, not the underlying math.

## Tangible Impact

**Population**: Engineering teams running production RAG systems who currently triage failures by hand — the same audience the cited "lessons learned" posts and LangChain forum thread describe directly. RAG is now a standard component of customer support, internal knowledge, and developer-tooling products, so this spans any team past the prototype stage with a live failure backlog, not a narrow vertical.
**Mechanism**: Today a team sees a wrong answer and has to manually decide whether to re-tune the retriever, re-chunk the corpus, or re-prompt the generator — each a different, expensive fix with no signal about which one is actually broken. An automated per-failure verdict with evidence turns that guess into a routed ticket, so engineering time goes to the actual broken stage instead of being spread across all three on a hunch.
**Measure**: agreement rate between the classifier's verdict and a human engineer's independent manual triage on a held-out failure set (precision/recall per failure class); median time from "user reports a bad answer" to "root-cause stage identified," before vs. after adoption; percentage of fixes that target the correctly-identified stage on the first attempt.

## Try It

A standalone skill version of this exists at [`skills/rag-failure-stage-attribution-classifier/`](../skills/rag-failure-stage-attribution-classifier/):

> Given one failed RAG (retrieval-augmented generation) interaction — the query, what got retrieved, and the generated answer — classifies whether the failure originated in retrieval, chunking, or generation, with quoted evidence and a confidence level. Use when someone pastes a single bad RAG answer and asks "why did this happen" or "which part of my pipeline is broken" rather than a full evaluation-framework build.

To use it: paste the whole `README.md` from that folder into any AI chat tool (ChatGPT, Claude, etc.) along with your query, retrieved chunks, and generated answer — no installation needed. If you use Claude Code, drop the `skills/rag-failure-stage-attribution-classifier/` folder into `~/.claude/skills/` and it activates automatically the next time you ask Claude to diagnose a bad RAG answer.

One honest caveat worth carrying over from the idea's own risk notes: real failures are often multi-cause — a mediocre retrieval result compounded by a bad chunk boundary — so the classifier is built to report `MIXED` or `INSUFFICIENT INPUT TO DETERMINE` rather than forcing a single clean label it can't actually defend.

Surfaced from `research/2026-11-13-rag-techniques.md`, pattern `P2`.
