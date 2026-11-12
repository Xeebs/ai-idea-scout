# CleanIndex: A Maintained Pre-Ingestion Scanner for RAG Knowledge-Base Poisoning

Anyone can write a document that tells your assistant what to do — and if that document ends up in your RAG index, your assistant will listen. That's the quiet failure mode sitting underneath every knowledge base built from support tickets, partner uploads, or scraped web pages: there's a real, documented attack here, a researcher has already written the paper describing it, and yet there is still no maintained tool a team can actually install to stop it.

## The Gap

In 2026, an arXiv paper called "CleanBase: Detecting Malicious Documents in RAG Knowledge Databases" laid out the threat clearly: an adversarial document, planted into a RAG knowledge base, can hijack the pipeline into following attacker-specified instructions instead of the user's. It's a real paper describing a real mechanism — but it's a paper, not a tool. A search for anything that actually implements this defense turns up a thin, uneven landscape: a handful of small vendor point-tools doing regex-level checks, a few abandoned-looking research prototypes, and — tellingly — the authors of one closely-related project, RAGDefender, stating in their own paper that they merely "plan to open-source it." Practitioner commentary (surfaced via a tianpan.co post) adds a layer of unresolved disagreement on top: some argue detection is the wrong layer entirely and permissioning (controlling who can contribute documents in the first place) is the control that actually matters.

So you have a confirmed threat model, a published detection approach, and zero maintained, adoptable implementations. That's an unusually clean gap: not "nobody's thought about this," but "everybody who's thought about it stopped at a prototype or a plan."

## The Project

CleanIndex is pre-ingestion scanning middleware — it sits between wherever your documents come from and your vector index, and it looks at every document before it gets a chance to become part of what your assistant trusts. It's built as a layered pipeline on purpose: a fast regex/heuristic pre-filter catches the obvious cases (imperative phrasing addressed to "the assistant," hidden or invisible-text injection tricks, known jailbreak-pattern fragments) cheaply and immediately, and an LLM-based classifier picks up the ambiguous cases the heuristics can't confidently call. Anything flagged gets quarantined for a human to look at — not silently blocked (which breaks pipelines on false positives and erodes trust) and not silently indexed anyway (which defeats the point).

The part that matters most for adoption is that it ships as a drop-in step for the ingestion pipelines teams already have — LangChain and LlamaIndex document loaders — rather than a bespoke integration someone has to hand-roll. That's precisely the gap the research prototypes left open: it's the difference between "we plan to open-source a detector" and a scanner you can actually point at your existing pipeline this afternoon.

## Tangible Impact

**Population**: Teams running RAG over externally-sourced or user-contributed content where documents aren't fully trusted before indexing — customer-support knowledge bases built from ticket/forum content, enterprise search over vendor- or partner-submitted documents, and any RAG deployment ingesting scraped or crowd-sourced web content. This is the exact threat model CleanBase's paper and the vendor point-tools target, but with no maintained tool any of these teams can actually install today.
**Mechanism**: Catching instruction-shaped adversarial content before it enters the index, rather than relying on output-side guardrails (which only catch the attack after it has already influenced a generation), closes the specific gap practitioner commentary flagged — that detection-at-ingestion is underbuilt relative to runtime output filtering — and gives teams a quarantine step that surfaces suspicious documents for review instead of either blind trust or blind blocking.
**Measure**: detection precision/recall on a labeled test set combining known jailbreak-injection patterns with CleanBase's described threat model; false-positive rate on a corpus of legitimate but imperative-sounding documents (e.g., instructional/how-to content, which risks over-triggering a naive filter); time-to-flag for a newly injected document in a simulated poisoning scenario.

## Try It

No companion skill has been written yet for CleanIndex — the idea's skill angle (a "Knowledge Base Poisoning Audit" that scans an existing corpus retroactively, rather than gating new ingestion) is sketched in the idea file but not yet built out into a `skills/` directory. If a `skills/rag-knowledge-base-poisoning-scanner/` lands in a future cycle, it'll show up linked here.

A few honest caveats worth carrying forward rather than glossing over: there's real disagreement among practitioners about whether detection is even the right layer compared to permissioning who can contribute documents at all — this project bets on detection being worth building regardless, but a permissioning-first team may see it as solving the wrong problem. A pattern/classifier-based scanner will, by design, miss a sufficiently novel injection technique it hasn't seen before — this is risk reduction, not a guarantee, and should be framed that way to anyone adopting it. And false positives on legitimate imperative content (how-tos, policy documents) are the failure mode that kills adoption fastest — a scanner annoying enough to get disabled defeats the whole premise. It's also worth checking, before building, whether CleanBase's own authors have shipped their own tool in the meantime — a win for the ecosystem, but worth confirming rather than duplicating.

---

Surfaced from `research/2026-11-12-rag-techniques.md`, pattern `P6`.
