# Eval Framework Schema Adapter Layer

A paste-anywhere prompt template for the moment you've signed up for (or trialed) an LLM eval platform — LangSmith, Braintrust, Humanloop, or W&B Weave — and your first attempt to load real data into it stalled because your internal data doesn't match the schema it expects. Instead of writing a one-off glue script or giving up and building a bespoke eval harness from scratch, this produces a draft mapping config, a dry-run preview against your actual data, and a precise list of what doesn't map and why.

This is a **one-time design session**, not a running integration. It doesn't call any API or move your data anywhere — it drafts a mapping you (or an engineer) then run yourself. It's the "figure out the mapping" half of the job; actually wiring it to sync continuously is separate infrastructure work this is not meant to replace.

## When to use this

- You have a LangSmith/Braintrust/Humanloop/Weave contract or free trial, and loading your production conversation/session data into it looked like it would require restructuring your data model.
- Your onboarding has stalled for days or weeks on "how do we get our data into their format."
- You're about to write a bespoke sync script and want a clear picture of exactly which fields are the hard part before you commit engineering time.

## What you need to provide

**Data source note**: the target platform's schema is something this skill reasons about by name (LangSmith, Braintrust, Humanloop, or W&B Weave are all mature, documented platforms) — but your internal data has no universal connector, so you provide it manually, pasted directly into the chat.

Give the assistant:

1. **The target platform name** — exactly one of: LangSmith, Braintrust, Humanloop, or W&B Weave.
2. **A sample of your real internal data objects, pasted as JSON** — at least 3, ideally 5–10 examples. Include any structural variation you have (e.g., some conversations with tool calls, some without; some sessions with a resolution field, some without). **Redact or anonymize any real customer PII, emails, or auth tokens before pasting** — the assistant will flag this and ask you to redo it if it spots obvious sensitive data.
3. *(Optional, recommended)* **A pasted snippet of the target platform's current example/dataset schema docs.** Platform schemas change over time, and without this the assistant is relying on its training knowledge of the schema, which it will flag as unverified.
4. *(Optional)* Which of your fields you consider the "input," the "expected output," and pure "metadata." If you skip this, the assistant will infer it and mark each guess with a confidence level.

## What the assistant will do

Paste this prompt along with your inputs above into any AI chat tool:

> I need help mapping my internal data into [PLATFORM NAME]'s eval dataset schema. Here is a sample of my data: [paste 3-10 JSON objects]. [Optionally: here's the platform's current schema docs: [paste]]. [Optionally: my input field is X, expected output is Y, metadata is Z.]
>
> Please:
> 1. State the target fields [PLATFORM NAME] requires for an eval example/dataset record, and whether you're using docs I gave you or your own training knowledge (flag the latter as unverified and worth double-checking).
> 2. Parse my sample objects and identify every field path, including nested/array fields, and which fields vary across samples.
> 3. Classify which of my fields map to the platform's input, expected-output, and metadata concepts — use my stated mapping if I gave one, otherwise infer and mark your confidence (High/Medium/Low) on each guess.
> 4. Draft a mapping config as YAML — one entry per target field, with a source field path and a transform if needed (only use: none, flatten_array, join, concat, rename, extract_last, cast:type).
> 5. Dry-run the mapping by hand against 2-3 of my pasted samples and show me the resulting transformed object for each.
> 6. List every target-required field that didn't map cleanly — for each, either suggest a transform/fallback and say what's lost, or tell me plainly it's a genuine schema gap on my side (e.g., I have no ground-truth field at all).
> 7. List any of my source fields that went unused, and flag which of those look substantive enough that I might want them kept in metadata instead of dropped.
> 8. End with an explicit list of what this did NOT validate — no live API call was made, no eval-score fidelity was checked, and this is only as good as the handful of samples I gave you.

## What you'll get back

A single report structured like this:

```
# Eval Schema Mapping Draft — <target platform>

## Platform schema used
(the target fields assumed, and whether confirmed from your docs or unverified)

## Mapping config (draft YAML)
target_platform: <name>
mappings:
  - target: <platform field>
    source: <path into your object>
    transform: <none | flatten_array | join | concat | rename | extract_last | cast:type>
    confidence: High | Medium | Low

## Dry-run preview (2-3 samples)
(your original sample, then the mapped output)

## Fields that didn't map cleanly
(table: target field | issue | suggested fix or "genuine schema gap")

## Source fields left unused
(table: field path | looks substantive? | suggestion)

## What this did NOT validate
(explicit caveats)
```

## What this will never do

- Never invent field names, sample data, or platform schema details that weren't given to it or genuinely known — if something's too ambiguous, it marks it low-confidence or unmapped rather than guessing silently.
- Never call it "production ready" — it's a hand-checked draft against a handful of samples, not a validated integration. Running it against the real API with a larger batch is the step that actually proves it works.
- Never quietly drop a field that looks like it could be your ground-truth/expected-output signal — if nothing maps to the platform's required expected-output field, it says so as a real gap rather than forcing a fake mapping.
- Never treat this as a live sync — if you ask it to "just connect it so it updates automatically," it will tell you that's a separate infrastructure build, not what this session does.
- Never echo back sensitive-looking data (PII, tokens, customer identifiers) verbatim — it gets flagged and redacted inline (e.g., shown as `[REDACTED EMAIL]`) while the rest of the mapping report still completes in the same response, with a note to redact at the source before real use.

## Example use

You've just gotten a Braintrust trial and tried uploading your support-bot's conversation logs, but Braintrust wants `input`/`expected` and your logs are nested session objects with a `turns` array, a `resolution_status` enum, and no single "correct answer" field anywhere. Paste 5-10 real (redacted) session objects plus "Braintrust" as the target, and you'll get back a mapping draft that flattens `turns` into something Braintrust-shaped, an honest flag that `resolution_status` isn't the same as an `expected` ground truth and you'll need to either add one or use it as a proxy metric instead, and a dry run showing exactly what your first three sessions would look like once mapped.
