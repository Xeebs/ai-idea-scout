# Scenario 2 — Llama 3.1 wrapped-in-prose output via vLLM, no chat template provided

## Input (what the user pastes)

> We serve Llama-3.1-8B-Instruct through vLLM's OpenAI-compatible endpoint for a `create_support_ticket` tool. This call got marked as a parse failure. Raw completion:
>
> ```
> Sure, I can help with that! Here's the function call:
>
> ```json
> {"name": "create_support_ticket", "arguments": {"priority": "high", "summary": "Customer reports login page returning 500 error on mobile Safari"}}
> ```
>
> Let me know if you need anything else!
> ```
>
> Tool schema:
> ```json
> {
>   "name": "create_support_ticket",
>   "parameters": {
>     "type": "object",
>     "properties": {
>       "priority": {"type": "string", "enum": ["low", "medium", "high"]},
>       "summary": {"type": "string"}
>     },
>     "required": ["priority", "summary"]
>   }
> }
> ```
>
> Parser error: `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
>
> I don't have the chat template handy — we're using vLLM's default Llama 3.1 tool-use template, haven't customized it. Model: Llama-3.1-8B-Instruct via vLLM 0.6.x.

## Why this is realistic

This is the other half of the idea's named taxonomy — a well-formed, perfectly correct tool call (right tool, right arguments, matches schema) that's simply wrapped in conversational prose and a markdown fence, which a naive JSON-parse-the-whole-string approach rejects outright. The user explicitly doesn't have the chat template on hand, testing whether the skill can still diagnose correctly from what's available rather than stalling or forcing a template-bug guess.

## Pass criteria

- [ ] Diagnosis bucket is **parser/extraction gap** (not template bug, not malformed output, not model reasoning failure).
- [ ] Evidence quotes the leading prose ("Sure, I can help with that!...") and the markdown code fence as the wrapping, plus notes the JSON payload itself is valid when isolated.
- [ ] Response connects the parser error ("Expecting value: line 1 column 1") to the fact that position 0 of the raw string is prose/whitespace, not JSON — i.e., explains *why* that specific error matches this bucket rather than just asserting it.
- [ ] Fix is concrete: strip markdown code fences and any leading/trailing non-JSON text before handing the string to a strict JSON parser (e.g., extract the substring between the first `{` and matching last `}`, or between the ```` ```json ```` fence markers).
- [ ] Does not treat the missing chat template as a blocker — correctly notes the template wasn't needed here because the evidence (prose wrapping + valid inner JSON) already fully explains the failure without it, OR explicitly acknowledges the template is unavailable but states confidence is still High because the failure is fully explained by the parser-level evidence alone.
- [ ] Does not misclassify this as "malformed-but-recoverable output" — the JSON itself is not malformed, it's just not isolated; the distinction should be respected.
- [ ] Does not reach "genuine model reasoning failure" — the tool, priority, and summary are all clearly correct and appropriate for a 500-error mobile login report.

## Fail conditions

- Classifying as chat-template rendering bug (there's no template leakage evidence here — no doubled braces, no leaked example).
- Refusing to give a diagnosis because the chat template wasn't provided, when the pasted evidence already fully supports a confident parser-gap diagnosis.
- Giving a vague fix like "improve the parser" instead of the specific stripping/extraction logic needed.
