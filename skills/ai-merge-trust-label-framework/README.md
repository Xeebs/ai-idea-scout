# AI Merge Trust Label Evaluator

A paste-in prompt for any AI chat tool. It takes a pull request diff and your team's merge-trust policy, and returns a one-shot recommendation — LABEL, DO NOT LABEL, or ESCALATE — for whether that PR qualifies for an "ai-merge-safe"-style trust label, with full reasoning. It does not apply any label, merge anything, or call any API — it's a judgment you (or your CI) sanity-check and act on yourself. Use it to test and tune your trust-label rules against real PRs before building the always-on automated version.

## When to use this
Use it when you have a pull request — especially one opened or heavily edited by an AI coding agent (Claude Code, Copilot, Cursor, Devin, etc.) — and want to know whether it meets your team's criteria for graduated-autonomy merging, before wiring up full automated labeling or auto-merge. This is the "try the rule on one PR by hand" step, not the continuous CI gate.

## What to give it

**Data source: Manual.** You paste everything — this does not connect to GitHub, your CI system, or a coverage tool on its own. If you want it to consider CI results or coverage deltas, paste those as text too.

1. **The diff** — every changed file's path, lines added/removed, and enough of the content that the kind of change is clear (dependency bump, docs, config, test, source logic, CI/workflow file, schema/migration, or anything touching auth/payments/secrets).
2. **Your policy** — the rules that qualify a PR for your trust label. Plain language is fine, e.g.:
   > "Only files under docs/, package.json, and tests/ qualify. Max 150 changed lines. Any non-test source file changed needs a matching test file changed too. No logic changes allowed, only deps/docs/config/test-only."

   If you don't have a policy yet, ask for the default one below and tell it to use that.
3. *(Optional)* Test/CI status or a coverage delta number, if your policy needs it and it isn't obvious from the diff.

**Default policy**, if you have none:
- Scope: `**/*.md`, `**/package*.json`, `**/*.lock`, `**/deps/**`, `tests/**` only.
- Size: ≤5 files and ≤150 changed lines total.
- Test coverage: every changed non-test source file needs a matching changed test file.
- Change type: dependency bumps, docs, config, and test-only changes allowed; any logic change always requires human review.

## The prompt

Paste this whole block into your AI chat tool, then paste your diff and policy where indicated:

```
You are evaluating a pull request for a merge-trust label decision. Follow this procedure exactly.

STEP 1 — Canonicalize my policy into four checks: Scope, Size, Test coverage, Change-type allowlist.
If my policy is silent on one of these, mark that check UNKNOWN rather than guessing a threshold.

STEP 2 — Parse the diff I give you into a per-file table: path, lines added/removed, and an
inferred change type (dependency bump / docs / config / test / source logic / CI-workflow /
schema-migration / auth-payment-secrets-related / other).

STEP 3 — Run the four policy checks, AND-gated (all must pass to be LABEL-eligible):
- Scope: every changed path matches an allowed pattern.
- Size: total diff size is within my stated limit.
- Test coverage: every changed non-test source file has a matching changed test file (or I gave
  you a coverage delta that meets my stated threshold).
- Change type: no changed file falls into a category I disallow.

STEP 4 — Independent of my policy, scan for hard-stop risk signals that force ESCALATE even if
all four checks above passed:
- Any file touching auth, authn/authz, payments, billing, secrets, or encryption.
- Any file under a CI/workflow or infrastructure-as-code path (e.g. .github/workflows/**,
  terraform/**, Dockerfile).
- Any deletion or weakening of an existing test (removed test file, fewer assertions, a new
  skip/xfail).
- Any change to the trust-label policy file or merge-automation config itself.
- Any changed path that doesn't match any category my policy defines — treat an unknown path as
  a gap in my policy, not a pass.

STEP 5 — Give me a verdict:
- ESCALATE if any hard-stop signal fired, no matter what the four checks said.
- DO NOT LABEL if no hard-stop signal, but one or more of the four checks is FAIL or UNKNOWN.
- LABEL only if no hard-stop signal and all four checks are PASS with nothing UNKNOWN.

STEP 6 — Output in exactly this format:

## Verdict: LABEL | DO NOT LABEL | ESCALATE

### Policy checklist
| Check | Result | Reasoning |
|---|---|---|
| Scope | PASS/FAIL/UNKNOWN | ... |
| Size | PASS/FAIL/UNKNOWN | ... |
| Test coverage | PASS/FAIL/UNKNOWN | ... |
| Change type | PASS/FAIL/UNKNOWN | ... |

### Hard-stop risk scan
- [none triggered] OR one bullet per triggered signal naming the file and why.

### Draft audit-ledger entry
- Verdict: ...
- Files evaluated: ...
- Checks: ...
- Timestamp: <fill in>

### Disclaimer
This is a one-shot advisory judgment, not an automated action. No label was applied and nothing
was merged. Confirm this verdict yourself before acting on it, especially on ESCALATE or
borderline LABEL results.

RULES YOU MUST FOLLOW:
- Never say you applied a label or merged anything — you only produce a recommendation.
- Never invent diff contents, line counts, or test-coverage numbers I didn't give you — mark the
  check UNKNOWN instead, and let that push the verdict toward DO NOT LABEL or ESCALATE, never
  toward LABEL.
- Always run the hard-stop scan even if my policy never mentions those categories.
- If my policy explicitly conflicts with a hard-stop rule (e.g. I said CI-workflow changes are
  fine), say so and still ESCALATE — flag it as a policy gap for me to fix, don't silently pick a
  side.

My policy:
<paste your policy here, or say "use the default policy">

My diff:
<paste your diff / changed-file list here>
```

## What you get back
A verdict (LABEL / DO NOT LABEL / ESCALATE), a table showing exactly which of your four policy checks passed, failed, or came back unknown and why, a list of any hard-stop risk signals found regardless of your policy, a draft audit-ledger entry you can paste into your own records or into the logs of an automated merge-trust Action once you build one, and a disclaimer that nothing was actually labeled or merged.

## What this is not
This is not the always-on automation. If you like how the trust rules perform across a handful of real PRs run through this prompt, the next step is wiring the same rule set into a CI check or GitHub Action that runs on every PR automatically, with a kill switch (removing the label halts any pending auto-merge) and a persistent audit ledger — that's a separate piece of infrastructure, not something a pasted prompt should ever be trusted to run unsupervised.
