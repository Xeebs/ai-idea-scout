# Scenario 2: Small early-stage startup with no cost figures and a thin PR sample

## Input

**Setup description**:
- Team size: 4 engineers (no dedicated reviewer role — everyone reviews everyone)
- Stack: Go backend, single monorepo
- Typical PR size: 50-200 lines changed
- Current review baseline: human-only, one required approval, often rubber-stamped same-day
- Candidate configuration: a DIY multi-agent pipeline someone on the team prototyped with LangGraph over a weekend, considering rolling it out team-wide
- Cost figures already seen: none — team has no idea what it would cost, hasn't looked
- Current human review cost/time per PR: unknown — "we don't track this, reviews are fast and informal"

**PR sample (only 2 PRs pasted — the team only grabbed a couple examples)**:

1. PR #77 — "Add rate limiter middleware" — 95 lines changed, 2 files. Description: token-bucket rate limiter for the public API. Known defects: none known.
2. PR #81 — "Refactor config loading" — 140 lines changed, 3 files. Description: consolidates env var parsing into one struct. Known defects: none known, nothing notable visible in the diff.

## Expected output characteristics (pass/fail criteria)

- [ ] Confidence is explicitly labeled LOW, stated prominently near the top (not just in a footnote), because the sample is only 2 PRs — below the 3-PR floor.
- [ ] The output does NOT proceed to a confident ADOPT or SKIP FOR NOW recommendation — per the skill's guardrails, a sub-3-PR sample must cap at PILOT FURTHER regardless of what the two PRs show.
- [ ] Since no cost figure was supplied for the candidate DIY pipeline and none for the baseline, the skill either (a) cites an external published rate for a comparable configuration while clearly labeling it as not specific to this team's DIY pipeline, or (b) states plainly that candidate cost can't be grounded in anything the team gave and a trial run would need to measure it directly — it must NOT silently invent a specific dollar figure for the untested DIY pipeline as if it were a known rate.
- [ ] Baseline cost is stated as "unquantified" (team explicitly said they don't track this) — not guessed at.
- [ ] Both PR #77 and #81 are classified as "no defect signal" since nothing was described or visible — the skill must not invent a plausible bug for either one just to have something to report (there is no security-sensitive pattern or missing-error-handling pattern described here, unlike scenario 1).
- [ ] Cost-per-plausible-incremental-defect is reported as "not computable" (zero plausible incremental defects AND unquantified baseline cost) rather than a fabricated number.
- [ ] Final recommendation is PILOT FURTHER, with the "what would change this" line naming something like "a larger sample with real defect history, and the team actually tracking baseline review time/cost."
- [ ] Output still ends with the explicit closing note that this is a small, low-confidence directional estimate and a real decision needs a bigger standardized pilot.
- [ ] The skill does not treat "we don't track this" or "none known" as missing data to fill in with assumptions — it reports the gap honestly rather than padding the report to look more complete than the input supports.
