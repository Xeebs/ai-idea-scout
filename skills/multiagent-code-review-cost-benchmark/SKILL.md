---
name: multiagent-code-review-cost-benchmark
description: Takes a team's description of their current PR-review setup plus a small sample of real recent PRs and produces a quick, honestly-caveated cost-vs-defect-catch estimate comparing their candidate multi-agent/AI code-review configuration against their current baseline, ending in a directional adopt/pilot/skip recommendation. Use when a team is deciding whether to adopt or expand AI-assisted code review and wants a fast gut-check before running a full benchmark or committing to a paid rollout.
---

# ReviewMeter Quick-Check: Multi-Agent Code Review Cost/Defect Estimator

## When to use this
Reach for this when a team lead or engineering manager says something shaped like "should we turn on Claude Code's multi-agent review / CodeRabbit / Qodo for this repo," "is multi-agent review worth the extra token cost over single-pass," or "we're about to pilot an AI code reviewer and want a cost/benefit gut-check before committing budget." This produces a **one-time directional estimate from a small hand-picked PR sample**, not a validated benchmark and not a running service. It is explicitly the fast pre-check before the real thing: if the estimate looks promising (or is too close to call), the next step is always a larger, standardized benchmark run (e.g. an independent harness like the "ReviewMeter" project this skill is the companion to, or at minimum a larger trial on the team's own repo) — not a final purchasing decision.

Do not reach for this to actually build, configure, or wire up a multi-agent review pipeline — that is separate runtime infrastructure. This skill only estimates whether it would be worth doing, from evidence the team hands over.

## Inputs
**Data source**: Manual — the user pastes/links a sample of recent PR diffs (or a description of their review setup) for this quick estimate; the full harness's "bring your own repo" mode would need a CONNECTED GitHub API/webhook integration, which is not wired up here and would be a separate build task (per the parent idea's Data Sources field). No API/connector reaches into GitHub, GitLab, CodeRabbit, or Qodo for this skill — a team could pull PRs via `gh pr diff`/`gh pr view` themselves and paste the output in, but that pull is manual, not a live connector this skill owns.

Required:
1. **Setup description**: team size, primary language(s)/stack, typical PR size (lines changed, rough), current review baseline (human-only, or a specific existing tool), and the candidate configuration being considered (e.g., "Claude Code native multi-agent review," "CodeRabbit," "Qodo," "a DIY multi-agent pipeline," or "single-pass LLM review").
2. **A sample of 3-10 real recent PRs** from the team's own repo: diff (or a representative excerpt if huge), PR description, and — critically — any defects that were actually found, whether by human reviewers at the time, by CI, or discovered post-merge. If no defects are known for a PR, say so explicitly rather than leaving it blank.

Strongly recommended (skip only if genuinely unavailable, and say so in the output):
3. **Any published cost figures** the team has already seen for the candidate configuration (vendor page, blog post, internal trial), so the estimate can be grounded in a number the team itself is evaluating rather than a generic external one.
4. **Current time/cost spent on human review per PR**, if known, so the baseline isn't just "free."

## Procedure
1. **Echo the setup** back in one short paragraph (team size, stack, PR size, baseline, candidate config) so the team can correct anything before the estimate proceeds.
2. **Check sample sufficiency up front.** Fewer than 3 PRs: proceed but cap the final confidence label at LOW and say so in the first line of the output, not buried at the end. 3-5 PRs: MEDIUM confidence. 6-10: the practical ceiling for a "quick" estimate — still label MEDIUM, not HIGH, and state plainly that HIGH confidence requires a full benchmark run against historical PR data, not this skill.
3. **For each PR in the sample**, record: lines changed, number of files touched, and a one-line complexity note (e.g., "single-file bugfix," "cross-module refactor touching 6 files," "new feature with new dependency").
4. **Estimate per-PR review cost for the candidate configuration**, grounded in whatever cost evidence is available: use Input #3 if supplied; otherwise use the most recent published range you can cite for that exact configuration (e.g., publicly reported ranges for Anthropic's native multi-agent code review have put cost around $15-25 per review as of early 2026, scaling with PR size — cite this explicitly as an external, vendor/press-reported figure, not a measured one, and say so). Never present an external rate as if it were measured from this team's own data.
5. **Estimate the baseline cost** for the same PR under the team's stated current process: if it's human-only, use the team's own time/cost figure from Input #4 if given; if no figure was given, state plainly that baseline cost is unquantified for that PR rather than inventing a number.
6. **Classify defect-catch delta per PR**, using only what's actually in the pasted diff/description/defect list — never invent a defect the team didn't mention or that isn't visibly present in the diff:
   - **Already caught by baseline**: a defect the team's own record shows was found by the existing process. Multi-agent review gets no credit here even if it would plausibly also catch it.
   - **Plausible incremental catch**: an issue visible in the diff (e.g., a missing null check, an unhandled error path, a security-sensitive pattern like unsanitized input reaching a query or shell call) that the team's own record does NOT show being caught, and that is the general shape of issue multi-agent/fan-out review is reported to be stronger at catching than single-pass (edge cases, cross-file consistency, security patterns) per the external evidence base. Mark this as "plausible," never "confirmed" — this skill is pattern-matching on the diff, not running an actual review.
   - **No defect signal**: PR has no known defects and nothing suspicious is visible in the diff/excerpt provided.
