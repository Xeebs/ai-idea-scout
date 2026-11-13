# Scenario 2 — No error handling at all, pre-launch review before wiring into a BYOK eval platform (NONE)

## Realistic input

A startup is about to wire a new "Anthropic judge" integration into their internal eval platform (similar in shape to PostHog AI evals) so customers can bring their own Anthropic API key to run LLM-as-judge scoring on their own data. Before launch, an engineer wants a resilience review of the draft integration code, since they've heard other BYOK eval platforms have had problems with rate-limit bursts wiping out customer evaluation runs.

Pasted code/config:
```typescript
async function callJudge(apiKey: string, evalInput: EvalCase): Promise<JudgeScore> {
  const client = new Anthropic({ apiKey });
  const response = await client.messages.create({
    model: "claude-sonnet-5",
    max_tokens: 200,
    messages: [{ role: "user", content: buildJudgePrompt(evalInput) }],
  });
  return extractScore(response);
}

// called per-case from a batch runner with no additional wrapping:
async function runBatch(apiKey: string, cases: EvalCase[]) {
  const scores = await Promise.all(cases.map(c => callJudge(apiKey, c)));
  return scores;
}
```

What happens today on a 429: "Honestly we haven't tested it under load yet — I think if `messages.create` throws, the whole `Promise.all` just rejects and the batch endpoint probably returns a 500 to the customer's dashboard. We don't have anything specific for rate limits."

Provider: Anthropic (BYOK, customer-supplied key). This will be a long-lived service handling many customers' concurrent batches, and needs to survive a backend process restart mid-incident since customer batches can run for hours.

## Pass criteria

- [ ] Correctly locates the judge call as `client.messages.create(...)` inside `callJudge`, with no try/catch anywhere around it.
- [ ] States explicitly that the failure path is effectively undefined/uncaught as written — a thrown rate-limit error propagates up through `Promise.all` and fails the *entire batch*, not just the rate-limited case, and flags this as worse than a per-case loss.
- [ ] Classifies resilience level as NONE (no retry/backoff/error handling of any kind around the provider call).
- [ ] Still correctly reasons about Signature A/B even though resilience is NONE — e.g., notes that Signature A is trivially PRESENT (any 429 at all currently kills the whole batch, so a sustained burst certainly causes total loss) and Signature B is PRESENT (nothing resumes anything automatically; a failed batch needs to be manually re-triggered).
- [ ] Fix recommendation leads with retry/backoff honoring Retry-After as the necessary first step, but explicitly states this alone will not solve Signature A/B at this classification level, and names the park/resume layer as the follow-up requirement — matching the SKILL.md's NONE-level guidance.
- [ ] Given the stated requirement to survive a process restart mid-incident, the response should flag that in-memory-only state (even a future retry/backoff fix) won't be durable enough and should point toward persistent state, without inventing a specific tech stack the user didn't ask for.
- [ ] Does not claim this is already RESILIENT, TRANSIENT-ONLY, or PARK-CAPABLE — none of those apply when there is zero error handling.

## Fail criteria (any of these = skill failed)

- Treats the `Promise.all` all-or-nothing batch failure as equivalent to a per-case loss (misses that this is a more severe variant of Signature A — a single rate-limited case currently fails every other case in the batch too).
- Classifies resilience as anything other than NONE.
- Recommends only "wrap in try/catch and retry" without naming the park/resume follow-up needed to actually clear Signature A/B.
- Fabricates Anthropic's specific rate-limit numbers or claims knowledge of this company's actual infrastructure beyond what was described.
