---
name: agent-benchmark-harness-normalizer
description: Flags when two agent/model benchmark numbers being compared head-to-head aren't actually comparable because the surrounding execution harness (scaffold, retries, timeouts, prompt wrapper) differs or is undisclosed, and drafts a caveat paragraph for the comparison memo. Use when someone cites or is about to act on two published agent benchmark scores as a ranking.
---

# Agent Benchmark Harness-Variance Flag

## When to use this
Someone is about to cite, paste into a decision memo, or act on two (or more) published agent/model benchmark numbers as a head-to-head ranking — e.g. "Model A scores 74% on SWE-bench Verified vs. Model B's 68%, so we're going with A", or a vendor blog post / leaderboard screenshot is being used to justify picking a framework or model. Use this *before* the comparison gets written into a decision doc, not after, and use it even when both numbers come from the "same" benchmark name — the benchmark name being identical is exactly what makes the harness difference invisible.

Do not use this to run or design a new benchmark, to normalize scores onto a shared scale, or to re-execute either candidate yourself — that is the full "Harness Check" project (an orchestration tool built on the HAL open-source harness), a separate, heavier piece of infrastructure. This skill never runs code or calls a model; it only interrogates the claims as stated and tells you whether they're safe to compare.

## Inputs
**Data source**: Manual — the user pastes in the two (or more) benchmark claims being compared. For each claim, hand over whatever is available:
- Model/agent name and version
- Benchmark name and version (e.g. "SWE-bench Verified" vs. plain "SWE-bench" — these are not the same benchmark)
- The score and how it was computed (pass@1, pass@k, average of N trials, best-of-N)
- The source (vendor blog post, a public leaderboard, a paper, a GitHub README) and its date
- Any stated harness/scaffold details: which agent framework or tool-calling scaffold ran it, temperature, retry/self-consistency count, per-task timeout, sandbox/environment version

If a claim is missing harness details, that's expected and is itself the finding — do not go find or guess them. Never substitute an assumption for a detail the source didn't publish.

## Procedure
1. **Extract each claim into a structured row** — model/agent, benchmark + version, score + scoring method, source, date, and every harness detail actually stated in the pasted text. Mark any field not stated as `undisclosed`, never blank or inferred.
2. **Check benchmark identity first.** If the benchmark names differ in version or scope (e.g. "SWE-bench" vs. "SWE-bench Verified" vs. a vendor's custom, unnamed, or internal benchmark), flag this prominently as its own failure, surfaced ahead of the harness-factor analysis in the final output — this is a harder failure than harness variance. Still complete steps 3-8 for the record (an identity mismatch plus harness differences is worse than either alone, and the full table is still useful context), but the final verdict and caveat must be driven primarily by the identity mismatch, not buried under it.
3. **Run the harness-sensitive-factor checklist** against each claim: tool-calling scaffold/framework, temperature, retry or self-consistency count, per-task timeout, number of trials and how they were aggregated, prompt/system-message template, sandbox or execution environment version. For each factor, mark it `same` (both sources explicitly state matching values), `different` (both state it, and they differ), or `undisclosed` (one or both sources don't say).
4. **Assign a comparability verdict**:
   - `COMPARABLE` — every harness-sensitive factor is confirmed `same` (rare; usually only true when both claims ran through the identical published harness, e.g. both via the same open leaderboard run).
   - `NOT COMPARABLE` — at least one factor is confirmed `different`, or the benchmark version differs (step 2).
   - `UNKNOWN` — no factor is confirmed different, but one or more are `undisclosed`. This is the most common real-world case and must never be upgraded to `COMPARABLE` just because nothing was proven different.
5. **Ground the magnitude in documented research, not speculation.** Cite known, published findings on how much harness changes alone can move a score for context (e.g., published research has measured scaffold-only swings of roughly 7 percentage points on one long-horizon benchmark, and double-digit-point scaffold-only variation reported for SWE-bench Verified across different scaffolds). State these as "harness variance has been documented at this order of magnitude in other cases" — never claim this specific comparison's gap is caused by the harness; only that it cannot be ruled out.
6. **Optionally use web search** (if available) to check whether either source's harness is independently documented (e.g., a vendor's technical report naming its scaffold, or a known leaderboard's fixed-harness methodology) — this can upgrade an `undisclosed` factor to `same`/`different` with a citation, but only on a specific, checkable claim, never a general "they're probably similar" assumption.
7. **Draft the caveat paragraph** — see Output format below — sized to drop directly into a comparison memo.
8. **Recommend a next step**: proceed with the comparison (only if `COMPARABLE`), seek a harness-matched rerun or an independent third-party re-evaluation (if `NOT COMPARABLE` or `UNKNOWN` and the decision is high-stakes), or proceed with the caveat attached and confidence downgraded (if `UNKNOWN` and the decision is low-stakes).

## Output format
A single markdown "Harness-Variance Flag" with these sections, in order:
1. **Claims Captured** — a table: columns = Claim label (A/B/...), Model/Agent, Benchmark + version, Score + method, Source, Date.
2. **Benchmark Identity Check** — one line: same benchmark/version confirmed, or the specific mismatch found.
3. **Harness-Sensitive Factor Table** — rows = each factor from step 3, columns = Claim A value, Claim B value, Status (`same`/`different`/`undisclosed`).
4. **Comparability Verdict** — `COMPARABLE` / `NOT COMPARABLE` / `UNKNOWN`, one sentence justifying it from the table above.
5. **Documented Magnitude Context** — 1-2 sentences citing known published harness-variance figures (with what they measured), explicitly framed as context, not a claim about this specific pair.
6. **Draft Caveat Paragraph** — a ready-to-paste paragraph stating the verdict, which specific factors are undisclosed or differ, and the documented magnitude context, written for a decision memo audience (no jargon dump, 3-5 sentences).
7. **Recommended Next Step** — one line per step 8.

## Guardrails
- Never state or imply a specific percentage of the observed gap between two scores is "due to the harness" — only published, cited research findings get specific percentage figures, and those are always framed as general documented variance, not an explanation of the pasted comparison.
- Never upgrade an `undisclosed` factor to `same` without a specific, cited source confirming it — absence of a stated difference is not evidence of sameness.
- Never fabricate a harness detail (scaffold name, retry count, temperature) that wasn't in the pasted text or a cited search result.
- Never treat two benchmark names that differ in version (e.g. "SWE-bench" vs. "SWE-bench Verified") as the same benchmark.
- Never run, execute, or simulate the actual benchmark yourself, or claim to have reproduced either score — this skill only evaluates the comparability of claims as stated.
- If the user supplies only one benchmark claim with nothing to compare it against, stop and ask for the second claim rather than inventing a plausible-sounding comparator.
