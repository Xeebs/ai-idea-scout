# Track Record Gate: Historical-Risk-Conditioned PR Autonomy Check

A paste-into-any-AI-tool prompt that gives you a one-shot, evidence-based recommendation on whether a single AI-agent-authored pull request is safe to auto-approve/auto-merge — based on the actual revert/hotfix history of the files it touches, instead of a static "diff under 50 lines" or "low/medium/high" label someone picked by hand.

## When to use this

You (or your team) are running an AI coding agent with some autonomy over PR approval or merging. You're about to decide, for one specific PR, whether it's safe to let it land without a human looking at it. Your current policy is a static rule — a file-path allowlist, a diff-size cutoff, a hand-picked risk tier — and you want a sharper, track-record-based answer before trusting it (or before building a full always-on system that tracks this automatically).

This is a one-time sanity check for a single PR, not a continuously running pipeline. If you find yourself wanting to run this on every PR, that's a sign you want the always-on version of this idea, not this prompt repeated by hand.

## What to hand over

This tool needs two things. If you're working inside a tool with live repo access (e.g., an agent with GitHub CLI/API access), it can pull the history itself — tell it the PR and repo, and let it query `gh api` / `git log` directly. **Connected mode**: GitHub/GitLab's commit and PR history API — a mature, already-available data source most repo-connected tools can already reach.

If you're pasting into a plain chat tool with no repo access, you need to supply this by hand instead — **manual mode**:

1. **The PR diff**, or at minimum the list of files/modules it touches and a one-line description of what kind of change each is (new endpoint, config change, refactor, etc.).
2. **A short history per touched file/module** — for each one, roughly: how many of the last ~20 merges to that file were later reverted or followed by a hotfix, and how recently. Something like: `src/billing/webhook.ts — 1 revert and 1 hotfix in the last 20 changes, most recent 12 days ago` or `src/docs/readme.md — 15 clean changes, no reverts ever`. If you genuinely don't have this for a file, say "no history available" rather than guessing — the tool treats missing data conservatively, never as "probably fine."
3. **(Optional)** your team's existing static policy, e.g. "diffs under 50 lines in `/config` auto-merge," so the recommendation can be checked against it.

## The prompt

Paste this, filling in your own PR details and history:

```
You are acting as a historical-risk-conditioned autonomy gate for one pull request.

PR touches these paths: [list files/modules]
For each, here's the recent outcome history: [paste per-file history, or "no history available" where you genuinely don't have it]
Our current static policy (optional): [e.g. "diffs under 50 lines in /config auto-merge"]

Do this:
1. For each touched path, classify its risk:
   - LOW: zero reverts/hotfixes in the history given, and at least 5 past changes observed.
   - MEDIUM: a revert/hotfix exists but it's older than 90 days, OR fewer than 5 past changes exist.
   - HIGH: a revert or hotfix landed on this path within the last 90 days.
   - COLD START: no history was given for this path at all — do NOT default this to LOW.
2. Roll the PR up to one aggregate risk level using the weakest-link rule: the PR's risk is the HIGHEST risk level found among any touched path.
3. Map that to a verdict:
   - LOW -> Approve autonomously.
   - MEDIUM or COLD START -> Flag for human review.
   - HIGH -> Block / require human review.
4. If I gave you a static policy, say whether your verdict agrees or disagrees with what that policy would have done, and why.
5. Never invent revert/hotfix numbers I didn't give you. If data for a path is missing, say so explicitly and mark it COLD START.

Output as:
## Historical-Risk Gate — PR Recommendation
**Verdict**: [APPROVE AUTONOMOUSLY | FLAG FOR HUMAN REVIEW | BLOCK — HUMAN REVIEW REQUIRED]
**Touched-path risk table**: [path | risk | evidence]
**Reasoning**: [2-4 sentences naming which path(s) drove the verdict]
**Static-policy comparison**: [only if I gave you one]
**Caveat**: This is a one-time, single-PR check, not a continuously updated ledger. If you're running this repeatedly, build the always-on version instead of repeating this by hand.
```

## What you get back

A short markdown report with:
- One clear verdict: approve autonomously, flag for review, or block.
- A table showing each touched file's risk level and the specific evidence behind it (or an explicit "no history available" if that's genuinely the case).
- Plain-language reasoning naming exactly which file drove the decision — a PR with nine safe files and one recently-reverted one should still get flagged, never averaged away.
- A comparison against your existing static policy, if you supplied one, so you can see exactly where the two disagree.
- A caveat reminding you this is a one-shot check, not a substitute for a running system.

## Guardrails this tool follows

- It never treats "no history found" as "probably safe" — missing data is always flagged, never assumed clean.
- It never lets safe files outvote one risky one; the single riskiest touched path decides the PR's verdict.
- It never fabricates revert or hotfix counts you didn't provide (or, in connected mode, that it couldn't actually retrieve).
- It never presents itself as a continuously-updated system — it's a single judgment on the PR you handed it, as of right now.
- It never claims to validate or reproduce any specific vendor's internal benchmark numbers — it's an independent read of the evidence in front of it, nothing more.
