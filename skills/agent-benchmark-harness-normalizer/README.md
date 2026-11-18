# Agent Benchmark Harness-Variance Flag

A self-contained prompt template for any AI chat tool. Paste this whole document (or just the "Prompt" section at the bottom, with your two benchmark claims filled in) into ChatGPT, Claude, Gemini, or any other assistant to get a structured check on whether two agent/model benchmark numbers are actually safe to compare head-to-head.

## What this is for

People constantly compare published agent/model benchmark scores — "Model A hit 74% on SWE-bench Verified, Model B hit 68%, so we're picking A" — without checking whether the two numbers were produced under the same execution conditions. Published 2026 research (e.g. a paper titled "Stop Comparing LLM Agents Without Disclosing the Harness") has measured that swapping only the surrounding execution harness — the tool-calling scaffold, retry logic, timeouts, prompt wrapper — while holding the model fixed can move a score by double digits on some benchmarks. The benchmark name being identical does not mean the comparison is valid. This tool catches that before it goes into a decision memo.

This is a lightweight, no-infrastructure check. It never runs a benchmark or re-executes either candidate — it only interrogates the claims as stated. (A separate, heavier project called "Harness Check" exists to actually re-run candidates through a normalized harness; this is the quick sanity-check version anyone can use in a chat window.)

## What you need to hand over

Manual input — you paste in the two (or more) benchmark claims you're comparing. For each one, give whatever you have:
- Model/agent name and version
- Benchmark name and version (note: "SWE-bench" and "SWE-bench Verified" are different benchmarks — say which one)
- The score and how it was computed (pass@1, pass@k, average of N trials, best-of-N — if stated)
- The source (vendor blog post, a leaderboard, a paper, a GitHub README) and its date
- Any harness/scaffold details that were stated: which agent framework ran it, temperature, retry count, per-task timeout, sandbox version

If some of these are missing, that's fine and expected — missing harness details are themselves the finding. Don't go look them up or guess; just note what wasn't stated.

## What it does

1. Puts each claim into a structured row: model, benchmark + version, score + method, source, date, and every harness detail actually stated.
2. Checks first whether the two benchmark names/versions actually match — a version mismatch is flagged immediately and is worse than a harness mismatch.
3. Runs a checklist of harness-sensitive factors against both claims — tool-calling scaffold/framework, temperature, retry/self-consistency count, per-task timeout, number of trials and aggregation method, prompt template, sandbox/environment version — marking each factor `same`, `different`, or `undisclosed`.
4. Assigns one of three verdicts:
   - **COMPARABLE** — every factor confirmed the same (rare).
   - **NOT COMPARABLE** — at least one factor confirmed different, or the benchmark versions don't match.
   - **UNKNOWN** — nothing confirmed different, but one or more factors are undisclosed. This is the most common outcome, and it is never upgraded to COMPARABLE just because nothing was proven different.
5. Grounds the magnitude of the risk in documented research (e.g. scaffold-only swings reported in the ~7-15 percentage point range in published 2026 papers on specific benchmarks) — framed as general context for how much this kind of gap can matter, never as a claim about what caused your specific numbers.
6. Drafts a ready-to-paste caveat paragraph for your comparison memo.
7. Recommends a next step: proceed as-is (only if COMPARABLE), seek a harness-matched rerun or independent re-evaluation (if the decision is high-stakes and the verdict is NOT COMPARABLE or UNKNOWN), or proceed with the caveat attached and lowered confidence (if the decision is low-stakes).

## Output you'll get

A markdown report with these sections in order:
1. **Claims Captured** — table of both claims (model, benchmark+version, score+method, source, date).
2. **Benchmark Identity Check** — one line confirming match or naming the mismatch.
3. **Harness-Sensitive Factor Table** — each factor, both claims' values, and same/different/undisclosed.
4. **Comparability Verdict** — COMPARABLE / NOT COMPARABLE / UNKNOWN, with one sentence of justification.
5. **Documented Magnitude Context** — 1-2 sentences citing real published harness-variance findings, as context only.
6. **Draft Caveat Paragraph** — a 3-5 sentence paragraph you can paste straight into your memo.
7. **Recommended Next Step** — one line.

## Rules this tool follows (don't let it skip these)

- It never says a specific percentage of the gap between your two scores is "because of the harness" — only cited published research gets specific percentage figures, always as general context.
- It never upgrades an undisclosed factor to "same" without a specific cited source — not stating a difference is not evidence of sameness.
- It never invents a harness detail that wasn't in what you pasted or in a cited search result.
- It never treats differently-versioned benchmarks (e.g. "SWE-bench" vs. "SWE-bench Verified") as the same benchmark.
- It never claims to have run, reproduced, or simulated either benchmark score itself.
- If you only give it one benchmark claim, it will ask you for the second one rather than making one up.

## Prompt

Paste this, with your two claims filled in:

```
You are checking whether two published agent/model benchmark claims are safe to compare head-to-head, given that research has shown the surrounding execution harness (scaffold, retries, timeouts) can move a score as much as swapping the model does.

Claim A:
- Model/agent: <name + version>
- Benchmark + version: <e.g. SWE-bench Verified>
- Score + method: <e.g. 74%, pass@1, average of N trials if known>
- Source + date: <vendor blog / leaderboard / paper, date>
- Harness details stated (if any): <scaffold/framework, temperature, retry count, timeout, sandbox version — or "not stated">

Claim B:
- Model/agent: <name + version>
- Benchmark + version: <...>
- Score + method: <...>
- Source + date: <...>
- Harness details stated (if any): <... or "not stated">

Do the following, in order:
1. Put both claims into a table (model, benchmark+version, score+method, source, date).
2. Check whether the benchmark name/version actually matches between A and B — if not, flag this prominently as its own failure (worse than a harness mismatch), but still complete steps 3-7 for context; the final verdict and caveat should be driven by the identity mismatch, not buried under the harness factor table.
3. Check these harness-sensitive factors for both claims, marking each "same" / "different" / "undisclosed": tool-calling scaffold/framework, temperature, retry/self-consistency count, per-task timeout, number of trials and aggregation method, prompt/system-message template, sandbox/environment version. Never guess a value I didn't give you — mark it undisclosed.
4. Give a verdict: COMPARABLE (everything confirmed same), NOT COMPARABLE (something confirmed different or benchmark mismatch), or UNKNOWN (nothing confirmed different but something undisclosed). Default to UNKNOWN rather than COMPARABLE when in doubt.
5. Cite 1-2 documented, real examples from published research of how much harness changes alone have been shown to move agent benchmark scores, as general context only — not as an explanation of my specific gap.
6. Draft a 3-5 sentence caveat paragraph I can paste into a comparison memo, stating the verdict, the specific undisclosed/differing factors, and the magnitude context.
7. Recommend one next step: proceed as-is, seek a harness-matched rerun, or proceed with the caveat and lowered confidence — based on how high-stakes my decision is (tell me if you need to ask what's at stake).

Never claim a specific percentage of my gap is caused by the harness. Never invent a harness detail I didn't give you. Never treat different benchmark versions as the same benchmark.
```