7. **Build the aggregate table and cost-per-incremental-defect figure** (Output format below).
8. **Give one recommendation**: ADOPT (pilot looks clearly favorable on this sample), PILOT FURTHER (mixed or too close to call, or confidence capped at LOW/MEDIUM), or SKIP FOR NOW (candidate config's estimated cost clearly outweighs plausible incremental catch on this sample) — always paired with the one sentence that would change the recommendation (e.g., "if the team's own baseline review time turns out to cost more than $X/PR, this flips to ADOPT").
9. **Always end with the harness pointer**: state explicitly that this is a directional, small-sample estimate, and that a real adoption decision should rest on a larger, standardized run (the ReviewMeter full-harness approach: a bigger PR corpus with ground-truth-labeled defects, run through the actual candidate tool, not a paste-and-estimate skill) — not on this output alone.

## Output format
A single markdown report, in this order:

```
# Multi-Agent Code Review Quick-Check

**Setup**: [team size, stack, typical PR size, baseline, candidate config — one line]
**Sample size / confidence**: [N PRs — LOW (<3) / MEDIUM (3-10)]

## 1. Per-PR Estimate
| PR | Lines/Files | Candidate cost est. | Baseline cost | Defect status |
|---|---|---|---|---|
| ... | ... | ... (cite source of rate) | ... or "unquantified" | already caught / plausible incremental catch / no signal |

## 2. Aggregate
- Total estimated candidate-config cost across sample: [$ or token estimate]
- Total baseline cost across sample: [$ or "unquantified — N of M PRs had no baseline cost given"]
- Plausible incremental defects: [count, listed by PR]
- Estimated cost-per-plausible-incremental-defect: [$ figure, or "not computable — baseline cost unquantified"]

## 3. Recommendation
**[ADOPT / PILOT FURTHER / SKIP FOR NOW]** — [one sentence why]
**What would change this**: [the single fact that would flip the recommendation]

## 4. What this estimate is not
A directional read from [N] hand-picked PRs and externally-cited rates, not a measured benchmark. Any external cost rate used is cited by source and date. Recommend running a larger standardized benchmark (own-repo "bring your own repo" harness mode, if available, or at minimum a 20+ PR pilot) before finalizing a purchasing or rollout decision.
```

## Guardrails
- Never state a defect as "caught" or "missed" unless it is explicitly present in the team's own stated defect list or visibly present in the pasted diff/excerpt — no inventing plausible-sounding bugs to pad the table.
- Never present an external, vendor- or press-reported cost figure as if it were measured from this team's own PRs — always name the source and that it's an external rate (e.g., "publicly reported range, not measured here").
- Never issue ADOPT or SKIP FOR NOW confidently off a sample under 3 PRs — cap at PILOT FURTHER with an explicit low-confidence note whenever sample size is below 3.
- Never compute a cost-per-defect figure when baseline cost is entirely unquantified — state plainly that the figure isn't computable rather than dividing by a guessed number.
- Never let this stand in for the full benchmark harness — every output must end with the explicit pointer that this is a small-sample directional estimate and a larger standardized run is the real decision basis.
- Never fabricate PR content (lines changed, files touched, defects) beyond what the user actually pasted or described.
