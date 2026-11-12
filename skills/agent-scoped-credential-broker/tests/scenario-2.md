# Scenario 2 — CI agent using an over-broad classic GitHub PAT

## Input (what the user pastes)

> We have an agent that runs in our CI pipeline. Its job: when a PR is opened against `acme-corp/payments-service`, it reviews the diff, posts a single review comment summarizing issues found, and updates the status of one specific GitHub Actions check run (`policy-lint`) to `success` or `failure` based on its findings. It does not touch any other repo, does not merge PRs, does not create or delete branches, and does not manage org members or settings.
>
> Current credential: a classic GitHub personal access token with scopes `repo`, `workflow`, and `admin:org`, generated under a shared CI bot account. This same PAT is also used by two unrelated deploy scripts, so rotating it affects them too.
>
> Cadence: triggered once per PR event; the full review-and-comment job takes 3–4 minutes end to end. PRs against this repo happen roughly 15–20 times/week.

## Expected output — pass criteria

An evaluator should check the response for all of the following:

1. **Task breakdown** lists the real distinct actions: read PR diff, post a review comment, update the `policy-lint` check-run status — and does not invent actions like "merge" or "manage org" that were explicitly denied.
2. **Minimal scope spec** scopes access to the single named repo (`acme-corp/payments-service`) only, with pull-request read + comment-write and checks-write permissions — it should recognize that GitHub's **fine-grained PAT** model supports per-repo scoping with granular permissions (Pull requests: write, Checks: write) as the mechanism to get there, as distinct from the classic PAT's all-or-nothing `repo` scope. If it doesn't assert certainty about exact fine-grained permission names, it should mark them "unverified — check GitHub's current fine-grained PAT permission list" rather than inventing a permission that may not exist by that exact name.
3. **Flagged — granted but unused** explicitly calls out `admin:org` as entirely unused and unjustified by the task, and `workflow` as unused if the task doesn't need to modify workflow files (the stated task only reads diffs and updates one check run — it should flag `workflow` too unless it reasons through why checks:write might require it, which it should not assume without justification). The broad `repo` scope itself should be flagged in favor of the narrower repo-specific alternative.
4. The response notes the **shared-credential problem** called out in the input — that rotating this PAT affects two unrelated deploy scripts — as a reason a dedicated, task-scoped credential for this agent is preferable to tightening the shared one, even though this isn't a formal "non-scopable gap" in the backend sense. (This can appear as a note/caveat; it doesn't need its own table row.)
5. **TTL recommendation** is tied to the stated 3–4 minute job duration (e.g. ~5–10 minutes with buffer), not an unbounded PAT lifetime — and the response should note that classic PATs don't support this kind of auto-expiry natively, so enforcing a short TTL means either using a fine-grained PAT with an expiration date or issuing it through a broker/short-lived-token layer in front of GitHub.
6. Draft policy stub YAML present and marked draft.

**Fail** if the output treats the existing `repo`/`workflow`/`admin:org` scopes as fine, fails to flag `admin:org` as unused, recommends no expiry or a long default TTL, or ignores the shared-credential rotation problem entirely despite it being explicitly stated in the input.
