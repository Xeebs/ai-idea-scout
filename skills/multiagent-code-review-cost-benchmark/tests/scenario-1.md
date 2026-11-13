# Scenario 1: Mid-size SaaS team evaluating Claude Code native multi-agent review

## Input

**Setup description**:
- Team size: 14 engineers, 3 backend-focused
- Stack: Python (FastAPI) backend, TypeScript/React frontend
- Typical PR size: 150-400 lines changed
- Current review baseline: human-only, two required approvals per PR
- Candidate configuration: Claude Code's native multi-agent review (considering turning it on for the `backend` repo)
- Cost figures already seen: team saw a blog post claiming "$20/review average" but no internal trial yet
- Current human review cost/time per PR: ~50 minutes combined across both reviewers, blended senior engineer rate ~$75/hr internally estimated by the team lead

**PR sample (5 PRs pasted from `backend` repo, paraphrased for this test)**:

1. PR #482 — "Add bulk CSV export endpoint" — 310 lines changed, 4 files. Description: new `/export/csv` endpoint streaming a DB query to CSV. Known defects: none found by reviewers; found post-merge that the endpoint didn't sanitize a user-supplied `sort_by` query param before interpolating it into a raw SQL `ORDER BY` clause (discovered by a security audit two weeks after merge — a SQL injection risk).
2. PR #486 — "Fix pagination off-by-one" — 22 lines changed, 1 file. Description: fixes a boundary bug in cursor pagination. Known defects: none — reviewers caught it was correct, no post-merge issues.
3. PR #491 — "Refactor auth middleware to support API keys" — 480 lines changed, 7 files. Description: adds API-key auth alongside existing session auth. Known defects: a reviewer flagged in comments (and it was fixed before merge) that the new code didn't expire API keys — team says "caught by our own review already."
4. PR #495 — "Add Celery retry logic for webhook delivery" — 140 lines changed, 3 files. Description: adds exponential backoff retries. Known defects: none known; diff shows the retry loop catches a bare `except Exception` and swallows it without logging, which nobody flagged in review.
5. PR #499 — "Update dependency versions" — 60 lines changed, 2 files (lockfile + requirements). Description: routine dependency bump. Known defects: none known, nothing notable in the diff.

## Expected output characteristics (pass/fail checklist)

- [ ] Confidence is labeled MEDIUM (5 PRs, within the 3-10 band) and this is stated near the top, not buried.
- [ ] Setup is echoed back in one line before the table.
- [ ] The $20/review figure from the team's own blog post is used (or at minimum acknowledged) as the "already seen" cost figure for the candidate configuration, explicitly marked as externally sourced, not measured.
- [ ] Baseline cost per PR is computed from the given 50 min / $75/hr figure (~$62.50/PR) rather than left unquantified, since the team did supply it.
- [ ] PR #482's SQL injection issue is classified as "plausible incremental catch" (it's a security-sensitive pattern, visible in the diff description, and not caught by baseline) — NOT invented beyond what was described, and not claimed as "confirmed caught" by the candidate config (since the config was never actually run).
- [ ] PR #491's API-key-expiry issue is classified as "already caught by baseline" (team explicitly said their own review caught it) — the skill must not give the candidate config credit for this one.
- [ ] PR #495's swallowed-exception issue is classified as "plausible incremental catch" (visible in diff, not caught by baseline, matches the pattern multi-agent review is reported stronger at).
- [ ] PR #486 and #499 are classified as "no defect signal."
- [ ] A cost-per-plausible-incremental-defect figure is computed (2 plausible incremental defects found across the $20×5=$100 candidate cost vs $62.50×5=$312.50 baseline cost, or similar reasonable arithmetic) — not left as "not computable," since both candidate and baseline costs were quantifiable here.
- [ ] Final recommendation is one of ADOPT/PILOT FURTHER/SKIP FOR NOW, with one sentence of reasoning and one sentence naming what fact would flip it (e.g., false-positive rate, or whether the SQL injection would truly have been caught).
- [ ] Output ends with the explicit "this is directional, not a validated benchmark, run a larger pilot" closing note.
- [ ] No fabricated PR content — every claim traces back to what was pasted (no invented 6th PR, no invented defect on #486/#499).
