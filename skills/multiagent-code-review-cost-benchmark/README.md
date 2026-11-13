# ReviewMeter Quick-Check: Multi-Agent Code Review Cost/Defect Estimator

A self-contained prompt template that takes your team's description of its current PR-review setup plus a small sample of your own real recent PRs, and produces a quick, honestly-caveated cost-vs-defect-catch estimate comparing a candidate AI code-review configuration (Claude Code's native multi-agent review, CodeRabbit, Qodo, a DIY multi-agent pipeline, or plain single-pass LLM review) against your current baseline — ending in a directional ADOPT / PILOT FURTHER / SKIP FOR NOW call. Paste the block below into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with your own setup details and PR sample.

## When to use this

Use this when:
- You're deciding whether to turn on or expand an AI/multi-agent code-review tool on a repo and want a fast gut-check before spending budget or engineering time on a real trial.
- You've seen a vendor's cost/accuracy claims (or an informal blog post) and want to sanity-check them against your *own* recent PRs instead of just trusting the marketing numbers.
- You want to know roughly whether it's even worth running a bigger, standardized benchmark before you invest the time to set one up.

This produces a **one-time directional estimate from a small hand-picked PR sample you provide**, not a validated benchmark and not a running tool. It does not connect to GitHub, GitLab, CodeRabbit, or Qodo — you pull your own PRs (e.g. with `gh pr diff`) and paste them in. If the estimate looks promising or is close, the right next step is a larger, standardized pilot or benchmark run — not a final purchasing decision based on this alone.

This is not the right tool if you want to actually build or configure a multi-agent review pipeline — that's separate infrastructure work, not an estimate.

## What to hand over

This is entirely manual — you describe your own setup and paste your own PR sample; nothing is fetched automatically. There is no live connector into GitHub/GitLab/CodeRabbit/Qodo here; if you want real PR content, pull it yourself first (e.g. `gh pr diff <N>`, `gh pr view <N>`) and paste the output in.

