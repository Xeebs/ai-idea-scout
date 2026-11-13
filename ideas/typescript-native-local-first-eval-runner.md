# Local Bench: A TypeScript-Native, Local-First LLM Eval Runner for Vitest

- **Status**: EXPLORING (promoted 2026-11-13 cycle 57: evidence density — ≥2 independent posts within the digest, "Evalite - an Early Preview" (aihero.dev) and "Evaluating Eval Tooling," both independently naming the same TS-native local-first eval gap)
- **Date**: 2026-11-13
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-13-llm-evaluation-observability.md · P4
- **Maturity verdict**: PARTIAL — `gh repo view mattpocock/evalite` shows the one real implementation filling this gap ("Evalite") is now "Deprecated and no longer maintained. Langfuse is the recommended replacement" (pushed 2026-11-09, 1,741 stars at deprecation) — but Langfuse is a full hosted/self-hosted observability platform, not a TS-native local-first eval runner, so it doesn't replace the use case. Only early-stage, low-adoption successors exist (`tsevals` v0.0.2, a `vitest-evals` prototype, a 48/100-health-score fork). PARTIAL rather than OPEN because prior art and a clear design pattern (Vitest-based runner) already exist to build on.
- **Format**: BOTH
- **Data Sources**: MANUAL — the developer writes the TypeScript eval test file themselves (inputs, expected outputs, and/or an LLM-judge rubric), exactly as they'd author a normal Vitest unit test; the runner calls the developer's own already-configured LLM API key to produce the response under test. There is no third-party data connector to read from — this is a local dev-loop tool operating on code the user already has, not a buyer's external data store.

## The Gap

The author of "Evalite - an Early Preview" (aihero.dev) wrote that it "seems strange... that no TypeScript-native, local-first tool exists for testing LLM-powered apps" and built one themselves — the clearest "has anyone built this" complaint in the digest. A second WebSearch hit, "Evaluating Eval Tooling," lists concrete missing features (grouping pass/fail samples, easy deterministic scoring) and calls the field inconsistent and gap-ridden. Evalite filled the gap for over a year and accumulated 1,741 stars, then was deprecated on 2026-11-09 with Langfuse named as the "replacement" — except Langfuse requires adopting a hosted/self-hosted observability platform, not running `vitest`-style tests locally in CI with zero data egress. The gap didn't just persist; it just reopened.

## The Project

A thin, dependency-light package that lets a TypeScript developer write LLM evals as ordinary Vitest test files using an `evalTest()` helper. Each test combines deterministic assertions (`exact`, `contains`, `jsonSchema`, cost/latency thresholds) with an optional LLM-judge scorer, runs through the existing `vitest` CLI and CI job a team already has, and writes results to a local SQLite/JSON run-history file. A companion `npx localbench view` command serves a small local web UI that groups samples by pass/fail, diffs a run against the previous one, and never sends anything off-box except the calls the developer's own test code already makes to their LLM provider.

Core components: (1) a Vitest plugin/matcher registering `evalTest()` and the scorer library; (2) a local run-history store (SQLite file, git-ignorable); (3) a static local-only viewer UI; (4) a migration guide and import script for Evalite's test format, to directly capture its 1,741-star userbase now stranded by the deprecation.

## Tangible Impact

**Population**: TypeScript/Node.js developers building LLM-powered features who want to test them inside their existing `vitest`/CI workflow without adopting a hosted eval platform. Size proxy: Evalite reached 1,741 GitHub stars before its deprecation — a concrete lower bound on developers who had already opted into exactly this pattern and are now stranded.

**Mechanism**: removes the choice developers are currently forced into — either hand-roll their own mini eval harness (as Evalite's and "Evaluating Eval Tooling"'s authors both did) or migrate to a hosted platform they didn't want — by giving them a drop-in library that fits the test workflow they already run.

**Measure**: median time for a developer to write and run their first eval test (target: comparable to writing a normal Vitest test, under 5 minutes); number of successful automated migrations from Evalite's test format; % of CI eval runs that complete with zero calls to any third-party service other than the LLM provider the developer's app already uses.

## Why Now

Evalite's deprecation (2026-11-09) is inside this digest's 30-day window and directly reopens a gap the community had already validated at scale (1,741 stars) — the successors that exist (`tsevals` v0.0.2, a prototype fork) are too early-stage to have absorbed that userbase yet, so there's a live, time-limited window before one of them does.

## Skill Angle

A Claude Code skill, separable from the runtime tool, that drafts a ready-to-run `evalTest()` suite for a given TypeScript LLM-powered function. **Trigger**: a developer says something like "write evals for this function" and points at a handler/module. **Inputs**: the TypeScript source of the function under test, plus 3-5 example input/expected-output pairs the developer pastes or describes. **Output**: a complete `*.eval.test.ts` file using Local Bench's `evalTest()` API — deterministic assertions for the cases that admit one, an LLM-judge rubric for the cases that don't, wired to run under the existing `vitest` command. This differs from the project itself: the project is the runtime library and viewer; the skill is a one-shot drafting aid that produces test files a developer could also hand-write, useful even before they've installed anything.

## MVP Sketch

Two weeks, 1-2 people: ship the Vitest plugin with `exact`/`contains`/`jsonSchema` scorers and a single LLM-judge scorer type, SQLite run storage, and a bare-bones CLI table output (skip the web UI for v0). Validate the core hypothesis — "a Vitest-native API is what the Evalite userbase actually wants back" — by publishing an Evalite-test-format import script and tracking how many GitHub issues/stars land on the new repo from people explicitly citing the deprecation.

## Risks & Open Questions

- Strongest reason this might already be solved: if Langfuse ships a genuinely lightweight local-first SDK mode in the next few months, it could retroactively make the deprecation's redirect correct — worth re-checking before building.
- Risk that `tsevals` or the `vitest-evals` prototype simply matures first and absorbs the gap before this ships.
- Open question: whether deterministic JSON-schema/cost scorers alone (no judge) cover enough real eval use cases to matter, or whether the LLM-judge path is load-bearing for adoption from day one.
- Open question: how much of Evalite's original design (snapshot testing integration, specific scorer API) is worth replicating exactly vs. redesigning.
