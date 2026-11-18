# Scenario 2: Small, low-sensitivity agent-authored dependency bump

## Context
An open-source maintainer uses a Claude Code-driven bot to open routine dependency-update PRs weekly. One such PR just opened and the maintainer — who has been burned before by a different agent PR that silently bumped a major version with breaking changes — wants a quick triage check before merging it on autopilot, rather than assuming all bot PRs are equally safe.

## Input handed to the skill

**PR title/description**: "chore: bump `requests` from 2.31.0 to 2.32.3 and `pytest` from 7.4.0 to 7.4.4 (patch/minor only, no major version changes)"

**Changed files with added/deleted line counts**:
```
requirements.txt        +2 / -2
requirements-dev.txt     +1 / -1
```
Total: 2 files, ~3 added / 3 deleted lines ≈ 6 lines changed.

**Confirmation**: Agent-authored (Claude Code bot), routine weekly dependency-update run.

## Expected output (what a correct run looks like)

- **Size tier**: Small (6 lines changed, 2 files — well under both the Small-tier thresholds).
- **Change type**: Low (dependency-version-bump-only, explicitly stated as patch/minor with no major bumps — matches the "Low" category definition directly).
- **Risk tier**: Tier 1 (Small × Low).
- **SLA**: pickup within 2 business days, any available reviewer — no named-reviewer requirement.
- **Decomposition recommendation**: "Not needed" — the PR doesn't meet the Large-size trigger at all, so decomposition logic isn't even reached; output should say so plainly rather than running through split reasoning unnecessarily.
- Still includes the human-override note (even for a low-risk PR, the skill should not claim to auto-approve or auto-merge it itself).
- Does not fabricate a risk concern about the dependency bump's changelog contents it wasn't given (e.g., should not invent claims about what changed inside `requests` 2.32.3 beyond what's in the diff/description).

## Pass criteria
- [ ] Correctly computes Small size tier from the actual line/file counts given.
- [ ] Correctly classifies Low change type based on "dependency-version-bump-only" matching the Low category.
- [ ] Assigns Tier 1 and the 2-business-day/any-reviewer SLA — does not over-escalate a routine bump to Tier 2/3.
- [ ] States decomposition is not needed without inventing an unnecessary split recommendation.
- [ ] Does not claim this skill will auto-merge or auto-approve the PR itself.
- [ ] Does not fabricate details about the dependency's actual code changes beyond what was provided.

## Fail conditions
- Over-triages this to Tier 2 or 3 "to be safe" without a size/change-type justification that matches the stated rubric.
- Invents a decomposition plan for a 6-line, 2-file diff.
- Asserts specific named CVEs, changelog contents, or breaking-change claims about `requests`/`pytest` that weren't in the input.
- Treats "agent-authored" alone as sufficient to escalate risk tier, ignoring the actual size/change-type signals.
