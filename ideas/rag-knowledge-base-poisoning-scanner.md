# CleanIndex: A Maintained Pre-Ingestion Scanner for RAG Knowledge-Base Poisoning

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques.md · P6
- **Maturity verdict**: OPEN — `gh search repos "RAG prompt injection detection"` returned only small, unmaintained-looking research prototypes (nadeem015/rag-prompt-injection-detection: self-described "research prototype"; two near-empty repos with no description; a niche JS SDK for Japanese-language injection). WebSearch found further research-only prototypes (RAGDefender, FilterRAG/ML-FilterRAG, an ECCWS proof-of-concept, provenance-based RAGShield) — none confirmed as released, actively-maintained tools; RAGDefender's own paper says the authors merely "plan to open-source it." No credible maintained implementation found after genuine multi-channel search — only discussion, research prototypes, and disagreement over approach (detection vs. permissioning).
- **Format**: BOTH

## The Gap

An arXiv paper, "CleanBase: Detecting Malicious Documents in RAG Knowledge Databases" (2026), proposes a detector for adversarial documents hijacking a RAG pipeline into following attacker-specified instructions — but it is a research paper, not a released tool. WebSearch found only small, regex-level vendor point-tools and research prototypes that explicitly say they plan to open-source rather than have done so, plus practitioner disagreement (via a tianpan.co post) over whether detection or permissioning is even the right control. Teams accepting externally-sourced or user-contributed documents into a RAG knowledge base currently have no maintained, adoptable scanner to run before ingestion.

## The Project

A pre-ingestion scanning middleware that sits between a document source and the vector index: it flags documents containing instruction-shaped content targeted at an LLM (imperative phrasing addressed to "the assistant," hidden/invisible-text injection techniques, known jailbreak-pattern fragments) using a layered approach — fast regex/heuristic pre-filter plus an LLM-based classifier for ambiguous cases — and quarantines flagged documents for human review rather than silently blocking or silently indexing them. It ships as a drop-in step for common ingestion pipelines (LangChain/LlamaIndex document loaders) rather than a bespoke integration, closing the "plan to open-source it" gap the research prototypes left open.

## Tangible Impact

**Population**: Teams running RAG over externally-sourced or user-contributed content where documents aren't fully trusted before indexing — customer-support knowledge bases built from ticket/forum content, enterprise search over vendor- or partner-submitted documents, and any RAG deployment ingesting scraped or crowd-sourced web content. This is the exact threat model CleanBase's paper and the vendor point-tools target, but with no maintained tool any of these teams can actually install today.
**Mechanism**: Catching instruction-shaped adversarial content before it enters the index, rather than relying on output-side guardrails (which only catch the attack after it has already influenced a generation), closes the specific gap practitioner commentary flagged — that detection-at-ingestion is underbuilt relative to runtime output filtering — and gives teams a quarantine step that surfaces suspicious documents for review instead of either blind trust or blind blocking.
**Measure**: detection precision/recall on a labeled test set combining known jailbreak-injection patterns with CleanBase's described threat model; false-positive rate on a corpus of legitimate but imperative-sounding documents (e.g., instructional/how-to content, which risks over-triggering a naive filter); time-to-flag for a newly injected document in a simulated poisoning scenario.

## Why Now

RAG knowledge bases are increasingly built from externally-contributed content (support tickets, partner docs, scraped web pages) as RAG adoption broadens beyond curated internal corpora, while the only published defense (CleanBase) remains a paper rather than a tool — the threat is live and documented, and the maintained-tool gap is confirmed rather than assumed.

## Skill Angle

A "Knowledge Base Poisoning Audit" skill: given a sample batch of documents already in a team's existing RAG corpus, it scans for the same instruction-shaped injection patterns the full scanner targets and reports a risk-ranked list — a one-time retroactive audit for teams who want to check an existing knowledge base's exposure before committing to the ingestion-pipeline integration.

## MVP Sketch

2–4 weeks, 1–2 people: build the regex/heuristic pre-filter first (fast, catches obvious cases), add an LLM-classifier pass for ambiguous documents, assemble a labeled test set from CleanBase's described patterns plus known public jailbreak-injection examples, and validate precision/recall plus false-positive rate on a mixed corpus of legitimate instructional content and injected documents before shipping the ingestion-pipeline integration.

## Risks & Open Questions

- Practitioner disagreement (detection vs. permissioning) is a real open question — this project bets on detection being worth building regardless, but a permissioning-first team may consider it solving the wrong layer.
- False positives on legitimate imperative/instructional content (how-tos, policy documents) could make the scanner annoying enough that teams disable it, undermining the whole premise.
- CleanBase's authors could release their own tool before this ships, which would be a win for the ecosystem but requires checking before duplicating effort.
- A sufficiently novel injection technique (not matching known patterns) will evade a pattern/classifier-based scanner by design — this is a risk-reduction tool, not a guarantee, and should be framed that way to adopters.
