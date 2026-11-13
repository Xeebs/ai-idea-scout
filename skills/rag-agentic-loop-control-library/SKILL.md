---
name: rag-agentic-loop-control-library
description: Audits a hand-rolled agentic RAG retrieval loop (retrieve → critique → re-query → stop) for three known failure modes — missing retry cap, uncalibrated stopping criterion, unhandled malformed tool-call JSON — and drafts the specific code fix for each. Use when a developer is about to ship, or has already had crash/hang problems with, a custom agentic retrieval loop.
---

# Agentic RAG Loop Audit

## When to use this

Reach for this skill the moment a developer pastes or describes a hand-rolled agentic-retrieval loop — code that plans a query, retrieves documents, critiques/evaluates whether the retrieval was sufficient, and either answers or rewrites the query and retries. Typical trigger phrases: "can you check my retrieval loop before I ship it", "my RAG agent hangs/loops forever", "my agent crashed on a malformed tool call", "how do I know when to stop retrieving". It is scoped to the hundreds-to-low-thousands-of-document regime (a solo developer or small team's internal tool), not million-document retrieval infrastructure — if the described system is at that scale, say so and redirect rather than patching the loop as if it will fix infra-scale problems.

## Inputs

**Data source**: Manual — the user pastes the actual loop code or pseudocode (any language/framework: raw function-calling, LangGraph, LlamaIndex, or a plain description of the steps). Optionally they also paste: the corpus size/regime, a stack trace or hang description from a real failure, or a sample of malformed JSON the model returned. Nothing is read from a connector or API — this is a code-review skill, not a monitoring integration.

## Procedure

1. **Parse the loop** into its five structural pieces: the retrieve call, the critique/evaluate step, the re-query/rewrite step, the loop's exit condition(s), and how it handles the model's tool-call/structured output. If any piece is genuinely absent from the pasted code (not just unclear), note it as "not present" rather than guessing.
2. **Check failure mode 1 — missing retry cap.** Is there a hard maximum iteration count? `while True`, `while not satisfied`, or a recursive call with no depth limit → **CRITICAL**. A cap present but set unreasonably high (>10) with no stated reasoning → **WARNING**. A cap with a specific number and reasoning → **OK**.
3. **Check failure mode 2 — uncalibrated stopping criterion.** Does the loop decide "good enough" using a signal other than the iteration count alone (an explicit relevance score threshold, a marginal-gain check between iterations, an LLM-judged sufficiency check)? If the only stop condition is the retry cap itself → **CRITICAL** ("the loop will always run to the cap on hard queries and never improve on easy ones — there is no early-exit or quality signal"). If a threshold exists but is a vague prompt instruction ("stop when you have enough") rather than a checked numeric value → **WARNING**. If a numeric/explicit check exists → **OK**.
4. **Check failure mode 3 — unhandled malformed tool-call JSON.** Is there error handling (try/except or equivalent) around parsing the model's structured output? No handling at all → **CRITICAL** (a single malformed response crashes or silently corrupts the loop). Handling exists but has no bounded retry of its own (so a persistently malformed model response loops forever) → **WARNING**. Handling exists and is bounded → **OK**.
5. **Bonus check — exit-reason logging.** Does the loop record *why* it exited (answered / max-iterations-hit / low-marginal-gain / parse-failure-exhausted)? If not, flag **INFO** — this is the only way to see these three failure classes happening in real traffic after the audit is done.
6. **Draft the fix for every CRITICAL and WARNING.** Write the actual code to add or change, in the apparent language/framework of the pasted snippet — not generic advice like "add error handling." If the framework/library's exact API can't be confirmed from the snippet, say so explicitly and give the generic (framework-agnostic) version of the fix instead of inventing API calls.
7. **Scope check.** If the pasted loop or a stated corpus size implies million-document-scale retrieval, state plainly that this audit's fixes address the control-loop logic only and will not resolve infra-scale retrieval problems — recommend dedicated retrieval infrastructure review instead.
8. **Report unverifiable items.** If something can't be assessed from the pasted snippet alone (e.g., whether `retrieve()` is idempotent across retries, whether the critique step itself can hang), list it under residual risk instead of assuming it's fine.

## Output format

A single markdown report with these sections, in order:

1. **Loop structure summary** — 2-3 sentences naming what pieces were found and which (if any) were absent.
2. **Findings table** — columns: Failure Mode | Severity (CRITICAL/WARNING/OK/INFO) | What was found | One-line fix summary.
3. **Drafted fixes** — for every CRITICAL and WARNING row, a code block with the actual snippet/diff to add, scoped to the user's language/framework (or marked "framework-agnostic" if it couldn't be determined).
4. **Exit-reason logging recommendation** — only if that check was INFO, otherwise omit this section.
5. **Residual risk** — bullet list of anything the audit could not verify from the pasted material alone.

## Guardrails

- Never declare a loop "safe" or "production-ready" overall — only report against the three named failure modes plus the exit-logging bonus check; anything outside that scope is explicitly out of scope, not implicitly passed.
- Never invent framework-specific API names or method signatures that can't be confirmed from the pasted snippet. If unsure, say so and give the framework-agnostic fix.
- Never recommend "migrate to LangGraph/LlamaIndex/a different framework" as the fix — this skill patches the user's existing loop in place; it does not push adoption of a specific orchestration library.
- Never cite a specific retry-count or threshold number as an "industry standard" fact — present defaults (e.g., 3-5 iterations) as a reasoned starting point to tune against the user's own data, not as a settled constant.
- If the pasted loop is too short or incomplete to evaluate one of the three failure modes (e.g., no critique step exists at all), say explicitly which mode couldn't be assessed and why — never fill the gap with an assumed verdict.
