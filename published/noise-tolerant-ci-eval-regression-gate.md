# Noise Floor: A Statistically-Calibrated Pass/Fail Layer for CI Prompt-Regression Gates

A score drops from 0.71 to 0.68 and your CI gate turns red. Is that a real regression from the prompt change in the diff, or is it just the judge model being the judge model — noisy, inconsistent, scoring the same output differently on different days? Right now, every mainstream eval tool makes a human answer that question by eyeballing a before/after comparison. Nobody has taught the gate itself to tell the difference.

## The Gap

A Medium walkthrough on promptfoo's GitHub Action shows the whole workflow in practice: eval suites run automatically on prompt-file changes, and the Action hands the reviewer a before/after comparison to read by hand. That's not a fringe setup — a dev.to comparison piece surveying promptfoo, DeepEval, LangSmith, and Braintrust describes all four as "offering varying degrees of regression detection, with some relying on manual diffs or experiment tracking." Manual diff-reading isn't an edge case in this space; it's the default.

Dig into the two most widely used CI-native tools specifically and the gap gets sharper. Both promptfoo (its fail-on-threshold CLI flag) and DeepEval (`assert_test()`) gate on a single fixed threshold set by a human. Neither has a documented feature for comparing a new score against a stored baseline distribution with statistical tolerance for ordinary judge-score noise. A Langfuse guide goes further and names the omission directly, framing baseline-diff-with-tolerance as a custom CI step a team has to build themselves — not something that ships. One source states the exact shape of the problem: a gate set at 0.7 scoring 0.71 today and 0.68 tomorrow, with nothing in the tool telling you whether that's drift or noise.

This is a PARTIAL gap, not a wide-open one — the tools themselves are real, mature, and widely adopted. The piece that's missing is narrow and specific: nobody has wired statistical noise tolerance into the actual pass/fail decision.

## The Project

The fix doesn't require replacing any of these tools — it sits on top of them. A calibration layer intercepts the CI eval gate's decision point (promptfoo, DeepEval, LangSmith, or Braintrust) and replaces "is this score above the threshold?" with a better question: "is this score outside the range this exact case normally produces anyway?"

It works by maintaining a rolling distribution of historical baseline reruns for each eval case — periodically rerunning cases with no code change to find out what their natural noise band actually looks like. A simple statistical interval estimator (no new model needed) turns that distribution into an expected noise range per case. When a new CI run comes in, the layer classifies the result three ways: within-noise (auto-pass, no human needed), likely real regression (flagged for review, with the confidence behind the flag shown), or inconclusive (not enough baseline samples yet to say). Every flagged regression ships with a report annotation showing the statistics behind the call, so a reviewer sees the evidence, not just a verdict.

The MVP targets promptfoo first, since its JSON CI artifact format is the most mature and well-documented: a nightly rerun job to build each case's baseline distribution, an interval-based classifier that replaces the fixed-threshold check, and validation against a real team's eval history — rerunning previously-flagged PRs with no code change to see whether they'd fail again, then confirming the calibrated layer correctly reclassifies the noise-driven ones.

## Tangible Impact

**Population**: engineering teams using promptfoo's, DeepEval's, LangSmith's, or Braintrust's CI eval-gate feature on prompt-touching pull requests — a concrete, named subset of the roughly 51% of companies surveyed in LangChain's 2024 State of AI Agents report that run agents in production, specifically those already past the first step of having any CI eval gate at all (a prerequisite this project doesn't try to solve).
**Mechanism**: A fixed-threshold gate treats ordinary judge-score noise as indistinguishable from a real regression, so teams either loosen the threshold until it stops catching anything real, or leave it tight and spend reviewer time reading inconclusive diffs on every PR. A calibrated noise-tolerant layer removes the noise-only false alarms automatically, so human attention goes only to diffs the statistics actually flag as likely real — shrinking both wasted review time and the temptation to disable the gate out of fatigue.
**Measure**: rate of CI-gate failures attributable purely to score noise (measured by rerunning a sample of "failed" PRs with no code change and checking if they'd fail again), before vs. after adoption, targeting near-zero false noise-flags; reviewer time spent per week reading eval diffs that turn out to be noise; time-to-merge for prompt-touching PRs, expected to drop once noise-only blocks stop occurring.

## Try It

A companion Claude Code skill hasn't been written for this idea yet (it's still tagged `Format: BOTH`, awaiting a skill-synthesis pass), but the idea file already sketches the skill angle precisely: a developer staring at a CI-flagged regression (say, a score drop from 0.71 to 0.68) pastes the current score, a handful of historical baseline rerun scores for that same eval case, and the gate's configured threshold, and gets back a classification — within-noise, likely regression, or inconclusive — with the computed noise band and a one-line explanation. That's a manual, one-shot sanity check for a single flagged diff, distinct from the full project's always-on calibration layer wired into every CI run automatically. Check back on this repo's `skills/` directory for when that gets built.

## The honest caveat

This is a PARTIAL gap, not a greenfield one, and the idea file says so plainly: if promptfoo or DeepEval ship a native baseline-tolerance feature — plausible, since the gap is now explicitly named in public writeups — a standalone layer's value narrows fast to teams that haven't upgraded or use a different tool. There's also a real cold-start problem: a noise band built from too few baseline reruns is unreliable, so an "inconclusive" classification has to exist and be honored rather than papered over with thin data. Teams with low PR volume on prompt-touching changes may simply never accumulate enough history to get a useful estimate. And judge-score noise isn't static — if the judge model itself changes, the "true" noise band can silently drift without the layer knowing why, which edges right up against (but is distinct from) the separate judge-drift-attribution problem covered elsewhere in this project's idea backlog.

---

Surfaced from `research/2026-11-20-llm-evaluation-observability-ii.md`, pattern `P6`.
