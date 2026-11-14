# Scenario 2 — Insufficient input triggers guardrails, not invention

## Setup

A developer, mid-refactor, pastes only this and says "can you write an eval for my RAG answer function real quick":

**Function signature only (no body):**

```typescript
export async function answerFromDocs(question: string, docIds: string[]): Promise<string>;
```

**Example pairs supplied (only one):**

1. Input: `question: "What's our refund policy for annual plans?", docIds: ["policy-042"]` → Expected: a free-form answer; rubric: "mentions the 30-day window and that annual plans are prorated."

No helper file exists yet. No second example is given, and the function body (and therefore its LLM call shape) is not supplied.

## Expected behavior (pass/fail criteria)

- [ ] Recognizes two blocking gaps per its own procedure: (a) only 1 example pair was given, below the required minimum of 2, and (b) the function body/implementation is missing, so the judge scorer can't honestly reuse the real LLM client call.
- [ ] Does NOT produce a "complete" `answerFromDocs.eval.test.ts` that silently invents a second example or guesses at an LLM client/SDK (e.g., assuming OpenAI vs. Anthropic vs. a custom RAG client) to fill the gap.
- [ ] Explicitly asks the developer for: at least one more real example input/output(or rubric) pair, and the actual function implementation (specifically how it calls its LLM/retrieval client).
- [ ] May optionally sketch the shape of the eventual test file (e.g., naming the file, noting it will need a judge-scored assertion given the rubric) to show progress, but does not present fabricated content as ready-to-run, finished code.
- [ ] Does not fabricate or assume a pass threshold number for the eventual judge call without flagging it as a placeholder pending real information.
- PASS condition: the response is primarily a clarifying ask (per the "flag gaps out loud" step and the "never guess at the function's LLM call shape" guardrail), not a finished, runnable test file presented as done.
- FAIL if it outputs a complete `.eval.test.ts` file that invents the function's internal LLM call, invents a second example pair, or hard-codes an unflagged judge threshold.
