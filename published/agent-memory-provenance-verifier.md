# Proof of Recall: A Structural Verifier for Claimed Agent Memory Authenticity

An AI agent tells you it remembers something you said last Tuesday. How would you actually check that's true, rather than a confident-sounding fabrication? On October 17, 2026, someone ran exactly that test — asking three separate LLM judges to tell a real agent memory from a counterfeit one — and posted the result to Hacker News. The judges couldn't do it. Not "struggled," not "needed tuning": no better than chance. If the obvious cheap fix for this doesn't work, what does?

## The Gap

The HN post ("Three LLM judges couldn't tell an AI agent's real memory from a counterfeit one," 2026-10-17, 5 points, linking to kairos-experiment.com/checks.html) reports a clean negative result: the straightforward mitigation for memory authenticity — hand the claim to an LLM and ask if it sounds genuine — fails outright. That failure isn't an isolated anecdote either. A Manifund grant writeup, working independently, reports that its own headlined detection mechanism "performed no better than chance" under a preregistered test, which corroborates the original finding rather than just repeating it.

What exists instead is research-grade and adjacent, not a deployed answer. `MemSentry` (arXiv 2609.08747) does open-source provenance-based pre-commit checks. "Proof-of-Execution Memory" (arXiv 2608.16032, MIT-licensed) checks a tamper-evident execution ledger instead of inspecting memory content directly — closer to the right idea, but shipped only as a standalone research artifact. A forged-reasoning-attacks survey covers `A-MemGuard` consensus checks, another adjacent-but-not-matching approach. None of this has been packaged, benchmarked, and dropped into the memory backends people are actually using. That's a real, still-open gap, not an already-solved problem wearing a different name.

## The Project

The core move is refusing to play the game the failed judges were playing. Instead of asking a model whether a claimed memory "sounds" genuine — exactly the approach that scored at chance — every memory write gets cryptographically tied, at creation time, to the specific execution-trace segment (a tool call, a retrieved document, a user turn) it was actually derived from. That's a hash reference into a tamper-evident log, in the spirit of Proof-of-Execution Memory, but built as a drop-in layer for existing memory backends rather than a one-off research artifact nobody can install.

Verifying a memory later stops being a judgment call and becomes a deterministic check: does the referenced trace segment still exist, is it unmodified, and does it actually support the claimed fact? That last question is the one subtlety worth sitting with — a fabrication could still cite a real trace segment while misrepresenting what it says, so the entailment check (not just the hash-reference check) is where the real evidentiary weight has to live, and that check remains model-based and imperfect even in the structural design.

The planned components: a write-time provenance-tagging wrapper for Mem0, Zep, and Letta (all three already have mature write-path APIs); a tamper-evident execution-trace store the tagger references; a verifier that resolves a memory's provenance reference, checks trace integrity, and runs a lightweight entailment check against the claimed content; and a benchmark that reproduces the kairos-experiment's genuine-vs-counterfeit test design, scored against this verifier instead of against LLM judges — the most direct possible comparison to the result that motivated the whole project.

## Tangible Impact

**Population**: Buyers and auditors evaluating memory-enabled agent products that market persistent, personalized "the agent remembers you" features — enterprise procurement and security teams vetting a vendor's memory claims before adoption, and builders who want to certify their own product's memory is genuinely derived rather than confabulated — directly the audience the kairos-experiment's negative result was aimed at warning.
**Mechanism**: Today there's no way to check whether a claimed agent memory ("the user told me X last Tuesday") actually happened versus was invented, short of an LLM judge the digest's own evidence shows performs no better than chance. A structural, trace-referenced verifier replaces that guess with a deterministic check, converting "trust the vendor's claim" into "verify it yourself against the reference."
**Measure**: (1) Precision/recall of the structural verifier against a labeled genuine-vs-counterfeit memory set (reproducing the kairos-experiment's test design), compared directly against the 3-LLM-judge baseline's near-chance performance. (2) False-positive rate on legitimately-derived memories whose referenced trace segment has since been compacted or externally modified. (3) Number of memory-backend integrations (Mem0, Zep, Letta) the verifier ships adapters for within the MVP window.

## Try It

A companion Claude Code skill already exists at `skills/agent-memory-provenance-verifier/`: a one-shot forensic check of whether one specific claimed AI-agent memory is actually backed by a pasted execution trace/transcript, or was confabulated — classifying the claim SUPPORTED, UNSUPPORTED, CONTRADICTED, or UNVERIFIABLE against cited trace segments, including the case where a real segment exists but is being misrepresented.

This is the manual, no-infrastructure-required slice of the idea above: it doesn't do live cryptographic trace verification against a running memory backend, but it does catch the exact failure mode the original HN post exposed — a confident claim that doesn't hold up against the evidence — the moment you hand it a memory record and the trace it's supposedly derived from.

To use it: paste the memory claim and the relevant trace/transcript excerpt into any AI chat tool along with the skill's README, or drop the `skills/agent-memory-provenance-verifier/` folder into `~/.claude/skills/` if you're running Claude Code. Either way, give it the claim and the evidence together — it will not proceed without both.

## Risks & Open Questions

- A sufficiently motivated fabrication could still reference a real trace segment while misrepresenting what it shows (citing a real tool call but mischaracterizing its result) — the entailment check, not just the hash-reference check, carries the real evidentiary weight, and that check is still model-based and imperfect.
- If major memory vendors (Mem0, Zep, Letta) add their own provenance tagging first, a standalone wrapper's differentiation narrows to the verification/benchmark layer alone.
- The kairos-experiment's original test set and methodology aren't fully public per the available evidence; building a comparable benchmark may require constructing a new labeled set from scratch, adding scope.
- It's unproven whether real-world "counterfeit memory" incidents are adversarial (deliberate fabrication) or ordinary hallucination — the verifier's design assumes the former is worth guarding against specifically, which the evidence doesn't yet establish as the dominant failure mode.

Surfaced from `research/2026-11-12-context-engineering-and-memory.md`, pattern `P6`.
