---
name: historical-risk-conditioned-autonomy-gate
description: One-shot risk-conditioned approve/flag recommendation for a single AI-agent-authored PR, based on the revert/hotfix track record of the files it touches, rather than a static file-path or diff-size rule. Use before committing to a full always-on ledger-and-gate pipeline.
---

# Track Record Gate: Historical-Risk-Conditioned PR Autonomy Check

## When to use this
A team is running (or piloting) an AI coding agent with some autonomy over PR approval or auto-merge, and is about to decide — for one specific PR — whether it's safe to let the agent's change land without human review. They currently rely on a static rule (file path allowlist, diff-size threshold, "low/medium/high" label chosen by hand) and want a sharper answer: "has this specific code area actually been safe historically, or are we just guessing?" This skill is the single-PR sanity check — the thing you run once, by hand, before deciding whether building a continuously-updated ledger-and-gate pipeline is worth it.

Do not reach for this skill to build or operate the always-on pipeline itself (that's the full project this skill was distilled from); it's for judging one PR at a time.

## Inputs
**Data source**: Connected — GitHub/GitLab PR, commit, and revert history via the GitHub/GitLab API (`gh` CLI or REST API), a mature, already-available connector, when run inside a tool with repo access (e.g., Claude Code with `gh` installed and authenticated). Manual fallback — when run in a plain chat tool with no repo access, the user pastes: (1) the PR diff or a list of touched files, and (2) for each touched file/module, a short history of past merges touching it with an outcome label (clean / reverted / hotfixed-within-N-days) and roughly how long ago each happened.

Required, either way:
1. The PR diff, or at minimum the list of files/paths it touches and what kind of change each is (e.g., "config change," "new endpoint," "refactor").
2. Historical outcome data for each touched path — reverts, hotfixes, or "fix-up" commits that followed a past merge to that path, with approximate recency. If this is genuinely unavailable for a path, say so explicitly rather than guessing.
3. Optional: the team's existing static policy (e.g., "diffs under 50 lines in `/config` auto-merge") so the recommendation can be compared against it.

## Procedure
1. **Extract touched paths.** From the diff or file list, build the set of distinct files/modules the PR changes.
2. **Gather per-path history.** For each touched path:
   - Connected mode: query commit history for that path (`gh api repos/{owner}/{repo}/commits?path={file}`), then check which of those commits were later reverted (a subsequent commit/PR with "revert" in its title referencing it) or followed within a short window (default 14 days, ask if unstated) by a commit whose message suggests a fix-up/hotfix to the same path.
   - Manual mode: use the outcome labels the user supplied directly; do not infer outcomes they didn't state.
   - If no history exists for a path (brand-new file, newly agent-managed area), mark it explicitly `NO HISTORY — cold start`, never default it to clean.
3. **Score each path**, over the most recent 20 changes to it or the last 180 days (whichever is smaller window the data allows):
   - `LOW` — zero reverts/hotfixes in the window, and at least 5 past changes observed.
   - `MEDIUM` — a revert/hotfix exists but it's older than 90 days, OR fewer than 5 past changes exist (thin history).
   - `HIGH` — a revert or hotfix landed on this path within the last 90 days.
   - `COLD START` — zero history found; treat as the conservative default, not as LOW.
4. **Roll up to a PR-level verdict** using the weakest-link rule: the PR's aggregate risk is the *highest* risk level among all touched paths (one risky file is enough to flag the whole PR).
5. **Map aggregate risk to a recommendation**:
   - `LOW` → Approve autonomously.
   - `MEDIUM` or `COLD START` → Flag for human review (reason: thin or absent track record).
   - `HIGH` → Block / require human review (reason: recent revert/hotfix history in a touched area).
6. **Compare against the stated static policy**, if one was given, and call out explicitly if the two disagree (e.g., "the static rule would auto-merge this; the historical gate would not, because `src/billing/webhook.ts` was hotfixed 12 days ago").

## Output format
A single markdown report:

```
## Historical-Risk Gate — PR Recommendation

**Verdict**: APPROVE AUTONOMOUSLY | FLAG FOR HUMAN REVIEW | BLOCK — HUMAN REVIEW REQUIRED

**Touched-path risk table**
| Path | Risk | Evidence |
|------|------|----------|
| ... | LOW/MEDIUM/HIGH/COLD START | e.g. "3 reverts in last 20 changes, most recent 18 days ago" or "no history found" |

**Reasoning**: 2-4 sentences naming the specific path(s) that drove the verdict (weakest-link rule) and the evidence behind it.

**Static-policy comparison** (only if a static rule was provided): agrees / disagrees, and why.

**Caveat**: This is a one-time, single-PR check, not a continuously updated ledger — it reflects history as of today only. A team relying on this repeatedly should build the always-on gate instead of re-running this by hand each time.
```

## Guardrails
- Never mark a path `LOW` risk from absence of data — absence of history is `COLD START`, treated the same as `MEDIUM` (flag), never as safe.
- Never fabricate revert/hotfix history. If connected mode can't retrieve history for a path, or manual mode wasn't given any, say so explicitly in the Evidence column instead of inventing a plausible-sounding number.
- Never let a LOW-risk majority outvote a single HIGH-risk touched path — the weakest-link rollup is mandatory, not a suggestion.
- Never present this one-shot check as equivalent to the continuously-updated ledger-and-gate pipeline it's a precursor to; the Caveat line is required output, not optional.
- Never claim this reproduces or validates any vendor's internal eval numbers (e.g., kodus-ai's self-reported PR #2193 results) — this is an independent judgment on the specific PR in front of you, nothing more.
