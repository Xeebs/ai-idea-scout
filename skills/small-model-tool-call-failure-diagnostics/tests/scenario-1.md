# Scenario 1 — Qwen2.5 doubled-brace template leak

## Input (what the user pastes)

> I'm running Qwen2.5-7B-Instruct through Ollama and testing a `get_weather` tool. My eval harness flagged this as a tool-calling failure but I can't tell if it's the model's fault. Here's the raw completion:
>
> ```
> {{"name": "get_weather", "arguments": {{"location": "Paris", "unit": "celsius"}}}}
> ```
>
> The user's actual question was "what's the weather like in Osaka right now in Fahrenheit?"
>
> Tool schema sent:
> ```json
> {
>   "name": "get_weather",
>   "description": "Get current weather for a location",
>   "parameters": {
>     "type": "object",
>     "properties": {
>       "location": {"type": "string"},
>       "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
>     },
>     "required": ["location", "unit"]
>   }
> }
> ```
>
> Chat template fragment (the tool-call section of the Jinja template):
> ```jinja
> {%- for tool in tools %}
> Example call: {{"name": tool.name, "arguments": {{"location": "Paris", "unit": "celsius"}}}}
> {%- endfor %}
> ```
>
> Model: Qwen2.5-7B-Instruct, runtime: Ollama 0.4.x.

## Why this is realistic

This is the exact failure mode the idea's digest cited: Qwen2.5's chat template renders a worked example with doubled braces (`{{...}}`), and a small model copies that literal example — including its placeholder arguments ("Paris", "celsius") — instead of generating a call derived from the actual question (Osaka, Fahrenheit). All five recommended inputs are present and internally consistent.

## Pass criteria

- [ ] Diagnosis bucket is **chat-template rendering bug** (not "malformed output" or "model reasoning failure").
- [ ] Evidence quotes the literal doubled-brace output (`{{"name": ...}}`) AND connects it to the matching fragment in the pasted Jinja template, not just one or the other.
- [ ] Response explicitly notes that the arguments ("Paris", "celsius") match the template's own example values rather than anything derivable from the real question ("Osaka", "fahrenheit") — this is the smoking-gun detail that separates "template leak" from "model hallucinated an argument."
- [ ] Fix names the specific template patch: escape/fix the doubled braces in the example and/or remove the leaking few-shot example, and mentions checking for a known community-fixed Qwen2.5 tool-call template.
- [ ] Confidence is High (all needed evidence was provided and is unambiguous).
- [ ] Does NOT suggest installing a proxy/wrapper tool.
- [ ] Does NOT misclassify this as "genuine model reasoning failure" (the model didn't "choose" Paris/celsius — it copied them from the template).

## Fail conditions

- Classifying as anything other than chat-template rendering bug.
- Asserting the diagnosis without quoting both the raw output and the template fragment.
- Suggesting the fix is "use a bigger model" (that's the bucket-5 fallback, wrong bucket entirely here).
