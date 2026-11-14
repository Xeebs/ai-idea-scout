# TS Vitest Eval Drafter

Turn a TypeScript LLM-powered function and a handful of known-good examples into a runnable Vitest regression suite — no new eval SaaS, no new hosted judge platform, no new npm package beyond Vitest itself. Paste the prompt block below into any AI chat tool (ChatGPT, Claude, Gemini, Copilot Chat, etc.) along with your function's source and your examples.

## When to use this

Use this when you have a TypeScript/Node.js function that calls an LLM — a chat wrapper, a RAG answer function, a classifier, a tool-calling handler — and you want automated regression tests for it that run through the `vitest` command your project already uses, without adopting a hosted eval platform (Langfuse, Axiom, LangSmith, Braintrust) or installing a separate eval framework just to get started.

Don't use this to debug one prompt interactively, to build an analytics dashboard, or to test non-LLM logic. It's specifically for converting known-good examples into a runnable suite.

## What to hand over

This is a manual, paste-in skill — there is no live data connector. You provide:

1. **The full TypeScript source of the function under test** — not just the signature. Include exactly how it calls its LLM client/SDK, because the generated test needs to call your real function honestly.
2. **3-5 example input → expected-output pairs.** At least 2 are required. If you have fewer, the assistant should ask you for more rather than invent examples — don't accept a draft that made up its own test cases.
3. **For any example where the expected output is open-ended** (a summary, a free-form answer, anything that isn't an exact match or a fixed JSON shape), a one-line description of what makes an output acceptable — this becomes the judge rubric.
4. Optional: your project's test file naming/location convention, if it's not the default colocated `<function-name>.eval.test.ts`.
5. Optional: a custom pass threshold for judge-scored cases (default 0.7 on a 0-1 scale).

## The prompt template

Paste this, filling in the bracketed parts:

```
You are drafting a Vitest-based regression test for an LLM-powered TypeScript function. Follow this procedure exactly:

1. Read my function below. Identify its name, parameter/return types, whether it's async, and exactly how it calls an LLM client — the test must call my actual function, not reimplement the LLM call.
2. Classify each of my example pairs as either:
   - DETERMINISTIC (exact string/value match, substring/keyword match, or a specific JSON shape) -> write exact()/contains()/jsonSchema() assertions.
   - JUDGED (open-ended text where correctness is graded against a rubric, not matched) -> write a judge-scored assertion.
   If a pair is ambiguous, ask me which bucket it belongs in instead of guessing.
3. If I haven't mentioned an existing shared helper file, draft a small evals/helpers.ts alongside the test defining evalTest(), exact(), contains(), jsonSchema(), and judgeScore() — plain TypeScript, zero new npm dependencies beyond vitest (already present in my project).
4. Write judgeScore(output, rubric) to build a short rubric prompt and call the SAME LLM client/import my function under test already uses. Never introduce a new provider, SDK, or API key. Compare the parsed numeric response against a named, editable PASS_THRESHOLD constant (default 0.7 unless I specify otherwise).
5. Assemble <function-name>.eval.test.ts: one describe() block, one it()/evalTest() per example pair, deterministic assertions first, judged assertions last.
6. Tell me the exact command to run it: npx vitest run path/to/<function-name>.eval.test.ts
7. If fewer than 2 usable examples exist, if my function body is missing, or if a rubric is missing for a judged case, stop and ask me rather than padding the file.

Never add a new eval SaaS, hosted observability platform, or hosted judge API to the generated file. Never fabricate example pairs I didn't give you. Never silently add an npm dependency beyond vitest.

Here is my function:
[PASTE FULL TYPESCRIPT SOURCE, INCLUDING THE LLM CALL]

Here are my example input/output pairs:
[PASTE 3-5 PAIRS, NOTING RUBRICS FOR ANY OPEN-ENDED ONES]

[OPTIONAL: my test file convention / pass threshold override]
```

## What you get back

1. The exact file path to save the generated test to (and the helper file path, if a new one is being created).
2. A complete, runnable `<function-name>.eval.test.ts` — no `// TODO` placeholders, no omitted code.
3. If this is your first eval file, a complete `evals/helpers.ts` alongside it.
4. The exact `npx vitest run ...` command to execute the new test(s).
5. A short list of any examples it couldn't use yet (ambiguous, missing rubric) and what you'd need to add to include them.

## Guardrails this skill follows

- It will not invent example input/output pairs — only your supplied pairs become assertions.
- It will not introduce a new eval SaaS, observability platform, or hosted judge API — the generated file calls `vitest` and the LLM provider your function already uses, nothing else.
- It will not add a new npm dependency beyond `vitest` without asking first.
- It will not hide the judge pass threshold inside the logic — it's always a named constant you can edit.
- It will not guess at your LLM call shape from a bare function signature — if you only give it a signature, it will ask for the implementation.
- It will not claim the generated suite is comprehensive — it's a regression net against the examples you gave it, not a substitute for human review of model outputs.

## Why this exists

TypeScript developers who want LLM regression tests inside their existing `vitest`/CI workflow are currently stuck hand-rolling their own mini eval harness or adopting a full hosted observability platform just to get a pass/fail signal on a prompt change. This skill produces the test file directly — useful today even before any dedicated eval runner library is installed, and the output format (deterministic + judge-scored assertions run through `vitest`) is designed to port cleanly if you later adopt a purpose-built local-first eval runner.
