# Local Bench: Vitest-Native LLM Evals, No Hosted Platform Required

A deprecation notice quietly reopened a gap 1,741 developers had already voted to fill. On 2026-11-09, Evalite — the one real TypeScript-native, local-first LLM eval runner anyone had actually built and shipped — was marked "Deprecated and no longer maintained," with Langfuse named as its replacement. Except Langfuse isn't a replacement for what people liked about Evalite: it's a full hosted/self-hosted observability platform, not a `vitest`-shaped way to write LLM regression tests that never leave your machine. The tool is gone; the need it satisfied for over a year clearly isn't.

## The Gap

The author of "Evalite - an Early Preview" (aihero.dev) put the complaint plainly: it "seems strange... that no TypeScript-native, local-first tool exists for testing LLM-powered apps," and built one themselves rather than wait for someone else to. A second independent post, "Evaluating Eval Tooling," lists the same missing basics — grouping pass/fail samples, easy deterministic scoring — and calls the whole field inconsistent and gap-ridden. Two unrelated authors naming the same hole, within the same 30-day window, is exactly the kind of signal that doesn't show up by accident.

Evalite answered that complaint well enough to reach 1,741 GitHub stars. Then its own maintainers stepped away and pointed everyone toward a product category it was never trying to compete with. The successors that exist today — `tsevals` at v0.0.2, a `vitest-evals` prototype, a fork sitting at a 48/100 health score — are real attempts, but none of them has had time to absorb a userbase that size. This isn't a cold-start problem; it's a warm, stranded one.

## The Project

Local Bench is a thin, dependency-light package that lets a TypeScript developer write LLM evals as ordinary Vitest test files, using an `evalTest()` helper instead of inventing a parallel eval framework. Each test combines deterministic assertions — `exact`, `contains`, `jsonSchema`, cost/latency thresholds — with an optional LLM-judge scorer, runs through the `vitest` CLI and CI job a team already has wired up, and writes results to a local SQLite/JSON run-history file. A companion `npx localbench view` command serves a small local web UI that groups samples by pass/fail and diffs a run against the previous one — all without sending a single byte anywhere except the LLM calls the developer's own test code was already going to make.

Four pieces make it up: a Vitest plugin/matcher that registers `evalTest()` and the scorer library; a local, git-ignorable run-history store; a static, local-only viewer UI; and — deliberately — a migration guide and import script for Evalite's own test format, aimed squarely at catching the 1,741-star userbase currently stranded by the deprecation before a competing successor does.

## Tangible Impact

**Population**: TypeScript/Node.js developers building LLM-powered features who want to test them inside their existing `vitest`/CI workflow without adopting a hosted eval platform. Size proxy: Evalite reached 1,741 GitHub stars before its deprecation — a concrete lower bound on developers who had already opted into exactly this pattern and are now stranded.

**Mechanism**: removes the choice developers are currently forced into — either hand-roll their own mini eval harness (as both the Evalite author and the "Evaluating Eval Tooling" author independently did) or migrate to a hosted platform they didn't actually want — by giving them a drop-in library that fits the test workflow they already run.

**Measure**: median time for a developer to write and run their first eval test (target: comparable to writing a normal Vitest test, under 5 minutes); number of successful automated migrations from Evalite's test format; % of CI eval runs that complete with zero calls to any third-party service other than the LLM provider the developer's app already uses.

## Try It

A companion Claude Code skill already exists at `skills/typescript-native-local-first-eval-runner/`: **"Drafts a self-contained Vitest eval test file for a TypeScript LLM-powered function, from the function's source and a handful of example input/output pairs the developer supplies — zero new eval SaaS, zero new npm dependency beyond Vitest."**

It's deliberately separable from the runtime library above — you can use it today even before Local Bench itself exists, by handing it a function and a few example input/output pairs and letting it draft the `*.eval.test.ts` file (and a shared `evalTest()`/`exact()`/`contains()`/`judgeScore()` helper, if you don't have one yet) for you to run with `npx vitest run`. It never introduces a new eval SaaS or hosted judge API — it reuses whatever LLM client the function under test already calls.

Two ways to use it:
- **Paste it into any AI chat tool**: copy the contents of `skills/typescript-native-local-first-eval-runner/README.md` into the chat, then hand it the function source and your example pairs.
- **Drop it into Claude Code**: copy the `skills/typescript-native-local-first-eval-runner/` folder into `~/.claude/skills/`, and Claude Code will reach for it automatically when you ask it to write evals for an LLM-powered function.

## Worth Weighing

If Langfuse ships a genuinely lightweight local-first SDK mode in the next few months, that could retroactively make the deprecation's own redirect correct — this gap is worth re-checking before committing real build time to it. There's also a live race condition: `tsevals` or the `vitest-evals` prototype could simply mature first and absorb the stranded userbase before Local Bench ships. And it's an open question how much of Evalite's original design — its snapshot-testing integration, its specific scorer API — is worth replicating exactly versus redesigning from scratch.

---

Surfaced from `research/2026-11-13-llm-evaluation-observability.md`, pattern `P4`.
