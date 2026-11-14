---
name: typescript-native-local-first-eval-runner
description: Drafts a self-contained Vitest eval test file for a TypeScript LLM-powered function, from the function's source and a handful of example input/output pairs the developer supplies — zero new eval SaaS, zero new npm dependency beyond Vitest.
---

# TS Vitest Eval Drafter

## When to use this

The trigger moment: a developer is working in a TypeScript/Node.js codebase that already runs `vitest`, has a function that calls an LLM (a chat completion wrapper, a RAG answer function, a classifier, a tool-calling handler, etc.), and says something like "write evals for this function," "test this LLM call," or "I need regression tests for this prompt" — without wanting to adopt a hosted eval platform (Langfuse, Axiom, LangSmith) or install a separate eval framework just to get started.

Do not reach for this skill to debug a single failing prompt interactively, to build a full observability/analytics dashboard, or to test non-LLM logic — it is specifically for turning a handful of known-good examples into a runnable regression suite.

## Inputs

**Data source**: Manual — the developer pastes the TypeScript source of the function under test and 3-5 example input/expected-output pairs (or a rubric describing what "good" looks like) directly into the chat. There is no connector: the generated test calls the LLM provider the developer's own function already uses, with whatever API key/client the project already has configured. Nothing is fetched from a third-party service by this skill itself.

Required:
1. The full TypeScript source of the function under test (not just its signature) — including how it calls its LLM client, so the generated test can be honest about what's being exercised.
2. 3-5 concrete example input → expected-output pairs. At least 2 are required to proceed; fewer than that, ask for more instead of inventing examples.
3. For any example where "expected output" isn't an exact/structural match (open-ended text, summaries, free-form answers), a one-line description of what makes the output acceptable (the rubric).

Optional:
4. The project's existing test file naming/location convention, if it differs from colocated `<name>.eval.test.ts`.
5. A custom pass threshold for judge-scored cases (default: 0.7 on a 0-1 scale).

## Procedure

1. **Read the function.** Identify its name, parameter types, return type, whether it's async, and exactly how it invokes an LLM (which client/SDK call, so the test calls the function itself rather than re-implementing the LLM call).
2. **Classify each example pair.**
   - *Deterministic*: output is an exact string/value, a substring/keyword that must appear, or a specific JSON shape → use an `exact()`, `contains()`, or `jsonSchema()` assertion.
   - *Judged*: output is open-ended natural language where correctness is graded, not matched → use a judge-scored assertion against the supplied rubric.
   - If a pair is ambiguous, ask the developer which bucket it belongs in rather than guessing.
3. **Check for an existing shared helper file** (something like `evals/helpers.ts`). If the developer hasn't mentioned one and this is their first eval file, draft one alongside the test file — a few dozen lines defining `evalTest()`, `exact()`, `contains()`, `jsonSchema()`, and `judgeScore()`. This is the only new local file introduced; it adds zero new npm dependencies (just `vitest`, already present). If a helper file already exists, import from it instead of redefining it.
4. **Write the judge scorer honestly.** `judgeScore(output, rubric)` builds a short rubric prompt ("Rate 0-1 how well this output satisfies: <rubric>. Output: <output>. Respond with only a number.") and calls the *same* LLM client/import the function under test already uses — never introduce a new provider, SDK, or API key. Parse the numeric response and compare against the threshold.
5. **Assemble the test file** as `<function-name>.eval.test.ts`, colocated next to the source file (Vitest convention): imports, one `describe()` block per function, one `it()`/`evalTest()` per example pair, deterministic assertions first, judged assertions last.
6. **Name the exact command to run it**: `npx vitest run path/to/<function-name>.eval.test.ts`.
7. **Flag gaps out loud** rather than silently padding: if fewer than 2 examples were given, if the function body wasn't supplied, or if a rubric is missing for a judged case, say so and ask before generating that part.

## Output format

Respond with:
1. One line stating the file path to save the test to (and the helper file path, if one is being created for the first time).
2. A fenced ` ```typescript ` code block with the complete `<function-name>.eval.test.ts` content — nothing truncated, nothing left as `// TODO`.
3. If a helper file is new, a second fenced ` ```typescript ` code block with the complete `evals/helpers.ts` content.
4. The exact `npx vitest run ...` command to execute the new test(s).
5. A short bullet list of any examples it couldn't use (ambiguous classification, missing rubric) and what's needed to add them.

## Guardrails

- Never invent example input/output pairs. Only generate assertions for pairs the developer actually supplied; if fewer than 2 usable pairs exist, stop and ask for more before writing the file.
- Never introduce a new eval SaaS, observability platform, or hosted judge API (Langfuse, Axiom, LangSmith, Braintrust, etc.) into the generated file — the entire point is a test that runs with `vitest` and talks to no service except the LLM provider the function under test already calls.
- Never add a new npm dependency beyond `vitest` (already assumed present) without explicitly flagging it and asking first — the shared helper file is hand-written TypeScript, not a wrapper around a third-party eval library.
- Never fabricate or hard-code a judge pass threshold silently — always surface it as a named, editable constant (`PASS_THRESHOLD = 0.7`) in the generated file.
- Never guess at the function's LLM call shape from its signature alone — if only a signature (no body) is supplied, ask for the implementation before generating the judge scorer, since it needs to reuse the real client call.
- Never claim the generated suite is "comprehensive" or a replacement for human review of model outputs — it is a regression net against the specific examples supplied, nothing more.
