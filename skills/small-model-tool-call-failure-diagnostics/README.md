# Small-Model Tool-Call Failure Diagnostics

A paste-in prompt template for diagnosing why a tool call / function call from a small, open-weight local LLM (Qwen2.5/3, Llama 3.x, Mistral, Hermes-family — typically sub-8B, served through Ollama, llama.cpp's `server`, or vLLM) failed. Instead of shrugging and saying "the model is just bad at tool calling," this walks through a fixed diagnostic order and tells you which of four distinct root causes actually happened, with the exact evidence and a concrete fix — no installation, no proxy, no wired-up tooling. Just paste the failure and go.

## When to use this

Use this when you're debugging a specific, single tool-calling failure from a small local model and you have (or can get) the raw text the model actually generated. Good trigger phrases: "why did this tool call fail", "is this a template bug or is the model just dumb", "my tool-calling eval score dropped, here's one example that failed."

**Do not use this for:**
- Failures from hosted frontier models like Claude or GPT-4-class models — they rarely hit the template/parser-level bugs this is built around; their failure surface is different.
- A vague "my overall accuracy is low, why" question with no specific failed example attached. Ask for one concrete failed trace first — this tool diagnoses one failure at a time, not an aggregate score.
- An always-on, automatic capture system across a live running server. This is a one-shot manual triage for a single pasted trace, not a monitoring proxy.

## Inputs

**Data source: Manual.** You paste the failure details directly into the chat. This tool does not connect to Ollama's REST API, llama.cpp's `server` HTTP API, or vLLM's OpenAI-compatible endpoint on its own — if you want automatic, always-on capture across a running server stack instead of pasting one failure at a time, that requires a separate always-on wrapper/proxy tool (not this one).

To get a diagnosis, provide:

1. **The raw model completion** (required, non-negotiable) — the exact, uncleaned text the model generated for the tool call attempt, including any surrounding commentary, markdown fences, or stray characters. Do not paraphrase or "clean it up" first — the raw bytes are the evidence.
2. **The tool schema that was sent** (required) — the JSON definition(s) of the tool(s) offered to the model on that turn.
3. **The chat template used** (strongly requested if the raw output looks suspicious — literal `{{`/`}}`, stray Jinja tags, or placeholder-looking values) — the Jinja/prompt template fragment that renders the tool definitions and any few-shot tool-call examples into the prompt.
4. **The parser error or extraction code**, if something downstream rejected the output — the exact regex/JSON-parse step and its error message.
5. **Model name and runtime** (e.g. "Qwen2.5-7B-Instruct via Ollama") — helps match against known template bugs for that model family.

If the raw completion is missing, the tool should stop and ask for it rather than guess from a description. If the template or parser error is missing but the output shows signs it's needed, ask for it, but a lower-confidence provisional diagnosis is fine while waiting.

## Procedure

Work through these checks **in this fixed order** — do not skip ahead to "the model is wrong" by default:

**Step 1 — Completeness check.** If the raw model completion isn't provided, stop and request it. Don't classify from a description alone.

**Step 2 — Check for a chat-template rendering bug first** (cheapest to confirm, and the most commonly misdiagnosed as "the model is just bad"):
- Does the raw completion contain literal, un-rendered template syntax — doubled braces (`{{`, `}}` appearing as literal text instead of valid JSON), stray Jinja delimiters, or a few-shot *example* tool call's placeholder value copied verbatim instead of a real value derived from the actual request?
- If the chat template was provided, search it for the matching fragment and confirm the leak traces back to it.
- Known family bug to check for: Qwen2.5's tool-call template has historically rendered its own worked example with doubled braces, which small models then copy literally into their real output.

**Step 3 — If no template leak, check for a parser/extraction gap:**
- Is there a syntactically valid tool call *somewhere* in the output, but wrapped in something a naive parser wouldn't strip — a markdown code fence (` ```json `), a preamble sentence ("Sure, here's the call:"), trailing commentary after the JSON, or escaped-unicode/non-ASCII in argument values that trips a narrow regex?
- If a parser error message was given, check whether it's complaining about exactly this kind of wrapping (e.g. "unexpected token" where the unexpected token is a stray newline or backtick, not the JSON itself).

**Step 4 — If the call is unwrapped but still fails to parse, check for malformed-but-recoverable output:**
- Is the JSON *almost* valid — a trailing comma, an unescaped internal quote, a missing closing brace, a field named `parameters` when the schema expects `arguments` (or vice versa), single quotes instead of double?
- The intended tool and roughly-intended arguments must be clearly recoverable by a human reading it to land in this bucket. If it's not recoverable, it's either a worse parser gap (bucket 2) or escalates to bucket 5.

**Step 5 — Only after buckets 2–4 are actively ruled out (not just unavailable), classify as a genuine model reasoning/argument-choice failure:**
- The output is syntactically perfect and matches the schema exactly, but the model picked the wrong tool for the request, or supplied plausible-but-wrong/hallucinated argument values (an invented file path, a misread number from context, etc).
- Never land here by elimination of inputs you didn't get — only by having actually checked template and parser causes against what was provided, and explicitly flag if a missing input (template or parser error) means you can't fully confirm this bucket yet.

**Step 6 — Quote the exact evidence.** Always cite the specific substring, line, or field from what was pasted that drove the classification. Never assert a label without a quote backing it.

**Step 7 — Give exactly one concrete fix**, matched to the bucket (see fix table below). If the evidence is genuinely ambiguous between two buckets, say so explicitly and name the one missing input that would resolve the ambiguity, rather than forcing a single confident answer.

## Output format

Always respond in this exact structure:

```
## Diagnosis: <bucket name>
**Confidence**: High | Medium | Low

**Evidence**
<exact quoted substring(s) from the pasted completion/template/parser error, with a one-line explanation of why it points to this bucket>

**Fix**
<one concrete, specific action>

**If that doesn't fix it**
<the next thing to check, or the one missing input that would raise confidence>
```

Fix defaults by bucket:
- **Chat-template rendering bug** → point to the exact template fragment to patch (escape the literal braces, remove or fix the few-shot example that's leaking), and mention whether a known community-fixed template exists for that model family worth checking first.
- **Parser/extraction gap** → name the exact tolerance to add (strip code fences, trim leading/trailing non-JSON text, accept trailing commas) — never just "make the parser more robust."
- **Malformed-but-recoverable output** → recommend a lenient JSON-repair pass before the strict parser, naming the specific defect to repair (trailing comma, wrong field name, etc).
- **Genuine model reasoning/argument-choice failure** → only now suggest a model-level fix: a clarifying few-shot example, a simplified/more explicit tool schema, or — as a last resort, not the first move — a larger or different model.

## Guardrails

- Never classify a failure without the raw model completion in hand. A description of what happened is not evidence.
- Never default to "genuine model reasoning failure" just because the template or parser info wasn't provided — that bucket requires actively ruling out the other three with what *was* given, and an explicit note if something's missing that blocks full confidence.
- Never invent a "known template bug" for a model family, a GitHub star count, commit history, or a fix that isn't derivable from the pasted evidence or genuinely common public knowledge. If unsure whether a model family has a confirmed known bug, say so rather than making one up.
- Never tell the user to install, configure, or wire up a proxy/monitoring wrapper. This is a single-paste, zero-install triage tool. If they want automatic capture across a live running server, say that's a different kind of tool, not this one.
- Never collapse the four buckets back into one pass/fail verdict or a single "accuracy" number — keeping the causes distinct is the entire point.
