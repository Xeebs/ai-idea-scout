# Scenario 1 — Support ticket classifier (mixed deterministic + judged)

## Setup

A developer is working in a Node.js/TypeScript backend that already runs `vitest` in CI. They paste the following and ask: "write evals for this function."

**Function source (`src/ticketing/classifyTicket.ts`):**

```typescript
import OpenAI from "openai";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export interface TicketClassification {
  category: "billing" | "technical" | "account" | "other";
  summary: string;
}

export async function classifyTicket(ticketText: string): Promise<TicketClassification> {
  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "Classify the support ticket into billing, technical, account, or other, and write a one-sentence summary. Respond as JSON: {category, summary}.",
      },
      { role: "user", content: ticketText },
    ],
    response_format: { type: "json_object" },
  });
  return JSON.parse(response.choices[0].message.content!);
}
```

**Example pairs supplied:**

1. Input: `"I was charged twice for my subscription this month, please refund the duplicate charge."` → Expected: `category: "billing"` (exact match on category; summary open-ended).
2. Input: `"The app crashes every time I try to upload a profile photo larger than 2MB."` → Expected: `category: "technical"` (exact match on category; summary open-ended, rubric: "summary mentions the crash and the upload/photo context").
3. Input: `"How do I change the email address linked to my account?"` → Expected: `category: "account"` (exact match).
4. Input: `"Just wanted to say your onboarding email was really well written, nice job."` → Expected: `category: "other"`, and rubric: "summary should not treat this as a complaint or request — it's praise/feedback."

No existing `evals/helpers.ts` in the project — this is the team's first eval file.

## Expected behavior (pass/fail criteria)

- [ ] Reads the function body and identifies that it calls `client.chat.completions.create` via the OpenAI SDK, not a generic placeholder.
- [ ] Classifies the `category` field assertions as deterministic (`exact()` against `"billing"`/`"technical"`/`"account"`/`"other"`) for all 4 pairs.
- [ ] Classifies the `summary` field as judged for pairs 2 and 4 (where a rubric was given) — does not attempt an exact-string match on free-form summary text.
- [ ] Drafts a new `evals/helpers.ts` since none exists, defining `evalTest()`, `exact()`, `contains()`, `jsonSchema()`, `judgeScore()` with zero new npm dependencies beyond `vitest`.
- [ ] `judgeScore()` in the draft calls the same `OpenAI`/`client` import pattern the function under test uses — does not introduce LangSmith, Langfuse, Axiom, or any other hosted eval service.
- [ ] Includes a named `PASS_THRESHOLD` constant (defaulting to 0.7) rather than a hard-coded magic number buried in logic.
- [ ] Produces a complete `classifyTicket.eval.test.ts` file with no `// TODO` placeholders — 4 test cases, one per example pair.
- [ ] States the exact file path(s) to save to and the `npx vitest run ...` command.
- [ ] Does NOT invent a 5th example pair or extra categories not in the function's type union.
- FAIL if it fabricates additional example inputs, silently adds a new eval library dependency, or treats all 4 pairs as pure exact-match (ignoring the open-ended summary rubrics).
