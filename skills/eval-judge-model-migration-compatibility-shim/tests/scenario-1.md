# Scenario 1: promptfoo judge swap, reasoning-model to non-reasoning-model (the PostHog bug, reproduced)

## Setup

A team runs promptfoo in CI to grade a RAG pipeline's answers using an LLM-as-judge assertion. They've been using `o3-mini` as the judge and are migrating to `gpt-4o-mini` to cut cost. This is the exact failure class documented in the real-world `PostHog/posthog#133640` PR this idea is built on: a saved reasoning-effort level breaking a judge-model switch.

## Input handed to the skill

Current judge config (promptfoo YAML, `promptfooconfig.yaml` excerpt):

```yaml
defaultTest:
  assert:
    - type: llm-rubric
      provider:
        id: openai:o3-mini
        config:
          reasoning_effort: high
          max_completion_tokens: 2000
      value: "Answer must correctly cite the source document and avoid fabricated figures."
```

Target judge model: `gpt-4o-mini`

Target model docs: not provided — skill must search live.

## Expected output (what a correct run looks like)

- Parameter table includes at minimum:
  - `reasoning_effort: high` → `INCOMPATIBLE` (gpt-4o-mini is not a reasoning model and does not accept this parameter) → action: drop. Must cite an actual source (search result or reasoning).
  - `max_completion_tokens: 2000` → classified; since both o3-mini and gpt-4o-mini are OpenAI Chat Completions-era reasoning/non-reasoning models that generally both accept `max_completion_tokens`, this should land as `COMPATIBLE` (or `UNVERIFIED` if the tool can't confirm gpt-4o-mini's exact accepted key via search — either is acceptable as long as it's not silently assumed INCOMPATIBLE without checking, and not left uncategorized).
  - Implicitly or explicitly notes that `temperature`/`top_p` were never set in the original config, so no action needed there (shouldn't invent parameters that weren't present).
- Alias risk section: flags `o3-mini` and/or `gpt-4o-mini` as bare family names with no dated snapshot suffix, and warns that OpenAI can repoint which exact underlying checkpoint these names serve. If the tool can find a currently-documented dated snapshot (e.g. a `gpt-4o-mini-<date>` form) it should suggest it and cite where it found it; if it can't find one confidently, it must say so rather than invent a date.
- Corrected config: a promptfoo YAML block with `reasoning_effort` removed/commented out and a note explaining why, `provider.id` updated to `openai:gpt-4o-mini`, and `max_completion_tokens` either kept or adjusted per its classification above.
- Confirm-manually list includes the canary-run reminder, plus any UNVERIFIED items.

## Pass / fail criteria

- PASS requires: `reasoning_effort` correctly flagged `INCOMPATIBLE` with a drop action (this is the core PostHog-bug reproduction — failing this is a hard fail).
- PASS requires: alias risk is raised for at least one of the two bare model names (not skipped entirely).
- PASS requires: the corrected config snippet is in valid-looking promptfoo YAML syntax matching the input's shape, not a generic/abstract format.
- PASS requires: no fabricated snapshot ID or fabricated documentation citation — if a snapshot ID is suggested, it must be presented as found-via-search or explicitly caveated as not found.
- FAIL if: the tool claims `reasoning_effort` is compatible with `gpt-4o-mini`, or drops it silently without flagging it in the table/diff for the user to see.
- FAIL if: no parameter table or no corrected config block is produced.
