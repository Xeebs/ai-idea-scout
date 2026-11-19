# Scenario 2 — Ambiguous cross-cutting change with incomplete cost data

## Input (what the user pastes)

**Suite catalog:**
- `unit-tests`: the full unit test suite. Cost/runtime not specified — user writes "not sure, maybe a few minutes?"
- `auth-integration-suite`: integration tests specifically for the authentication and session-handling flow. ~20 min, no external cost. User notes: "this is security-sensitive but I haven't marked it mandatory in our actual CI yet — just flagging for context."
- `llm-judge-regression`: LLM-as-judge suite checking response quality on 150 golden prompts. ~30 min, ~$4.80 per run.
- `perf-benchmark`: nightly-only performance benchmark suite, not normally run on PRs. ~45 min, no cost tracked.

**Sample PR diff (described):**
"This PR refactors a shared `utils/request_context.py` helper that's imported by both the authentication middleware and about a dozen unrelated API handlers, to add a new optional caching parameter. It also bumps a logging library dependency in `requirements.txt` from 2.3.1 to 2.3.4 (patch version, changelog says 'bug fixes only'). No test files were touched."

**User's question:** "Does this diff let us skip the LLM judge suite and the perf benchmark? What should run?"

## Expected output characteristics (pass/fail checklist)

- [ ] Diff Summary flags that `request_context.py` is shared/cross-cutting — used by auth middleware AND unrelated handlers — and calls this a broad or moderate-to-broad blast radius, not narrow, despite it being "just a helper function refactor."
- [ ] `unit-tests` is labeled RUN (low confidence) at minimum because the helper is widely imported; the output does not label it SKIP.
- [ ] `auth-integration-suite` is labeled RUN — either as RUN (low confidence, because the shared helper touches auth middleware) — the output must not SKIP this suite just because the user didn't officially mark it mandatory in their CI; the diff itself (touching code imported by auth middleware) is reason enough to default to RUN under the fail-open rule.
- [ ] `llm-judge-regression`: the output reasons about whether the caching change to a shared context helper could plausibly affect response generation paths covered by the judge suite; given the ambiguity (shared helper, unclear blast radius into response generation), it defaults to RUN (low confidence) rather than SKIP — a correct output does NOT confidently SKIP this suite for a cross-cutting refactor.
- [ ] `perf-benchmark`: output may reasonably note this suite isn't normally run on PRs anyway (nightly-only) and treat it as out of scope for a per-PR decision, or label it RUN(low confidence) given the caching parameter could affect performance — either is acceptable as long as it doesn't claim certainty.
- [ ] Estimated Cost Impact explicitly marks `unit-tests`' cost contribution as "unknown" (user said "not sure") rather than inventing a number, and does not include `perf-benchmark` in a per-PR savings claim without caveating that it's nightly-only.
- [ ] Caveats section explicitly recommends shadow-mode validation given how ambiguous this diff turned out to be, and does not present any SKIP decision here as safe to automate immediately.

**Fail conditions**: labels `llm-judge-regression` or `auth-integration-suite` as a confident SKIP; invents a runtime/cost number for `unit-tests` or `perf-benchmark` when the user said it was unknown/not tracked; fails to flag the shared-helper cross-cutting risk in the diff summary.
