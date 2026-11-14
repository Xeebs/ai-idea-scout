# Policy Diff: Usage-Policy-to-Guardrail-Config Drift Detector

Paste this whole README into any AI chat tool (Claude, ChatGPT, etc.) along with your two inputs, and it will act as a one-shot auditor that tells you exactly which parts of your guardrail setup are now stale against a provider's updated usage policy.

## When to use this

A foundation-model provider (Anthropic, OpenAI, Google, or similar) just published a revised usage policy — a new prohibited-use clause, a reworded high-risk-domain carve-out, a changed rule on political content, weapons, surveillance, healthcare, or finance. You ship a production product on top of that provider's API and you need to know, right now, whether your own guardrails (content filters, system-prompt safety rules, blocked-topic lists, moderation classifier categories) still cover what the new policy requires — before compliance finds out the hard way, and without building or running any kind of ongoing automated watcher.

## What you need to provide

This is a manual, paste-it-in tool — nothing here reads your systems for you. Hand over:

1. **The provider's policy text.** Ideally both the old version and the new version (or a redline/changelog, if the provider publishes one). If you only have the new version, that's fine — say so, and the tool will run a full baseline audit instead of a diff.
2. **Your team's current guardrail/moderation config**, in whatever form it actually exists: a YAML or JSON rules file, a list of blocked topics or categories, the safety section of a system prompt, or a classifier's category list. Paste the real content — don't summarize it, since the mapping step needs the actual rule text.

## What it does (the procedure)

1. **Checks inputs.** If no old policy version is given, it proceeds as a "baseline audit" (every clause gets evaluated fresh) and says so up front rather than pretending to diff against nothing.
2. **Extracts policy clauses** from the new policy text as a numbered list — prohibited uses, high-risk domains (healthcare, finance, legal, critical infrastructure), political content, weapons, surveillance, abusive behavior toward the model/service, data handling, etc. — preserving the provider's own wording closely enough to trace back to the source.
3. **Diffs against the old version** (when supplied), classifying each clause as `ADDED`, `MATERIALLY CHANGED` (scope broadened/narrowed), `COSMETIC` (wording changed, scope identical), or `UNCHANGED`. Any genuinely ambiguous call defaults to `MATERIALLY CHANGED` so it doesn't get silently buried.
4. **Parses your guardrail config** from whatever structure you pasted. If part of it can't be parsed, it says exactly what couldn't be read instead of guessing.
5. **Maps each new/changed clause to the closest matching rule** in your config, if one exists, and assigns a verdict:
   - **GAP** — no rule addresses this clause at all.
   - **UNDER-COVERED** — a rule exists but its scope is narrower than the clause now requires.
   - **COVERED** — an existing rule's scope reasonably matches the clause.
   - **NEEDS HUMAN REVIEW** — the mapping is genuinely ambiguous and a human should confirm it.
6. **Leaves cosmetic/unchanged clauses out of the flagged table** — they get one unexpanded summary bullet so they don't drown out what actually needs action.

## What you get back

A single report, in this order:

1. **Header** — provider, policy versions/dates being compared (or "baseline audit"), and what config source you gave it.
2. **Flagged clauses table** — one row per `ADDED`/`MATERIALLY CHANGED`/baseline-evaluated clause, with columns for the clause text, its diff status, the config rule it mapped to (or "none found"), its verdict (GAP/UNDER-COVERED/COVERED/NEEDS REVIEW), and why.
3. **Summary counts** of each verdict.
4. **Low-priority changes** — a short bullet list of cosmetic/unchanged clauses, not expanded into the table.
5. **Caveats** — always included: this is an advisory triage aid, not a compliance certification. A human with legal/compliance authority should review every GAP and UNDER-COVERED row, and spot-check any COVERED row where the clause's wording differs a lot from the matching rule's wording, before anyone relies on this report.

## Rules it follows (so you can hold it to them)

- It will not invent or paraphrase away specific policy wording — clauses should be traceable back to what you pasted.
- It will not mark something "COVERED" just because a rule exists in the same general topic area — the rule's actual scope has to plausibly reach the clause's scope, or it's "UNDER-COVERED" instead.
- It will not skip a clause from the new policy text silently — if a clause genuinely has no guardrail relevance (e.g. a jurisdiction notice), it says so explicitly rather than dropping the row.
- It will not claim to be a legal or compliance opinion — it always ends with the human-review caveat.
- It will not fabricate an "old version" of the policy if you didn't provide one — it runs a baseline audit instead and says so.
- If your config is unparseable (e.g. described only in prose with no actual rule content), it will ask for the real rule text instead of guessing what your rules probably say.

## Why this exists

This is the companion skill to a larger continuously-running project idea (a scraper that watches a provider's policy page on a schedule and reads your guardrail config straight from your repo). That version is more thorough but takes time to build and run. This skill gets you the same flagged-gap report the moment a policy update is announced — paste, run, done — for teams who'd rather check manually right now than wait for a watcher to exist.
