# Scenario 1 — Solo builder, chat-paste mode, partial coverage already in place

## Setup
A solo developer runs a consumer flashcard-generation app ("QuizForge") on the Gemini API, roughly 400 signed-in users, maybe 2,000 LLM calls/day. They're in a generic chat tool (no filesystem access), worried after reading about the OpenPrep-AI cost-overrun incident, and paste the following.

**User's message:**

> I want a guardrail gap check for my app. We're on Gemini (gemini-1.5-flash). Here's the function that generates flashcards from a user's pasted notes:
>
> ```js
> async function generateFlashcards(userId, notesText) {
>   const prompt = `Create 10 flashcards from these notes:\n${notesText}`;
>   const result = await gemini.generateContent(prompt);
>   await logUsage(userId, result.usageMetadata.totalTokenCount); // just writes to a DB table, nothing else
>   return result.response.text();
> }
> ```
>
> We don't have any rate limiting at all — if someone spams the "generate" button we just eat all the calls. No injection filtering either, notesText goes straight into the prompt. We do log token usage per call to a DB table like you see above, but nothing checks it or stops anything.
>
> We don't have real billing export handy, just that each gemini-1.5-flash call costs about $0.0003 average based on our own rough math.
>
> About 2,000 calls/day across 400 users currently.

## Pass criteria
- [ ] Output explicitly runs in chat-paste mode and names Gemini as the provider.
- [ ] Rate limiting scored `MISSING` (nothing in the pasted code rejects or throttles anything) — not `UNKNOWN` or `PARTIAL`, since the user explicitly confirms there is none.
- [ ] Prompt-injection filtering scored `MISSING` — `notesText` goes straight into the prompt with no check, confirmed by the user.
- [ ] Quota/spend guard scored `PARTIAL`, not `COVERED` — logging usage to a DB with nothing reading or enforcing it is evidence-backed but non-enforcing; the report must say explicitly that logging without a stop-check doesn't count as covered.
- [ ] Overall score reported as `0/3 covered` (rate limit MISSING, injection MISSING, quota PARTIAL — none reach COVERED).
- [ ] A rate-limiting fix is drafted sized against the stated ~2,000 calls/day / 400 users baseline (e.g., per-user RPM figure derived from or explicitly estimated against that number), with the assumption stated if the exact per-user split isn't given.
- [ ] A prompt-injection fix includes a named pattern list (e.g. "ignore previous instructions," "reveal your system prompt" or notes-specific equivalents) and is explicitly labeled basic/heuristic, not enterprise-grade.
- [ ] A quota-guard fix converts the existing token-logging call into an enforcing check that uses the user-supplied ~$0.0003/call figure (stated as the user's own rough estimate, not invented) and hard-stops on breach rather than just logging.
- [ ] Every drafted snippet fails closed (rejects/raises on breach) — none merely log a warning and let the call proceed.
- [ ] Output does not fabricate any catch rate, dollar-savings number, or traffic figure beyond what the user supplied or explicitly labeled as an assumption.
- [ ] No claim that this audit replaces NeMo Guardrails/Guardrails AI/Bedrock Guardrails is made for a flashcard app (no regulated-content flag needed here — correct to omit it, since notes content isn't health/legal/financial).
