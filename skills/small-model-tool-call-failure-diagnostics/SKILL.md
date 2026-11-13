---
name: small-model-tool-call-failure-diagnostics
description: Diagnoses a single failed tool call from a small/local LLM (Ollama, llama.cpp, vLLM) by classifying the root cause into one of four buckets — chat-template rendering bug, parser/extraction gap, malformed-but-recoverable output, or genuine model reasoning failure — with cited evidence and a concrete fix. Use when a user pastes a raw failed tool-call trace and asks why it broke, instead of guessing "the model is just bad at this."
---

# Small-Model Tool-Call Failure Diagnostics

## When to use this
The user is debugging a tool-calling / function-calling failure from a small, open-weight local model (typically sub-8B — Qwen2.5/3, Llama 3.x, Mistral, Hermes families) served through Ollama, llama.cpp's `server`, or vLLM's OpenAI-compatible endpoint, and pastes a failed trace with a question like "why did this tool call fail", "is this a template bug or is the model just dumb", or "my tool-calling accuracy dropped, here's one of the failures." It is a one-shot, zero-install triage for a single failure — not a running proxy that watches a live stack (that would be a different, always-on tool).

Do not reach for this for: failures in Claude/GPT-4-class hosted models (different failure surface and much rarer template/parser class of bug), or for aggregate "why is my overall score low" questions without a specific failed trace attached — ask the user to paste one concrete failure first.

## Inputs
**Data source**: Manual — the user pastes the trace directly in the chat; this skill does not connect to Ollama's REST API, llama.cpp's `server` HTTP API, or vLLM's OpenAI-compatible endpoint itself (reaching into those live is the job of the companion always-on wrapper/proxy project this skill is a lightweight, no-install counterpart to — see that project's README if the user wants automatic capture across a running stack instead of one-off pastes).

Required from the user (ask for whatever is missing before classifying):
1. **The raw model completion** — the exact text the model generated for the tool call, uncleaned, including any surrounding text. This is the one truly non-negotiable input; refuse to classify without it.
2. **The tool schema that was sent** — the JSON schema/definition of the tool(s) offered to the model for that turn.

Strongly requested, ask explicitly if missing and the raw output contains anything suspicious (literal `{{`, `}}`, unescaped tags, or template-looking placeholder text):
3. **The chat template used** — the Jinja/prompt template fragment that renders tool definitions and few-shot tool-call examples into the prompt. Needed to confirm or rule out a template rendering bug.
4. **The parser error or extraction code**, if the failure was caught downstream — e.g. the regex/JSON-parse step that rejected the output, and its exact error message.
5. **Model name and runtime** (e.g. "Qwen2.5-7B-Instruct via Ollama") — helps match known template bugs for that family.

## Procedure
1. **Check completeness.** If the raw completion is missing, stop and ask for it — do not guess a classification from a description alone. If the chat template or parser error is missing but the raw output shows signs that would need it to confirm, ask for it before finalizing (a lower-confidence provisional classification is fine while waiting).
2. **Scan for template rendering bugs first** (cheapest to confirm, most often misdiagnosed as "model is bad"):
   - Does the raw completion contain literal, un-rendered template syntax — doubled braces (`{{`, `}}` appearing as literal text rather than valid JSON), stray Jinja delimiters, or a few-shot *example* tool call's placeholder values copied verbatim (e.g. the model emits the exact example argument from the template instead of a value derived from the actual user request)?
   - If the chat template was provided, grep it for the matching fragment and confirm the leak traces back to it.
   - Known family bugs to check against: Qwen2.5's tool-call template historically renders its own example with doubled braces that small models then copy literally.
3. **If no template leak, check for a parser/extraction gap:**
   - Is there a syntactically valid tool call *somewhere* in the output, but wrapped in something the parser likely doesn't strip — markdown code fences (` ```json `), a preamble sentence before the JSON ("Sure, here's the call:"), trailing commentary after it, or non-ASCII/escaped-unicode in argument values the parser's regex doesn't anticipate?
   - If a parser error message was provided, check whether it's complaining about exactly this kind of wrapping (e.g., "unexpected token at position 0" when position 0 is a stray newline or backtick).
4. **If the call is unwrapped but still fails to parse, check for malformed-but-recoverable output:**
   - Is the JSON *almost* valid — a trailing comma, an unescaped internal quote, a missing closing brace, a field named `parameters` when the schema says `arguments` (or vice versa), single quotes instead of double quotes?
   - The intent (which tool, roughly what arguments) must be clearly recoverable by a human reading it for this bucket — if it's not recoverable, downgrade to bucket 2 (parser gap, too malformed for a regex to help) or escalate to bucket 4.
5. **Only if buckets 1–3 are explicitly ruled out, classify as genuine model reasoning/argument-choice failure:**
   - The output is syntactically perfect and matches the schema exactly, but the model picked the wrong tool for the request, or supplied plausible-looking but wrong/hallucinated argument values (e.g., inventing a file path, misreading a number from context).
   - This is the bucket most likely to be a wrong default — never land here without having actively checked 1–3 against the evidence pasted, not just by elimination of ones not provided.
6. **Quote the exact evidence** that drove the classification — the specific substring, line, or field — never just assert a label.
7. **Give one concrete fix**, keyed to the bucket (see Output format). If evidence is genuinely ambiguous between two buckets, say so and name the one missing input that would resolve it, rather than forcing a single answer.

## Output format
Always return this structure:

```
## Diagnosis: <bucket name>
**Confidence**: High | Medium | Low

**Evidence**
<exact quoted substring(s) from the pasted completion/template/parser error, with a one-line explanation of why it points to this bucket>

**Fix**
<one concrete, specific action — a template patch, a parser tolerance change, a JSON-repair step, or (last resort) a model/prompt change>

**If that doesn't fix it**
<the next thing to check, or the one missing input that would raise confidence>
```

Bucket-specific fix defaults:
- **Chat-template rendering bug** → show the exact template fragment to patch (escape the literal braces, remove/fix the few-shot example), and note whether a known community-fixed template exists for that model family worth checking first.
- **Parser/extraction gap** → specify the exact tolerance to add (strip code fences, trim leading/trailing non-JSON text, accept trailing commas) rather than "make the parser more robust."
- **Malformed-but-recoverable output** → recommend a JSON-repair pass (e.g. `json_repair`-style lenient parsing) before the strict parser, and name the specific defect to repair.
- **Genuine model reasoning/argument-choice failure** → only now suggest a model-level fix: a clarifying few-shot example in the prompt, a simplified/more explicit tool schema, or — as the last resort, not the first — a larger or different model.

## Guardrails
- Never classify without the raw model completion in hand — a description of the failure is not evidence.
- Never default to "genuine model reasoning failure" by elimination of missing inputs — only reach that bucket after actively checking for template leakage and parser/format issues in what *was* provided, and say explicitly if a missing input (template, parser error) means that bucket can't yet be confirmed.
- Never fabricate a known template bug, stars/commit history, or a "fix" that wasn't derivable from the pasted evidence or common, verifiable public knowledge about that model family's template — if unsure whether a specific family has a known bug, say "no confirmed known bug for this family" rather than inventing one.
- Never tell the user to install, configure, or wire up a proxy/wrapper — this skill works from a single paste only; if they want always-on automatic capture across a running stack, say that's a different (project-level) tool, not this skill.
- Never collapse the four buckets back into a single pass/fail or "accuracy" number — the entire point is to keep the causes distinct.
