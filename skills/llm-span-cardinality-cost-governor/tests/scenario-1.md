# Scenario 1 — Existing setup, bill already climbing

## Input (realistic, not a toy example)

> Our LLM trace bill with Langfuse has basically doubled in the last two months and finance is asking why. We instrumented our RAG assistant with OpenTelemetry about three months ago. Right now every span in a call chain captures `gen_ai.prompt` and `gen_ai.completion` in full — we didn't realize it was duplicating on every child span, so a single user request that fans out into a retrieval span, a reranking span, and two LLM-call spans ends up storing the full prompt/completion text four times. We also attach `retrieved_context` (the full text of every retrieved chunk, can be 5-10KB) to each retrieval span, and `tool_call.arguments`/`tool_call.result` on two tool-calling spans per request (usually small JSON, under 500 bytes). We're doing about 50,000 LLM-touching requests per day. Our error rate (failed generations, timeouts, or tool-call failures) is around 3%. We use Langfuse as our backend, billed roughly per GB ingested. We have no retention/incident-replay requirement beyond "the usual 14 days." We'd like to cut ingestion by at least half without losing the ability to debug errors.

## Pass criteria

- [ ] Output has all six sections in order: Inputs Received, Attribute Classification Table, Truncation Plan, Sampling Policy, PII/Compliance Flags, Open Questions.
- [ ] Inputs Received correctly restates 50,000 req/day and 3% error rate as given (not flagged as assumed), and names Langfuse as the backend.
- [ ] Attribute Classification Table includes every named attribute exactly once: `gen_ai.prompt`, `gen_ai.completion`, `retrieved_context`, `tool_call.arguments`, `tool_call.result` — plus reasonable always-safe attributes (model name, token counts, status/error code) even though the user didn't list them explicitly, OR the output notes it is only classifying the attributes explicitly named.
- [ ] `gen_ai.prompt`/`gen_ai.completion` are classified Hash-and-truncate, and the Truncation Plan explicitly flags the root-span-only fix for the 4x duplication problem described in the input — this is the single highest-value catch in this scenario; missing it is a fail.
- [ ] `retrieved_context` is addressed explicitly (classified into some tier with a rationale, not silently omitted) given it's 5-10KB per chunk and attached per retrieval span.
- [ ] `tool_call.arguments`/`tool_call.result` are classified (likely Always-safe or Hash-and-truncate given "usually small JSON, under 500 bytes") with a rationale referencing their actual size.
- [ ] Sampling Policy shows the volume-reduction arithmetic using the actual 3% error rate and proposes/derives a rate consistent with the stated "cut ingestion by at least half" target, and includes the plain-language debuggability-tradeoff sentence.
- [ ] Sampling Policy guarantees 100% capture of error/failed-generation/timeout/tool-failure traces.
- [ ] No specific dollar savings figure is invented — only volume/percentage math traceable to the given numbers, or an explicit assumption flag.
- [ ] PII/Compliance Flags addresses `retrieved_context` and/or prompt/completion content if the retrieved chunks or prompts could plausibly contain user data — at minimum raises the question rather than ignoring it.
- [ ] Output explicitly states this is a draft to implement/validate, not already-enforced policy.
- [ ] Fail if: any section invents a specific GB or dollar number not derivable from the input; any section recommends sampling that would drop error traces; the 4x-duplication issue is never mentioned.
