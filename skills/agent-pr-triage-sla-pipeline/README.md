# Agent PR Triage & SLA Recommender

A paste-into-any-AI-chat-tool prompt that gives you a quick risk tier, recommended review SLA, and (if it's oversized) a concrete split recommendation for one specific agent-authored pull request — before it enters, or while it's stuck in, your team's review queue.

## Why this exists

Agent-authored PRs (from Copilot, Devin, Claude Code, Cursor, or similar) reportedly sit much longer before a human picks them up for review than human-authored PRs, and contain more defects on average — but most teams still apply one flat review SLA to every PR regardless of how big or risky it actually is. That means a 20-line config change and an 800-line multi-module feature wait in the same queue under the same rule, and nothing structurally discourages oversized, high-risk agent PRs from happening in the first place.

This prompt is the one-shot version of that fix: point it at one PR, get back a risk tier, a risk-calibrated SLA recommendation, and (when warranted) a concrete suggestion for how to split it into smaller, independently reviewable pieces.

**Data source**: Connected — this is designed to run against your GitHub/GitLab Pull Requests API data (diff stats, file list, PR metadata). If you're using this inside a tool that can fetch that for you (e.g., Claude Code with `gh` CLI access), let it fetch directly. Otherwise, gather the inputs below yourself and paste them in.

## What to hand it

Before running this prompt, gather:

1. **Per-file line change counts** for every file in the PR's diff (added/deleted lines per file) — or just paste the full diff text and let the AI count.
2. **The PR's title and description** — what it's for (feature, refactor, config change, bugfix, schema migration, dependency bump, etc.).
3. **Confirmation the PR is agent-authored** (fully or substantially) — this prompt's SLA calibration assumes the agent-PR review-bottleneck context; for a human-authored PR, say so instead and the AI will tell you to use your normal process.

## The prompt

Paste this, filling in the bracketed parts with your actual PR data:

```
You are triaging one pull request for review-SLA and risk purposes. This PR is agent-authored (or substantially agent-generated).

PR title/description: [paste]
Changed files with added/deleted line counts (or full diff): [paste]

Do the following:

1. Compute total lines changed and number of files touched. Classify size as:
   - Small: <100 lines changed AND <5 files
   - Large: >400 lines changed OR >15 files
   - Medium: anything in between

2. Classify change type as the HIGHEST-sensitivity category that applies:
   - Low: config-only, docs-only, dependency-bump-only, test-only
   - Medium: internal refactor/logic change, no public API or schema change
   - High: touches a public API contract, database schema/migration, auth/session/permission logic, payment/billing code, or security-sensitive paths

3. Assign a risk tier from this matrix (size rows, change-type columns):
                 Low        Medium      High
   Small         Tier 1     Tier 1      Tier 2
   Medium        Tier 1     Tier 2      Tier 3
   Large         Tier 2     Tier 3      Tier 3

4. Assign the SLA for that tier:
   - Tier 1: pickup within 2 business days, any reviewer
   - Tier 2: pickup within 1 business day, a named reviewer who owns these files
   - Tier 3: pickup within 4 business hours, a named senior/lead reviewer, no auto-merge regardless of CI status

5. Decide whether to recommend splitting this PR: only if size is Large AND risk tier is 2 or 3. If triggered, group the changed files by module/directory boundary and propose 2-4 split PRs, each with its file list and a one-line reason it's independently reviewable. Explicitly flag any files that are too tightly coupled to separate (e.g., a migration and the code that depends on it) and keep those together. If the change genuinely doesn't split cleanly, say so plainly instead of forcing an artificial split.

6. Note that industry figures claiming agent-authored PRs take several times longer to review and have higher defect rates are unverified secondary-aggregator estimates — cite them only as background for why tiered SLAs matter, never as a precise prediction for this PR.

Output in this exact structure:

## PR Triage: <title/identifier>

**Risk Tier**: <1/2/3> — <justification>
**Recommended Review SLA**: <pickup window> · Reviewer requirement: <who>
**Decomposition recommendation**: <"Not needed — <reason>" or the numbered split list with file groups, rationale, and any keep-together exceptions>
**Human override**: this is a recommendation for a human reviewer/lead to confirm, adjust, or reject — not a blocking gate.

Never fabricate file contents or diff stats you weren't given — if something's missing, say what and ask for it instead of guessing.
```

## What you get back

A short structured readout: a risk tier (1/2/3) with the size + change-type reasoning behind it, a recommended review SLA (pickup-time window and who should review it), and — only when the PR is both large and risky enough to warrant it — a concrete proposal for how to split it into smaller PRs along real module boundaries, with any tightly-coupled files flagged to keep together.

## What this is not

This is a one-shot advisory check for a single PR, run by a human when they need it — it does not watch your repo, auto-label incoming PRs, start a real SLA clock, or block merges. If your team wants that always-on version (automatic risk scoring and routing on every agent-authored PR as it opens, with breach tracking over time), that's a separate piece of infrastructure, not this prompt.

## Guardrails

- Don't treat the output as self-enforcing: it's advisory input for a human, not an automated gate.
- Don't let it recommend splitting files that are genuinely coupled (e.g., a migration and its dependent code) — if it does, override it; that's a judgment call it can get mechanically wrong.
- Don't use this on a PR you know is human-authored without saying so — the SLA calibration assumes the agent-authored review-bottleneck context.
- Don't treat the "4-5x slower pickup" / "1.7x more defects" figures as precise facts about this specific PR — they're background context from unverified secondary sources, not a measurement of your team.
