# Proof of Recall: A Structural Verifier for Claimed Agent Memory Authenticity

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-and-memory.md · P6
- **Maturity verdict**: PARTIAL — active but narrow/unevaluated research exists on the adjacent "memory poisoning/forged-reasoning" framing: `MemSentry` (arXiv 2609.08747, open-source provenance-based pre-commit checks), "Proof-of-Execution Memory" (arXiv 2608.16032, MIT-licensed, checks a tamper-evident execution ledger instead of inspecting memory content), and a forged-reasoning-attacks survey covering `A-MemGuard` consensus checks. A Manifund grant writeup independently reports its own headlined detection mechanism "performed no better than chance" under a preregistered test — corroborating the original evidence that naive judge-based detection doesn't work. These are research-grade, not production-evaluated, implementations — real gap, differentiated build still viable.
- **Format**: BOTH — write-time provenance tagging plus a continuous verifier is persistent runtime infrastructure; checking one specific flagged memory record against its claimed source is a separable one-shot audit task.
- **Data Sources**: CONNECTED — integrates with an existing memory backend's write path (Mem0, Zep, or Letta — mature APIs already exist for all three) and the agent runtime's own execution-trace/tool-call log (already captured by most harnesses), tagging each memory write with a cryptographic reference to the trace segment it was actually derived from, and resolving that reference at verification time. The memory-backend and trace-logging connectors are mature today; no existing product links the two for provenance verification, which is what this project builds. The skill-angle one-shot version can also run MANUAL — against a pasted memory record plus a pasted execution trace/transcript excerpt — for after-the-fact audits without the live integration installed.

## The Gap

Hacker News, "Three LLM judges couldn't tell an AI agent's real memory from a counterfeit one" (2026-10-17, 5 points), linking to kairos-experiment.com/checks.html, reports a negative result: the straightforward mitigation — ask an LLM to judge whether a claimed memory is genuine — fails outright. The gap-analyst's search found only research-grade adjacent work and one independent corroboration (the Manifund grant writeup) that naive judge-based detection performs no better than chance, with no production-evaluated alternative shipped anywhere.

## The Project

A structural, non-judgment-based provenance verifier: instead of asking a model whether a claimed memory "sounds" genuine, every memory write is cryptographically tied at creation time to the specific execution-trace segment (tool calls, retrieved documents, user turns) it was actually derived from — a hash reference into a tamper-evident log, in the spirit of Proof-of-Execution Memory but packaged as a drop-in layer for existing memory backends rather than a standalone research artifact. Verifying a memory's authenticity later becomes a deterministic check (does the referenced trace segment exist, is it unmodified, does it actually support the claimed fact) instead of a model guessing from text alone — directly answering the negative result that motivated the digest's HN post.

Components: a write-time provenance-tagging wrapper for Mem0, Zep, and Letta; a tamper-evident execution-trace store the tagger references; a verifier that resolves a memory's provenance reference, checks trace integrity, and runs a lightweight entailment check (does the referenced segment actually support the claimed content); a benchmark reproducing the kairos-experiment's genuine-vs-counterfeit test design, scored against this verifier instead of LLM judges.

## Tangible Impact

**Population**: Buyers and auditors evaluating memory-enabled agent products that market persistent, personalized "the agent remembers you" features — enterprise procurement and security teams vetting a vendor's memory claims before adoption, and builders who want to certify their own product's memory is genuinely derived rather than confabulated — directly the audience the kairos-experiment's negative result was aimed at warning.
**Mechanism**: Today there's no way to check whether a claimed agent memory ("the user told me X last Tuesday") actually happened versus was invented, short of an LLM judge the digest's own evidence shows performs no better than chance. A structural, trace-referenced verifier replaces that guess with a deterministic check, converting "trust the vendor's claim" into "verify it yourself against the reference."
**Measure**: (1) Precision/recall of the structural verifier against a labeled genuine-vs-counterfeit memory set (reproducing the kairos-experiment's test design), compared directly against the 3-LLM-judge baseline's near-chance performance. (2) False-positive rate on legitimately-derived memories whose referenced trace segment has since been compacted or externally modified. (3) Number of memory-backend integrations (Mem0, Zep, Letta) the verifier ships adapters for within the MVP window.

## Why Now

The negative result — three LLM judges failing, independently corroborated by a Manifund-funded grant finding its own method "no better than chance" — closes off the obvious cheap fix within the same 30-day window, while structural alternatives (Proof-of-Execution Memory, MemSentry) exist only as research code with no packaged, benchmark-evaluated product. That leaves a clear, now-narrowed engineering gap rather than an open-ended research question.

## Skill Angle

Given a specific memory record (a claimed fact or "experience" the agent reports) and the session's execution trace/transcript it's claimed to derive from, pasted directly, check deterministically whether the trace actually contains support for the claim (a matching tool result, retrieved document, or user statement) and flag it as supported, unsupported, or contradicted — citing the specific trace segment either way. This is a one-shot audit useful today for anyone reviewing a specific flagged memory, without the full write-time tagging infrastructure installed.

## MVP Sketch

A wrapper around one memory backend (Mem0) that tags each write with a hash reference to the current session's append-only tool-call/message log, plus a verifier CLI that resolves a reference and runs a cheap-model entailment check between the referenced trace segment and the memory's claimed content. Experiment: reproduce the kairos-experiment's genuine-vs-counterfeit test set (or a close equivalent built from real agent sessions with planted fabricated memories), score the structural verifier against it, and compare precision/recall directly to the paper's reported near-chance LLM-judge baseline. 3–4 weeks for 1–2 people.

## Risks & Open Questions

- A sufficiently motivated fabrication could still reference a real trace segment while misrepresenting what it shows (citing a real tool call but mischaracterizing its result) — the entailment check, not just the hash-reference check, carries the real evidentiary weight, and that check is still model-based and imperfect.
- If major memory vendors (Mem0, Zep, Letta) add their own provenance tagging first, a standalone wrapper's differentiation narrows to the verification/benchmark layer alone.
- The kairos-experiment's original test set and methodology aren't fully public per the digest evidence; building a comparable benchmark may require constructing a new labeled set from scratch, adding scope.
- It's unproven whether real-world "counterfeit memory" incidents are adversarial (deliberate fabrication) or ordinary hallucination — the verifier's design assumes the former is worth guarding against specifically, which the evidence doesn't yet establish as the dominant failure mode.
