# Judge Swap Migration Audit

A paste-in prompt template for auditing an LLM-as-judge evaluation config *before* you swap the judge model to a different one. Use it with any AI chat tool (ChatGPT, Claude, Gemini, etc.) that can do a live web search — no installation, no eval framework required.

## Why this exists

Every eval framework that uses an LLM as a judge (promptfoo, deepeval, custom harnesses) saves request parameters alongside the judge model: things like a reasoning-effort level, a response-format/structured-output setting, a max-token key, a temperature. These parameters are model-specific. When you swap the judge model — which happens routinely as providers deprecate and replace models every few months — those saved parameters often don't survive the swap:

- A saved `reasoning_effort: high` causes a 400 error on a non-reasoning target model.
- A token-limit key like `max_tokens` needs to become `max_completion_tokens` or `max_output_tokens` depending on the target model's API generation.
- A `temperature` value that was valid on the old model (e.g. 1.5) can silently exceed the new model's accepted range (e.g. max 1.0).
- If either model ID is an unpinned alias (no dated snapshot), the provider can repoint it later and your judge's scores can shift with zero config change at all — the hardest kind of breakage to catch.

No eval framework ships a built-in audit for this today — it gets discovered one breakage at a time, in production, as a runtime error or a silently-shifted score. This prompt does the audit up front.

## What to hand this

Paste all of the following into the chat along with this prompt:

1. **Your current judge configuration** — the exact YAML/JSON/code block that sets the judge's provider, model, and every request parameter on that judge call (reasoning/thinking settings, response-format/structured-output settings, token-limit parameter and value, temperature, top_p, any other model-specific flags).
2. **The target judge model's name or ID** you're migrating to.
3. **(Optional)** Any documentation page or changelog entry you already have for the target model's supported parameters — this saves the tool a search step and lets it cite your source directly. If you don't have this, the tool will search for it itself, live, using current provider documentation; if it can't find a confident answer for some parameter, it will say so rather than guess.

## The prompt

```
You are auditing an LLM-as-judge evaluation config for a judge-model swap, before I apply it.

Current judge config:
<paste your judge config here — provider, model, and every request parameter set on the judge call>

Target judge model: <name/ID>

Target model docs (optional, skip if you don't have this — I'll search instead):
<paste docs/changelog here if you have them>

Do the following:

1. List every request parameter in my current judge config (reasoning/thinking controls, response-format/structured-output settings, the token-limit key and its value, temperature, top_p, any other model-specific flags).

2. For each parameter, determine whether the target model supports it, under what name, and within what range/enum. Use the docs I pasted if I gave you any; otherwise search the live web for the target provider's current documentation on that specific parameter and cite the source URL you used. If you cannot find a confident answer for a parameter from any source, mark it UNVERIFIED instead of guessing — do not assume compatibility or incompatibility without a citation.

3. Classify every parameter into exactly one of:
   - COMPATIBLE — same name, value within target's accepted range, no change needed.
   - INCOMPATIBLE — target model doesn't accept this parameter at all. Action: drop it.
   - RENAMED — target wants the same concept under a different key. Action: rename, keep the value if still valid.
   - RANGE-CHANGED — key is fine, value is out of range for the target. Action: clamp/remap, flagged for me to confirm.
   - UNVERIFIED — no confident source found. Action: I need to confirm manually.

4. Check both the current and target model IDs: is either one an unpinned alias (a bare family name or a "-latest"-style tag, not a specific dated/snapshot ID)? If so, warn me that the provider can silently repoint that alias to a different underlying model later, shifting my judge's scores with no config change on my end. If the provider offers dated/snapshot IDs for that model family, tell me the specific one you found (cite your source) as a suggested pin. If you can't find one, say so — don't invent a snapshot ID.

5. Give me the output as:
   - A markdown table: Parameter | Current value | Status | Action | Source
   - An "Alias risk" paragraph (or "no alias risk detected" if neither ID is a bare alias)
   - A corrected config block in the same format/syntax as what I pasted, with every fix applied and a comment on each change
   - A "confirm manually" list of every UNVERIFIED parameter, plus a reminder that even a fully compatible config can produce different judge scores on the new model — recommend I run a canary comparison (old judge vs. new judge, same held-out sample) before fully cutting over.

Do not apply anything automatically — this is a diff for me to review. Do not claim this replaces actually re-running the eval.
```

## What you get back

A single report with:
1. A parameter-by-parameter compatibility table with a cited source for every row.
2. An alias-risk warning naming any unpinned model ID and, where found, a specific snapshot ID to pin to instead.
3. A corrected config snippet, ready to paste back into your eval framework, with every change commented.
4. A short list of anything the tool couldn't verify, plus a reminder to run a canary comparison before full cutover — passing this audit cleanly does not guarantee identical scores, only that the request itself won't error or silently drop settings.

## Limits

- This audits the *judge* model swap specifically — not the model under test, not prompt drift, not dataset staleness.
- It can only cite what it finds via your pasted docs or a live search; if provider documentation for a parameter is thin or absent, expect `UNVERIFIED` rows rather than false confidence.
- It will not invent model IDs, snapshot names, or capability claims it didn't actually find a source for.
