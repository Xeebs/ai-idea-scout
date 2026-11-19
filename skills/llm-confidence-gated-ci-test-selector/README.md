# LLM Confidence-Gated CI Test-Selector (Design Review)

A paste-in prompt template for deciding whether a "skip CI/eval suites that clearly don't apply to this PR" strategy would actually save your team meaningful cost, and whether it's safe to try. You give it a sample PR diff and a description of your test suites; it gives you back a per-suite run/skip recommendation, a cost estimate, and a safety-first default. This is a one-time design review, not something that runs automatically in your pipeline — you paste, read the output, and decide whether to build or buy the real automated version.

## When to use this

Use this when your team runs expensive test or eval suites on every pull request — especially slow or costly ones like LLM-as-judge regression checks, agent-behavior evals, or large end-to-end suites — and you're burning CI time and money re-running everything even on changes that obviously can't affect most of those suites (a README edit, a comment fix, a one-line config tweak). You suspect a smarter, diff-aware gate could skip the suites that clearly don't apply while still running everything when it's not sure — but before building that gate as real CI infrastructure, you want a sanity check on whether it would actually help and what it would look like.

This is not for teams with fast, cheap CI suites where this tradeoff isn't worth the complexity, and it's not a replacement for actually running the gate continuously — it's a one-shot proposal review.

## What to hand over

**Data source: Manual.** You paste two things directly into the chat:

1. **A sample PR diff** — a real pull request's diff (unified diff format is fine, or just describe which files changed and what kind of change it was: docs, logic, config, dependency bump, etc.). Ideally paste 3-5 varied examples (a docs-only change, a core-logic change, a config change) rather than just one — the review gets much more useful with variety, but one diff is enough to start.
2. **Your test/suite catalog** — list every CI/eval suite you run on a PR, with: what it actually covers (e.g., "runs the full backend integration test set" or "LLM-as-judge check on 200 golden prompts for output quality regressions"), and your best guess at its cost or runtime (time, dollar cost of any LLM-judge calls, compute minutes — whatever you track). If you don't have exact numbers, say so; the review will just flag that suite's cost contribution as unknown rather than making one up.

Nothing is fetched automatically from GitHub, your CI system, or a billing dashboard — this is entirely based on what you paste.

## What it does (the procedure)

1. **Reads your diff(s) and classifies them** — which files changed, what kind of change each represents (docs-only, test-only, config/infra, core logic, public API, security-sensitive paths like auth or payments), and summarizes the overall "blast radius" in one line.
2. **Reads your suite catalog** — notes each suite's coverage area, its cost/runtime as you gave it, and flags anything that's mandatory, security, or compliance-related (either because you said so or because it's self-evidently that kind of check).
3. **Scores every suite against the diff** with one of three labels:
   - **SKIP (high confidence)** — the diff clearly doesn't touch anything this suite covers.
   - **RUN (low confidence / fallback)** — it's plausible or unclear whether the diff touches this suite's coverage. When in doubt, this is the label — never SKIP on a guess.
   - **RUN (mandatory, never gated)** — any suite you flagged (or that's obviously) security/compliance-critical always gets this label, independent of the diff.
   Each label comes with a one-sentence, diff-specific justification — not a generic "looks unrelated."
4. **Applies a fail-open rule out loud** — no suite gets skipped unless the review can point to specifically why its coverage is untouched by every file in the diff. Any ambiguity defaults to running it.
5. **Estimates cost impact using only the numbers you gave it** — sums the cost/runtime of the suites recommended for SKIP to produce a savings range, and explicitly marks any suite's cost contribution as "unknown" if you didn't supply a figure for it, rather than inventing one. This estimate is framed as based on your sample diff(s) only, not a validated long-run average.
6. **Recommends a validation path before you trust this for real** — regardless of how clean your sample looked, the review will tell you to run the real gate in shadow mode (logging decisions without actually skipping anything) across 20-30 real historical PRs first, and confirm no real regression would have been missed by a skipped suite, before letting any automated version of this actually skip suites in production CI.

## What you get back

A single report with five sections, in this order:

1. **Diff Summary** — files touched, change category, one-line blast-radius verdict.
2. **Suite Decision Table** — every suite you listed, its decision (SKIP / RUN-low-confidence / RUN-mandatory), and a diff-specific justification.
3. **Mandatory / Never-Gated Suites** — the subset that always runs regardless of diff content, and why.
4. **Estimated Cost Impact** — the savings range from step 5, with any suites whose cost was unknown called out separately, clearly labeled as a single-sample (or small-sample) estimate.
5. **Caveats & Recommended Next Step** — the fail-open statement, and the recommendation to validate in shadow mode across real historical PRs before trusting this in production.

## Guardrails — what this will never do

- It will never recommend SKIP for a suite when the diff's relationship to that suite's coverage is ambiguous or under-described — it defaults to RUN every time it's unsure. That fail-open behavior is the entire safety property of this idea; the review should never undermine it just to look more "efficient."
- It will never recommend skipping a suite you flagged as mandatory, security, or compliance-related, no matter what the diff looks like.
- It will never invent a cost or runtime number for a suite you didn't give figures for — it will say "cost unknown" instead of guessing.
- It will never present a single diff's results as proof this strategy is safe in general — it will always recommend validating against a real batch of historical PRs (shadow mode, no suites actually skipped yet) before trusting this for real CI traffic.
- It is not the automated gate itself — it's a one-time sanity check to help you decide whether building (or buying) the real continuously-running version is worth it.

## Example prompt to paste into any AI chat tool

> I run these test suites on every PR: [list your suites, what each covers, and approximate cost/runtime]. Here's a sample PR diff: [paste diff or describe the change]. Using the LLM Confidence-Gated CI Test-Selector procedure — classify the diff's blast radius, score each suite SKIP (high confidence) / RUN (low confidence, fail-open default) / RUN (mandatory, never gated), apply a strict fail-open rule where any ambiguity defaults to RUN, estimate cost savings only from the numbers I gave you (mark anything I didn't specify as "cost unknown"), and end with a recommendation to validate this in shadow mode against 20-30 real historical PRs before trusting it in production. Give me back the five-section report: Diff Summary, Suite Decision Table, Mandatory Suites, Estimated Cost Impact, and Caveats & Next Step.
