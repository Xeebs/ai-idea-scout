---
name: eval-judge-model-migration-compatibility-shim
description: Audits an LLM-as-judge eval config (promptfoo, deepeval, or custom) before swapping the judge model to a different one, flagging every saved parameter that will break, needs renaming, or needs re-ranging — and warning if either model ID is an unpinned alias that could silently shift scores later.
---

# Judge Swap Migration Audit

## When to use this

The trigger moment is **before** a judge-model swap is applied, not after it breaks. Reach for this skill when a user says something like "I'm switching my eval judge from `o3-mini` to `gpt-4o-mini`," "we're upgrading our judge model, what will break," or is actively editing the `provider`/`model` field of a judge config in promptfoo, deepeval, or a custom LLM-as-judge harness. Also applies when a user reports a judge-swap error (a 400, a silently-shifted score distribution) after the fact — same audit, run retroactively to explain the failure.

Do not use this for general eval-quality questions ("is my judge biased") or for swapping the *model under test* — only for swapping the *judge* model itself, where saved request parameters (reasoning effort, response format, token-limit keys, temperature bounds) are the thing that breaks.

## Inputs

**Data source**: Connected — the idea this skill is drawn from assumes a provider's live model-capability metadata endpoint (e.g. OpenAI/Anthropic `/models`-style APIs) as the long-term source of truth; that connector is not yet a standard, mature integration anywhere, so this skill works today without it. In practice this skill runs on two input paths: (1) whatever current judge config the user pastes (MANUAL — the judge's provider/model fields and every saved request parameter: `reasoning_effort`, `response_format`, `max_tokens`/`max_completion_tokens`/`max_output_tokens`, `temperature`, `top_p`, any provider-specific flags), and (2) the target model's documented parameter support, which this skill tries to get live via WebSearch against current provider docs first, falling back to whatever capability docs/changelog the user pastes in if a live search comes up empty or ambiguous for a given parameter.

Required from the user:
1. The current judge configuration — paste the exact YAML/JSON block, or the relevant lines of code, that sets the judge's model and its request parameters.
2. The target judge model's name/ID.
3. Optional but helpful: the target model's provider docs page or changelog entry, if the user already has it handy (skip the live-search step for that parameter).

## Procedure

1. **Extract the full current judge parameter set** from what the user pasted: provider, model ID/alias, and every request parameter set on the judge call (reasoning/thinking controls, response-format/structured-output settings, token-limit key and value, temperature, top_p, any other model-specific flags). Note the config's framework shape (promptfoo YAML, deepeval Python/JSON, or unrecognized/custom) — this determines the output snippet's syntax later, not the compatibility logic itself.
2. **Build the target model's capability profile.** For each parameter found in step 1, determine whether the target model supports it, under what name, and with what accepted range/enum:
   - If the user pasted target-model docs, use those directly and cite them as the source.
   - Otherwise, run a WebSearch against the target provider's current documentation for that specific parameter (e.g. "`<target model>` reasoning_effort support", "`<target model>` max_completion_tokens vs max_output_tokens", "`<target model>` temperature range"). Cite the URL found.
   - If neither pasted docs nor search give a confident answer for a parameter, mark it `UNVERIFIED` rather than guessing — never assume compatibility or incompatibility without a cited source.
3. **Classify every parameter from step 1** against the target profile into exactly one status:
   - `COMPATIBLE` — same name, value is within the target's accepted range/enum, no change needed.
   - `INCOMPATIBLE` — target model does not accept this parameter at all (e.g. `reasoning_effort` on a non-reasoning model). Action: drop it.
   - `RENAMED` — target model wants the same concept under a different key (e.g. `max_tokens` → `max_completion_tokens`, or vice versa depending on provider/API generation). Action: rename, keep value if still valid.
   - `RANGE-CHANGED` — key name is fine but the saved value falls outside what the target accepts (e.g. `temperature: 1.5` against a target whose max is `1.0`). Action: clamp or remap to nearest valid value, flagged for human confirmation.
   - `UNVERIFIED` — could not confirm from any source. Action: "confirm manually before migrating."
4. **Check both model IDs for alias risk.** If either the current or target model ID is an unpinned alias (no explicit dated/snapshot suffix — e.g. a bare family name or a "-latest" style tag) rather than a specific dated snapshot, flag it: the provider can silently repoint that alias to a new underlying model later, shifting judge scores without any config change at all. If the provider is known to offer dated/snapshot IDs for that model family, name a specific snapshot ID found via search or pasted docs as the suggested pin; if none was found, say so explicitly rather than inventing one.
5. **Assemble the output** per the format below, including a ready-to-paste corrected config snippet matching the framework shape detected in step 1 (or a generic parameter list if the framework wasn't recognizable).
6. **Close with a manual-confirmation list** — every parameter marked `UNVERIFIED` in step 3, plus a one-line reminder that even a fully `COMPATIBLE`/fixed config can still produce different scores under the new judge, so a canary run comparing old-judge vs. new-judge scores on a held-out sample is recommended before fully cutting over.

## Output format

A single Markdown report, "Judge Migration Diff: `<current model>` → `<target model>`", containing:

1. A parameter table:

   | Parameter | Current value | Status | Action | Source |
   |---|---|---|---|---|
   | reasoning_effort | high | INCOMPATIBLE | drop | <docs URL or "pasted docs"> |
   | max_tokens | 2000 | RENAMED → max_completion_tokens | rename key, keep value | <docs URL> |
   | temperature | 1.5 | RANGE-CHANGED (target max 1.0) | clamp to 1.0, confirm with team | <docs URL> |

2. **Alias risk** section — one paragraph per model ID flagged in step 4, or "No alias risk detected — both IDs are pinned snapshots" if neither is flagged.
3. **Corrected config** — a ready-to-paste block in the same syntax as the input (promptfoo YAML, deepeval config, etc.), with every `INCOMPATIBLE`/`RENAMED`/`RANGE-CHANGED` fix applied and a comment marking what changed and why.
4. **Confirm manually** — bullet list of every `UNVERIFIED` parameter, plus the canary-run reminder from step 6.

## Guardrails

- Never mark a parameter `COMPATIBLE` or `INCOMPATIBLE` without a cited source (pasted docs or a specific search result) — mark it `UNVERIFIED` instead of guessing.
- Never invent a dated/snapshot model ID that wasn't actually found in documentation or search results; say "no pinned snapshot found" rather than fabricate one.
- Never claim this audit replaces actually re-running the eval — a fully parameter-compatible config can still produce materially different scores under a new judge; always recommend a canary comparison before full cutover.
- Never silently apply the corrected config — always present it as a diff for the user to review and apply themselves.
- Never guess the framework's exact config syntax if it can't be identified from the pasted input; fall back to a generic parameter list rather than outputting plausible-looking but wrong promptfoo/deepeval syntax.
- This skill audits judge-model swaps specifically (reasoning/format/token/temperature parameters on the judge call) — do not scope-creep into auditing the model under test, prompt changes, or dataset drift.
