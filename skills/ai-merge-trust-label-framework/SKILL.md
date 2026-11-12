---
name: ai-merge-trust-label-framework
description: Evaluates a pull request diff against a team's merge-trust policy and returns a one-shot LABEL / DO NOT LABEL / ESCALATE recommendation with per-rule reasoning, for teams deciding whether a PR (especially one authored by an AI coding agent) qualifies for an "ai-merge-safe"-style trust label before any auto-merge automation touches it.
---

# AI Merge Trust Label Evaluator

## When to use this
Use this when someone has a pull request — usually one opened or heavily edited by an AI coding agent (Claude Code, Copilot, Cursor, Devin, etc.) — and wants to know whether it's safe enough to tag with a trust label like `ai-merge-safe` under their team's graduated-autonomy merge policy, *before* wiring up full automated labeling/auto-merge. This is the "test the rule design on one PR" step, not the always-on CI gate. Reach for it when someone says things like "is this PR safe to auto-merge," "would this pass our trust-label policy," "should I label this ai-merge-safe," or "help me check this agent PR against our merge rules."

## Inputs
**Data source**: Manual — the user pastes (1) the PR diff or an equivalent file-by-file change list with added/removed line counts, and (2) their trust-label policy, either as prose or a short rule list. There is no connector: this skill never reads a live GitHub PR, CI status, or coverage report on its own — if the user wants that, they paste the relevant CI/coverage output as text too.

Specifically ask for, if not already given:
1. **The diff** — file paths changed, +/- line counts per file, and enough content to judge what kind of change each file represents (dependency bump, docs, config, test, source logic, CI/workflow, schema/migration, secrets/auth/payment-related).
2. **The policy** — the team's rules for what qualifies a PR for the trust label. If they don't have one yet, offer the default policy below and ask them to confirm or edit it before scoring — never silently substitute your own policy and present a verdict as if it were theirs.
3. *(Optional)* Test/CI status or coverage delta, if their policy depends on it and it isn't inferable from the diff.

**Default policy** (used only when the user has none and agrees to it):
- Scope: `**/*.md`, `**/package*.json`, `**/*.lock`, `**/deps/**`, `tests/**` only.
- Size: diff touches ≤5 files and ≤150 changed lines total.
- Test coverage: any changed non-test source file must have a corresponding changed test file in the same diff.
- Change type: dependency bumps, docs, config, and test-only changes allowed; logic changes require human review regardless of size.

## Procedure
1. **Canonicalize the policy** into four checks: Scope, Size, Test coverage, Change-type allowlist. If the user's policy is vague on one of these, mark that check `UNKNOWN (policy silent)` rather than inventing a threshold.
2. **Parse the diff** into a per-file table: path, +/- lines, inferred change type (dependency bump / docs / config / test / source logic / CI-workflow / schema-migration / auth-payment-secrets-related / other).
3. **Run the four policy checks**, AND-gated — all four must pass for the policy side to say LABEL-eligible:
   - Scope: every changed path matches an allowed pattern.
   - Size: total diff size is within the policy's limit.
   - Test coverage: every changed non-test source file has an accompanying test-file change (or the user supplied a coverage delta meeting the policy's threshold).
   - Change type: no changed file falls in a disallowed/high-risk category per the policy.
4. **Run the hard-stop risk scan independent of the policy** — these force ESCALATE even if all four policy checks pass:
   - Any file touching auth, authn/authz, payments, billing, secrets/credentials, or encryption.
   - Any file under a CI/workflow or infrastructure-as-code path (e.g. `.github/workflows/**`, `terraform/**`, `Dockerfile`).
   - Any deletion or weakening of an existing test (fewer assertions, removed test file, `skip`/`xfail` added).
   - Any change to the trust-label policy file or merge-automation config itself (a PR should never be able to loosen the rules that judge it).
   - Any changed path that matches none of the policy's known categories (an "unknown path" is a policy gap, not a pass).
5. **Determine the verdict**:
   - **ESCALATE** — any hard-stop signal fired, regardless of the policy checks' outcome.
   - **DO NOT LABEL** — no hard-stop signal, but one or more of the four policy checks failed or came back `UNKNOWN`.
   - **LABEL** — no hard-stop signal, and all four policy checks passed with no `UNKNOWN`.
6. **Draft an audit-ledger entry** recording: verdict, which checks passed/failed/unknown, the file list evaluated, and a `<timestamp — fill in>` placeholder — formatted so it can be pasted straight into the team's existing ledger or the parent GitHub Action's log once they adopt it.
7. **Always close with the advisory disclaimer** (see Guardrails) — this skill never applies the label or merges anything itself.

## Output format
```
## Verdict: LABEL | DO NOT LABEL | ESCALATE

### Policy checklist
| Check         | Result        | Reasoning |
|---------------|----------------|-----------|
| Scope         | PASS/FAIL/UNKNOWN | ... |
| Size          | PASS/FAIL/UNKNOWN | ... |
| Test coverage | PASS/FAIL/UNKNOWN | ... |
| Change type   | PASS/FAIL/UNKNOWN | ... |

### Hard-stop risk scan
- [none triggered] OR a bullet per triggered signal, naming the file and why.

### Draft audit-ledger entry
- Verdict: ...
- Files evaluated: ...
- Checks: ...
- Timestamp: <fill in>

### Disclaimer
This is a one-shot advisory judgment, not an automated action. No label was applied and nothing was merged. A human should confirm this verdict before acting on it, especially on ESCALATE or borderline LABEL results.
```

## Guardrails
- Never claim to have applied a GitHub label, triggered a merge, or called any API — this skill only produces a text recommendation. The user (or the parent project's GitHub Action) performs any real action.
- Never invent diff contents, line counts, test-coverage numbers, or file purposes the user didn't supply or that can't be inferred from what they pasted — mark the relevant check `UNKNOWN` and let that push the verdict toward `DO NOT LABEL` or `ESCALATE`, never toward `LABEL`.
- Always run the hard-stop risk scan even when the user's policy doesn't mention those categories — a policy's silence on auth/payments/CI files is a gap in their policy, not evidence the PR is safe.
- Never let `LABEL` be interpreted as "merge now" — it means "meets this team's stated trust criteria for this PR, pending human confirmation," full stop.
- Never carry a verdict over between PRs or sessions — each PR gets evaluated fresh against the diff and policy given in that request.
- If the user's policy and the hard-stop list conflict (e.g. their policy explicitly allows CI-workflow changes), say so explicitly and still ESCALATE — flag the conflict as something they should resolve in their policy, don't silently override either side.
