---
name: eval-framework-schema-adapter-layer
description: Drafts a field-by-field mapping config (plus a dry-run preview and an unmapped-fields report) that translates a team's internal conversation/session data shape into the schema a named eval platform (LangSmith, Braintrust, Humanloop, or W&B Weave) expects, so a stalled eval-tool onboarding has a concrete next step instead of a bespoke glue script. Use when a team has an eval SaaS contract or trial and their first real data load into it failed or looked like a multi-week rebuild.
---

# Eval Framework Schema Adapter Layer

## When to use this
Reach for this when someone has already picked (or trialed) a named eval platform — LangSmith, Braintrust, Humanloop, or W&B Weave — and hit the same wall: their production data (nested conversation turns, custom session objects, domain-specific fields) doesn't match what the platform's dataset/example format expects, and the default response is "write a one-off sync script" or "give up and roll our own harness." Typical trigger phrases: "we have a LangSmith account but our data doesn't fit their dataset format," "how do I get our conversation logs into Braintrust without rewriting everything," "our eval onboarding has been stuck for two weeks on data formatting."

This is a one-time mapping *design* session — it produces a mapping config and a report a human reviews and runs. It does not call any API, does not move data anywhere, and does not set up a recurring sync job. If someone wants that mapping running continuously against new data as it's produced, say so explicitly: that's the adapter-service/infrastructure version of this idea, a different, bigger build than this skill.

## Inputs
**Data source**: Connected (target side) / Manual (source side) — target side is one of four named, mature eval-platform APIs (LangSmith, Braintrust, Humanloop, W&B Weave) whose documented example/dataset schema this skill reasons about by name; source side is necessarily Manual because no universal connector exists for an arbitrary team's internal data model — the user pastes a representative sample of their own internal objects as JSON.

Required:
1. **Target platform name** — exactly one of: LangSmith, Braintrust, Humanloop, W&B Weave.
2. **A sample of real internal data objects**, pasted as JSON — at least 3, ideally 5–10, covering any structural variation (e.g., turns with and without tool calls, sessions with and without a resolution field). Anonymize/redact PII or secrets before pasting; flag this to the user if the sample looks like it contains real customer identifiers, emails, or tokens.

Optional but improves accuracy:
3. **A pasted snippet of the target platform's current example/dataset schema docs** (field names, types, nesting rules) — platform schemas evolve, and this skill's built-in knowledge of them may be stale. If not supplied, proceed using documented-as-of-training-knowledge field names but flag every platform-side field name as "verify against current docs" in the output.
4. Which fields the team considers the "input," the "expected output," and pure "metadata" — if not stated, infer and flag the inference as a guess.

## Procedure
1. **Confirm the four required/common fields for the named target platform** from its example/dataset schema (use the pasted docs snippet if given; otherwise use best current knowledge and flag it as unverified):
   - LangSmith: each example needs an `inputs` dict and an `outputs` dict; optional `metadata` dict.
   - Braintrust: each dataset record needs `input`, `expected`, optional `metadata`, optional `tags`.
   - Humanloop: each datapoint needs `inputs` (flat key/value dict) and a `target`/expected-output field; optional `messages` for chat-shaped data.
   - W&B Weave: each dataset row is a flat dict of columns; there's no single fixed schema, but any `Evaluation` scorer function's argument names must match row keys exactly — so the real constraint is "whatever your scorer functions expect."
   State which of these you're using and that it should be spot-checked against the platform's current docs before a real sync.
2. **Parse the pasted sample objects.** Identify every leaf field path (including inside nested objects/arrays), note which fields repeat across samples vs. appear in only some (optional/variant fields), and note array fields that likely need flattening or joining (e.g., a `turns[]` array of role/content pairs).
3. **Classify the team's intent for each field** — which source field(s) correspond to the platform's "input" concept, which to "expected output," which to "metadata," and which look irrelevant to eval (internal IDs, timestamps unrelated to the eval signal). Use the team's stated mapping (input #4) if given; otherwise infer and mark each inference with a confidence flag (High/Medium/Low).
4. **Draft the mapping config** as YAML: one entry per target field, each with a `source` field path (dot/bracket notation into the sample objects) and, where needed, a `transform` (e.g., `flatten_array`, `join(", ")`, `concat`, `rename`, `extract_last`, `cast:string`). Keep the DSL to these six transform primitives — do not invent new transform syntax per field if an existing primitive covers it.
5. **Dry-run the mapping by hand against 2–3 of the pasted samples** and show the resulting transformed object for each, so the user can eyeball correctness immediately rather than trusting the YAML blind.
6. **List every target-required field with no clean source mapping.** For each, either (a) propose a transform/fallback that gets close enough and say what's lost, or (b) state plainly that this is a genuine schema gap on the team's side that the mapping cannot paper over (e.g., the platform requires a single `expected` string but the team has no ground-truth field at all).
7. **List source fields that were not used in any mapping.** Flag any that look substantive (not just internal bookkeeping) in case the team wants them preserved in the platform's `metadata` bucket instead of dropped.
8. **State explicitly what this session did and did not validate**: it validated field-shape compatibility by hand against the pasted sample, not live API behavior, not eval-score fidelity, and not the full production data distribution — recommend running the mapped output through the platform's actual free tier/sandbox against a larger batch before trusting it in CI.

## Output format
A single markdown report, in this order:

```
# Eval Schema Mapping Draft — <target platform>

## Platform schema used
<bullets of the target fields assumed, and whether they were confirmed from pasted docs or are unverified training knowledge>

## Mapping config (draft YAML)
```yaml
target_platform: <name>
mappings:
  - target: <platform field>
    source: <path into internal object>
    transform: <none | flatten_array | join | concat | rename | extract_last | cast:type>
    confidence: High | Medium | Low
...
```

## Dry-run preview (2–3 samples)
<for each: the original pasted sample, then the mapped output it produces>

## Fields that didn't map cleanly
| Target field | Issue | Suggested fix or "genuine schema gap" |
|---|---|---|

## Source fields left unused
| Field path | Looks substantive? | Suggestion |
|---|---|---|

## What this did NOT validate
<explicit caveat list — no live API call, no eval-score fidelity check, sample-size limits of the pasted data>
```

## Guardrails
- Never fabricate sample data, field names, or platform schema details that weren't pasted or weren't genuinely known — if the sample is too thin or ambiguous to map a field confidently, mark it Low confidence or list it as unmapped rather than guessing silently.
- Never present a platform's schema fields as current, verified fact when they came from this skill's own training knowledge rather than a pasted docs snippet — always flag that case as "verify against current docs," since all four platforms' APIs evolve.
- Never claim the mapping is "production ready" or "validated" — this is a draft checked by hand against a handful of pasted samples; the only thing that proves fidelity is running it against the real API with a larger batch, which is outside this one-time session.
- Never silently drop a source field that looks like it could be a ground-truth/expected-output signal — if nothing in the sample clearly maps to the platform's required expected-output field, say so as a genuine schema gap, don't invent a proxy mapping to force a green checkmark.
- Never treat this as a running sync job — if asked to "just connect it so it syncs automatically," state plainly that this skill only designs the one-time mapping; wiring it to run continuously against live data is a separate infrastructure build.
- If the pasted sample looks like it contains real PII, customer identifiers, auth tokens, or secrets, flag it immediately in the output and redact it inline (e.g., show `[REDACTED EMAIL]` in place of the real value) rather than echoing it verbatim in the dry-run preview — still complete the rest of the mapping report in the same response, with a note recommending the user redact at the source before using this for real engineering work.
