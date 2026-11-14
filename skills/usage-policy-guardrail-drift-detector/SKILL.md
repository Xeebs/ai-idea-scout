---
name: usage-policy-guardrail-drift-detector
description: Diffs a foundation-model provider's updated usage policy against a team's own guardrail/moderation config and flags which clauses are uncovered, under-covered, or now stale. Use when a provider (Anthropic, OpenAI, Google, etc.) publishes a usage-policy revision and the team needs to know whether their deployed guardrails still comply, without waiting to build the continuous watcher version of this idea.
---

# Policy Diff: Usage-Policy-to-Guardrail-Config Drift Detector

## When to use this
A foundation-model provider (Anthropic, OpenAI, Google, or similar) has published a revised usage policy — a new or reworded prohibited-use clause, a changed high-risk-domain carve-out, a new restriction on political content, weapons, surveillance, healthcare, or finance use cases. A team that ships a production LLM product on top of that provider's API needs to know, right now, whether their own guardrail config (content filters, system-prompt rules, classifier categories, blocked-topic lists) still covers the new or changed clauses — before legal/compliance notices an account-suspension risk, and before anyone has built or run a continuously-polling watcher for this.

## Inputs
**Data source**: Manual — the user pastes (or uploads as a file) two things: (1) the provider's policy text — ideally both the old and new versions, or a redline/changelog if the provider publishes one, but the new version alone is acceptable as a baseline run; and (2) their team's current guardrail/moderation configuration, in whatever form it exists (a YAML or JSON rules file, a list of blocked topics/categories, a system-prompt safety section, or a classifier category list). This is the deliberately lighter-weight companion to the idea's CONNECTED project (which polls the provider's policy page and reads the config straight from the team's GitHub/GitLab repo on a schedule) — this skill exists for the ad hoc moment before that watcher exists or fires, so both inputs are pasted by hand.

## Procedure
1. **Confirm inputs.** Require at minimum the new policy text and the guardrail config. If no old/prior policy version is supplied, proceed but mark the run as a **baseline audit** (every clause gets evaluated, not just a diff) rather than a drift diff, and say so explicitly in the output header.
2. **Extract policy clauses.** Parse the new policy text into a numbered list of discrete clauses/categories (e.g. prohibited uses, high-risk domains — healthcare, finance, legal, critical infrastructure — political content, weapons, surveillance, CSAM, abusive behavior toward the model/service, data handling). Preserve the provider's own clause wording verbatim; do not paraphrase away specificity.
3. **Diff against the old version (if supplied).** For each clause, classify as `ADDED` (no prior equivalent), `MATERIALLY CHANGED` (scope broadened or narrowed — e.g. a carve-out removed, a domain list extended), `COSMETIC` (wording changed but scope identical — e.g. reordering, synonym swaps), or `UNCHANGED`. Never classify a clause `MATERIALLY CHANGED` without citing the specific words that changed scope; if unsure whether a wording change is cosmetic or material, default to flagging it `MATERIALLY CHANGED` and let the human review step decide — never silently downgrade a close call to COSMETIC.
4. **Parse the guardrail config.** Identify the team's existing rule/category boundaries from whatever structure they pasted (YAML keys, JSON category list, prose rule descriptions, classifier labels). If the format is ambiguous or only partially parseable, say exactly which part couldn't be parsed rather than guessing at missing structure.
5. **Map each ADDED/MATERIALLY CHANGED/baseline clause to the closest matching config rule(s)**, if any. For each, assign one of:
   - `GAP` — no config rule addresses this clause's subject matter at all.
   - `UNDER-COVERED` — a rule exists but its scope is narrower than the clause now requires (name the specific gap between rule scope and clause scope).
   - `COVERED` — an existing rule's scope reasonably matches the clause.
   - `NEEDS HUMAN REVIEW` — the mapping is genuinely ambiguous (e.g. the clause is semantically covered by a rule but worded so differently that a human should confirm it wasn't a coincidental text match).
6. **Do not flag COSMETIC or UNCHANGED clauses as gaps** — list them in a low-priority summary line only, so the report doesn't bury the clauses that actually need action under noise.
7. **Produce the flagged report** (format below), then append the mandatory caveat block.

## Output format
A single markdown report with these sections, in order:
1. **Header** — provider name, policy versions/dates being compared (or "baseline audit, no prior version supplied"), and a one-line description of the config source the user pasted.
2. **Flagged clauses table** — columns: `Clause (verbatim or near-verbatim)` | `Diff status (ADDED/CHANGED/baseline)` | `Mapped config rule (or "none found")` | `Verdict (GAP/UNDER-COVERED/COVERED/NEEDS REVIEW)` | `Why`. One row per ADDED/MATERIALLY CHANGED/baseline-evaluated clause — never omit a clause from this table.
3. **Summary counts** — count of GAP, UNDER-COVERED, COVERED, NEEDS REVIEW.
4. **Low-priority changes** — one bullet list of COSMETIC/UNCHANGED clauses, unexpanded.
5. **Caveats (mandatory, always included verbatim in substance)**: this is an advisory mapping, not a compliance guarantee; a human with legal/compliance authority should review every GAP and UNDER-COVERED row, and spot-check COVERED rows where the clause wording differs substantially from the rule's wording, before relying on this report.

## Guardrails
- Never invent or paraphrase away specific policy wording — quote the clause closely enough that a reviewer can find it in the source text.
- Never mark a clause `COVERED` just because *some* rule exists in the same general topic area — the rule's actual scope must plausibly reach the clause's scope, or it's `UNDER-COVERED`.
- Never silently skip a clause that appears in the new policy text — if it's genuinely irrelevant to guardrail enforcement (e.g. a jurisdiction notice), say so explicitly rather than omitting the row.
- Never present this as a compliance certification or legal opinion — it is a triage aid; always end with the human-review caveat.
- Never fabricate "old version" text if the user didn't supply it — run as a baseline audit instead of pretending to diff against nothing.
- If the config format is unparseable (e.g. a screenshot described in prose with no actual rule content), say so and ask for the actual rule text/file rather than guessing what the rules probably are.
