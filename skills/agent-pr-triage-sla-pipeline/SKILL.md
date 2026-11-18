---
name: agent-pr-triage-sla-pipeline
description: One-shot risk tier, review SLA, and (if oversized) split recommendation for a single agent-authored pull request. Use when a reviewer or team lead has one specific agent-authored PR stuck or about to enter the review queue and wants a quick triage read instead of a flat org-wide SLA.
---

# Agent PR Triage & SLA Recommender

## When to use this
A reviewer, tech lead, or team lead has one specific pull request authored (fully or substantially) by a coding agent — Copilot, Devin, Claude Code, Cursor, or similar — and needs a fast answer to three questions before it enters or stays in the review queue:

- How risky is this PR, really, relative to the team's other PRs?
- What review SLA (pickup-time window, reviewer seniority) should apply to it specifically, instead of one flat SLA for every PR regardless of size or risk?
- If it's oversized for its risk tier, how should it be split before review rather than after a reviewer has already struggled through it?

This is a one-shot judgment call, not the always-on routing/labeling infrastructure a team would build to apply this automatically to every incoming PR — it's meant to be run by hand on one PR at a time.

## Inputs
**Data source**: Connected — the GitHub/GitLab Pull Requests API (mature) is the intended source: diff stats, files-touched list, and change metadata at PR-open time. In a Claude Code session with the `gh` CLI authenticated, fetch this directly (`gh pr view <url> --json files,additions,deletions,title,body` and `gh pr diff <url> --name-only`) rather than asking the user to paste anything. If `gh` isn't available or the PR is on a platform without an authenticated connector in this session, fall back to asking the user to paste: the PR URL or number, the list of changed files with per-file added/deleted line counts, and the PR title/description stating its intent.

Required before triage can run:
1. Per-file added/deleted line counts for every file in the diff (or the full diff text, from which these can be counted).
2. The PR's stated intent/description (what it's for — feature, refactor, config change, bugfix, migration, dependency bump).
3. Confirmation the PR is agent-authored (or substantially agent-generated) — this skill's SLA calibration assumes the elevated defect-rate and pickup-time context agent-authored PRs carry; for a clearly human-authored PR, say so and recommend the team's normal process instead.

## Procedure
1. **Compute size signals**: total lines changed (additions + deletions) and count of distinct files touched.
   - Size tier = **Small** if total lines changed < 100 AND files touched < 5.
   - Size tier = **Large** if total lines changed > 400 OR files touched > 15.
   - Size tier = **Medium** otherwise.
2. **Classify change type** from the file paths and stated intent (pick the highest-sensitivity category that applies):
   - **Low**: config-only, docs-only, dependency-version-bump-only, test-only changes.
   - **Medium**: internal refactor or logic change with no public API, schema, or external-interface change.
   - **High**: touches a public API contract, a database schema/migration, auth/session/permission logic, payment/billing code, or any file path containing `auth`, `payment`, `billing`, `security`, `migration`, or equivalent for this codebase's conventions.
3. **Assign risk tier** from this matrix (size down the side, change type across):
   | | Change: Low | Change: Medium | Change: High |
   |---|---|---|---|
   | Size: Small | Tier 1 | Tier 1 | Tier 2 |
   | Size: Medium | Tier 1 | Tier 2 | Tier 3 |
   | Size: Large | Tier 2 | Tier 3 | Tier 3 |
4. **Assign the SLA for that tier**:
   - Tier 1: pickup within 2 business days, any available reviewer.
   - Tier 2: pickup within 1 business day, a named reviewer from CODEOWNERS (or the file paths' usual owner) is required.
   - Tier 3: pickup within 4 business hours, a named senior/lead reviewer is required, and the PR may not self-merge or auto-merge regardless of CI status.
5. **Decide whether to recommend decomposition**: trigger a split recommendation if Size tier is **Large** and Risk tier is **Tier 2 or Tier 3** (i.e., large AND not low-sensitivity). If triggered:
   - Group the changed files by top-level directory/module boundary (e.g., `frontend/`, `api/`, `db/migrations/`, a named service directory).
   - Propose 2–4 candidate split PRs, each listing its files and a one-line rationale for why that group is independently reviewable and mergeable.
   - Flag any file that is tightly coupled to another across your proposed split (e.g., a migration file whose corresponding model/ORM change is in a different proposed split) as a "keep together" exception, and merge those into one split.
   - If the files don't cleanly separate into independent modules (e.g., one tightly-coupled cross-cutting change), say so explicitly and recommend NOT splitting rather than forcing an artificial boundary — a human review decision, not a mechanical rule, should win here.
6. **Always add a one-line override note**: these are recommendations for a human reviewer/lead to accept, adjust, or reject — never an instruction to block, auto-close, or auto-merge the PR yourself.

## Output format
```
## PR Triage: <PR title or identifier>

**Risk Tier**: <1/2/3> — <one-line justification citing the size and change-type signals used>
**Recommended Review SLA**: <pickup window> · Reviewer requirement: <any / named CODEOWNER / named senior>
**Agent-authored context note**: <one line — only if the team hasn't calibrated its own pickup-time/defect baseline yet, note that industry figures on agent-PR pickup time and defect rates are unverified secondary-aggregator estimates and the team's own tracked outcomes should be the real benchmark>

**Decomposition recommendation**: <"Not needed — <reason>" OR a numbered list of 2-4 proposed split PRs, each with its file list and one-line rationale, plus any "keep together" exceptions and why>

**Human override**: This is a one-shot recommendation. A reviewer or lead should confirm, adjust, or reject the tier, SLA, and split before acting on it — do not treat this as a blocking gate.
```

## Guardrails
- Never claim the 4.6–5.3x pickup-time or 1.7x defect-rate industry figures as this team's own established facts — they are unverified secondary-aggregator estimates; cite them only as context for why tiered SLAs matter, never as a precise prediction for this specific PR.
- Never recommend a file split that separates a schema migration from the code that depends on it, or any other pairing you can identify as tightly coupled — flag coupling explicitly instead of mechanically splitting by file count or directory alone.
- Never treat this skill's output as self-enforcing — it does not block merges, assign actual GitHub reviewers, or start a real SLA clock; it is advisory input for a human to act on (or for the always-on pipeline version of this idea to automate later).
- Never fabricate file contents, diff stats, or PR metadata you were not given or could not fetch — if the diff or file list is incomplete, say exactly what's missing and ask for it rather than guessing a risk tier from the PR title alone.
- Never apply this skill's agent-authored calibration to a PR you have reason to believe is human-authored — say so and recommend the team's normal (non-agent-specific) review process instead.