Required:
1. **Setup description**: team size, primary language/stack, typical PR size (roughly how many lines change per PR), your current review baseline (human-only, or a specific tool already in use), and the candidate configuration you're evaluating (e.g. "Claude Code native multi-agent review," "CodeRabbit," "Qodo," "a DIY multi-agent pipeline," or "single-pass LLM review").
2. **3-10 real recent PRs from your own repo**: for each, the diff (or a representative excerpt if it's huge), the PR description, and — importantly — any defects actually found for that PR, whether by a human reviewer, CI, or discovered after merge. If a PR has no known defects, say so explicitly rather than leaving it blank.

Strongly recommended (if you skip these, say so — the output will note reduced confidence or an unquantifiable figure):
3. **Any cost numbers you've already seen** for your candidate configuration (vendor page, blog post, your own trial), so the estimate uses a number you're actually evaluating rather than a generic external one.
4. **Roughly how much time/cost your current human review takes per PR**, if you know it — without this, baseline cost can't be quantified.

## The prompt

Paste this, filling in your own details and PR sample where marked:

```
You are producing a quick, honest cost-vs-defect-catch estimate for whether my team should adopt an AI/multi-agent code-review configuration, based on a small sample of my own real PRs. This is a directional gut-check, not a validated benchmark.

MY SETUP:
- Team size: [ ]
- Stack/language: [ ]
- Typical PR size: [ ]
- Current review baseline: [human-only / name of existing tool]
- Candidate configuration I'm evaluating: [e.g. Claude Code native multi-agent review / CodeRabbit / Qodo / DIY multi-agent pipeline / single-pass LLM review]

ANY COST FIGURES I'VE ALREADY SEEN (optional):
[vendor number, blog post figure, or "none - use the most recent published range you can cite for this exact configuration, and tell me the source"]

MY CURRENT REVIEW COST/TIME PER PR (optional):
[e.g. "~45 min of a senior engineer's time" or "unknown"]

MY PR SAMPLE (3-10 real PRs from my own repo):
PR 1: [diff or excerpt] / [description] / [known defects, or "none known"]
PR 2: [...]
[... up to 10]

Do the following:

1. Echo my setup back in one line so I can correct anything before you proceed.

2. Check sample sufficiency: fewer than 3 PRs = cap confidence at LOW and say so immediately, not at the end. 3-5 PRs = MEDIUM. 6-10 = still MEDIUM, not HIGH - tell me HIGH confidence needs a full benchmark run, not this.

3. For each PR, record lines changed, files touched, and a one-line complexity note.

4. Estimate per-PR cost under my candidate configuration. Use my own cost figure if I gave one; otherwise cite the most recent published rate you can find for that exact configuration (e.g., publicly reported ranges for Anthropic's native multi-agent review have cited roughly $15-25 per review as of early 2026, scaling with PR size) and say explicitly that it's an external, reported figure, not something measured from my data.

5. Estimate baseline cost per PR using my own time/cost figure if given. If I didn't give one, say plainly "unquantified" for that PR rather than guessing a number.

6. For each PR, classify defect-catch delta using ONLY what I actually gave you - never invent a bug I didn't mention or that isn't visible in what I pasted:
   - "Already caught by baseline" - a defect I said my current process already found.
   - "Plausible incremental catch" - something visible in the diff I pasted (missing null check, unhandled error path, security-sensitive pattern like unsanitized input reaching a query/shell call) that I did NOT say my current process caught, and that's the general shape of issue multi-agent review is reported to be stronger at catching. Mark as "plausible," never "confirmed."
   - "No defect signal" - nothing known or visible.

7. Build the aggregate table and a cost-per-plausible-incremental-defect figure (or say it's not computable if baseline cost is unquantified).

8. Give me ONE recommendation: ADOPT, PILOT FURTHER, or SKIP FOR NOW, with one sentence why, plus the single fact that would flip it.

9. Always close by telling me this is a small-sample directional estimate and that a real decision should rest on a larger standardized pilot (20+ PRs minimum) or a dedicated benchmark run against my own repo history, not this output alone.

Output in exactly this structure:

# Multi-Agent Code Review Quick-Check

**Setup**: [one line]
**Sample size / confidence**: [N PRs - LOW/MEDIUM]

## 1. Per-PR Estimate
[table: PR | Lines/Files | Candidate cost est. (cite source) | Baseline cost (or "unquantified") | Defect status]

## 2. Aggregate
- Total estimated candidate-config cost across sample
- Total baseline cost across sample (or "unquantified - N of M PRs had no baseline figure")
- Plausible incremental defects (count, listed by PR)
- Estimated cost-per-plausible-incremental-defect (or "not computable")

## 3. Recommendation
**[ADOPT / PILOT FURTHER / SKIP FOR NOW]** - [one sentence]
**What would change this**: [the single fact that flips it]

## 4. What this estimate is not
[state plainly: a directional read from a small hand-picked sample and externally-cited rates, not a measured benchmark; recommend a larger pilot/benchmark before any purchasing or rollout decision]

Rules you must follow:
- Never state a defect as caught/missed unless it's explicitly in what I gave you.
- Never present an external cost rate as if it were measured from my own PRs - always name the source and date.
- Never give ADOPT or SKIP FOR NOW off fewer than 3 PRs - cap at PILOT FURTHER with a low-confidence note.
- Never compute cost-per-defect when baseline cost is entirely unquantified - say it's not computable instead.
- Never let this replace a real benchmark - always close with the "this is directional, run a bigger pilot" note.
- Never fabricate PR content (lines, files, defects) beyond what I actually gave you.
```

## What you get back

A markdown report: your setup echoed back for a quick sanity check, a per-PR table showing estimated candidate-configuration cost against your (possibly unquantified) baseline and a defect-status call for each PR, an aggregate cost-per-plausible-incremental-defect figure, one clear ADOPT/PILOT FURTHER/SKIP FOR NOW recommendation with the single fact that would flip it, and an explicit closing note that this is a directional estimate from a small sample — not a substitute for a real standardized benchmark run.

## Guardrails — what this will never do

- Claim a defect was caught or missed that wasn't explicitly in your sample or defect list.
- Present an external vendor/press cost figure as if it were measured from your own data, without naming the source.
- Give a confident ADOPT or SKIP call off fewer than 3 PRs.
- Compute a cost-per-defect number out of an unquantified baseline.
- Stand in for a real benchmark run — every output ends with the "this is directional" caveat.
- Invent PR details beyond what you actually pasted.

## Limits

This is a one-time, small-sample directional estimate from PRs you hand over once — it does not connect to GitHub/GitLab/CodeRabbit/Qodo, does not run continuously, and is capped at MEDIUM confidence even at its best (10 PRs). If you want a validated, apples-to-apples number across review configurations, the right next step is a larger standardized benchmark run against your own PR history (ideally 20+ PRs with confirmed ground-truth defects) — this prompt is the fast gut-check that tells you whether that investment is worth making, not a replacement for it.
