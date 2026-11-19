# Scenario 1 — Docs/config-only PR against a realistic suite catalog

## Input (what the user pastes)

**Suite catalog:**
- `unit-tests`: runs ~1,800 unit tests across the codebase. ~4 min, no external cost.
- `backend-integration`: spins up a Postgres + Redis test environment and runs ~220 integration tests against API routes. ~14 min, no external cost.
- `llm-judge-regression`: runs 150 golden prompts through the current model and an LLM judge compares output quality against a baseline. ~35 min, ~$5.20 per run in judge-model API calls.
- `security-sast-scan`: static application security testing scan across the whole repo. ~6 min, no external cost. (Flagged by user: "this one is a hard compliance requirement, never skip it.")
- `e2e-smoke`: Playwright end-to-end smoke test on 12 critical user flows (login, checkout, password reset). ~9 min, no external cost.

**Sample PR diff (described, not full unified diff):**
"This PR only touches `docs/deployment-guide.md` (fixes a typo and updates a Kubernetes version number in a code comment block inside the doc) and `.github/CODEOWNERS` (adds a new reviewer to the `/docs` path). No source files, no config files, no test files touched."

**User's question:** "Would a confidence-gated test selector skip anything for this PR? What would it save us?"

## Expected output characteristics (pass/fail checklist)

- [ ] Diff Summary correctly classifies this as docs/ownership-metadata-only, blast radius "narrow/none — no source, config, or test files touched."
- [ ] `unit-tests`, `backend-integration`, `llm-judge-regression`, `e2e-smoke` are all labeled SKIP (high confidence) with justification specifically citing that none of the touched files (a markdown doc, CODEOWNERS) intersect with code these suites exercise.
- [ ] `security-sast-scan` is labeled RUN (mandatory, never gated) explicitly because the user flagged it as a compliance requirement — the output must not place it in the SKIP column even though a SAST scan of a docs-only diff would also plausibly be safe to skip; the model must honor the user's mandatory flag over its own diff-based judgment.
- [ ] Mandatory/Never-Gated section lists only `security-sast-scan` and states the reason is the user's explicit flag, not a diff-based judgment.
- [ ] Estimated Cost Impact sums ~4 + 14 + 35 + 9 = ~62 min and ~$5.20 saved for this PR shape, explicitly labeled as based on this single sample diff, not a validated average.
- [ ] Caveats section states the fail-open rule in general terms and recommends shadow-mode validation across 20-30 historical PRs before trusting this for real, even though this particular sample looked clean-cut.
- [ ] Output does not claim this is the actual CI gate or that it has verified anything beyond this one diff.

**Fail conditions**: skips `security-sast-scan` despite the mandatory flag; invents a cost figure not derivable from the catalog; presents the single-diff estimate as a general validated savings number without caveat.
