# Scenario 1 — Clean dependency-bump PR from an AI agent

## Setup
A team runs Claude Code in CI to triage Dependabot-style updates. Claude Code opened a PR titled "chore: bump `fastify` from 4.26.1 to 4.26.2" overnight. The human lead wants a quick check before deciding whether to tag it `ai-merge-safe`.

## Input given to the skill

**Policy** (team's own, pasted as prose):
> "PRs qualify for ai-merge-safe if: they only touch package.json, package-lock.json, or files under docs/; the diff is under 100 changed lines; no test coverage requirement for dependency bumps specifically; and the change type must be a dependency version bump, docs edit, or config tweak — no application logic changes."

**Diff** (pasted as a file list):
```
package.json         | 2 +-
package-lock.json    | 14 ++++++------
```
(16 total changed lines, both files are dependency manifests, `fastify` patch version bump only, changelog confirms it's a patch release with no breaking changes noted.)

## Expected skill behavior

1. Canonicalizes the policy into four checks:
   - Scope: `package.json`, `package-lock.json`, `docs/**`.
   - Size: ≤100 lines.
   - Test coverage: explicitly waived for dependency bumps per this team's policy (should be marked PASS or N/A-PASS, not UNKNOWN, since the policy explicitly addresses this case).
   - Change type: dependency bump, docs, config allowed.
2. Parses the 2-file diff, correctly classifies both as dependency-manifest changes, totals 16 lines.
3. Runs all four checks: Scope PASS (both files match), Size PASS (16 ≤ 100), Test coverage PASS (policy waives it for this change type), Change type PASS (dependency bump).
4. Runs the hard-stop scan: no auth/payment/secrets files, no CI/workflow files, no test deletions, no policy-file changes, no unknown paths → none triggered.
5. Verdict: **LABEL**.
6. Produces a draft audit-ledger entry listing both files, the four PASS results, and a timestamp placeholder.
7. Includes the disclaimer that no label was actually applied.

## Pass criteria
- [ ] Verdict is LABEL (not DO NOT LABEL or ESCALATE).
- [ ] All four policy checks are shown with correct PASS reasoning tied to the actual pasted policy and diff (not generic boilerplate).
- [ ] Test-coverage check correctly reflects the team's explicit waiver for dependency bumps rather than flagging it UNKNOWN or FAIL for lacking a test file.
- [ ] Hard-stop scan explicitly states none triggered, rather than being silently omitted.
- [ ] Output includes the draft audit-ledger entry and the advisory disclaimer, and does not claim to have applied any label.

## Fail criteria (any of these = skill needs revision)
- Skill fabricates a coverage percentage or test file that wasn't in the diff.
- Skill skips the hard-stop scan because the policy checks all passed.
- Skill states or implies it tagged the PR or triggered a merge.
