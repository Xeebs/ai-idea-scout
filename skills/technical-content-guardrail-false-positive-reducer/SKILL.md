---
name: technical-content-guardrail-false-positive-reducer
description: Diagnoses why a team's AI safety guardrail is blocking legitimate technical/developer queries (process-kill commands, exploit/CVE discussion, pentest requests) and drafts a starter benign-vs-malicious labeled eval set plus root-cause category recommendations. Use when a team has a sample of guardrail false-positives from a coding assistant, DevOps copilot, or security-tooling product.
---

# Technical-Content Guardrail False-Positive Reducer

## When to use this
A team running an AI coding assistant, DevOps/SRE copilot, or security-research tool notices (or an engineer flags) that their safety guardrail is blocking legitimate technical requests — things like "write a script to kill this process," "craft a payload to test our rate limiter," or "explain this CVE for an internal writeup" — because the vocabulary overlaps with violence, hacking, or weapons categories. The team has (or can quickly pull) a sample of these flagged queries and wants to know why they're being blocked and what to do about it, before investing in a custom classifier or guardrail replacement.

This is a diagnostic/triage step, not the fix itself. It produces the artifacts (root-cause breakdown, starter eval set) a team needs before training or deploying a pre-filter — it does not train or deploy anything.

## Inputs
**Data source**: Manual — the team pastes a sample of queries their current guardrail has false-positived on (query text plus the guardrail's verdict/category, and ideally a human-confirmed ground-truth label of benign or malicious). There is no mature connector today that pulls this automatically from a guardrail gateway's audit log, so manual export is the honest v1.

Required per query, as a simple list or table:
1. **Query text** (verbatim, the actual user/developer input).
2. **Guardrail verdict** — what category or label the guardrail assigned (e.g., "Violence," "Hacking," "Weapons," "Blocked — unspecified"). If the team only has "blocked/allowed" with no category, note that explicitly.
3. **Ground-truth label**, if known — benign or malicious, confirmed by a human who understands the technical context. If not yet labeled, say so; the skill will flag these as needing review rather than guessing with false confidence.
4. Optional: the product/domain context (e.g., "DevOps copilot," "pentest-support tool," "general coding assistant") — sharpens the root-cause read.

Minimum useful sample: 10 queries. Below that, the root-cause breakdown is too thin to act on — say so and ask for more before producing a verdict.

## Procedure
1. **Parse each query** and identify the specific trigger vocabulary likely responsible for the flag (e.g., "kill," "exploit," "payload," "inject," "bypass," "attack," "crash," "backdoor," "exfiltrate").
2. **Infer the likely guardrail category** each trigger word maps to (Violence, Self-harm, Hacking/malicious code, Weapons, etc.) — cross-check against the guardrail's own reported verdict where given; flag any mismatch between the stated verdict and the inferred category as worth the team double-checking their gateway's logging.
3. **Classify intent** using the query's full context (not just the trigger word) into: benign-technical, genuinely-malicious, or ambiguous-needs-human-review. Use the ground-truth label when provided; when absent, make a provisional call and mark it provisional.
4. **Never treat a provided ground-truth label as wrong without saying so explicitly** — if the skill's own read of a query contradicts the team's human-confirmed label, state the disagreement and the reasoning, don't silently override it.
5. **Draft a matched eval-set pair** for each benign-technical query: the real benign text, paired with a *structurally similar but genuinely malicious* counterpart that uses the same trigger vocabulary. Keep the malicious counterpart abstract and intent-only (e.g., "a request to disable another party's production system without authorization") — never generate working exploit code, real payloads, or operational attack instructions, even for the "malicious" side of the pair.
6. **Aggregate** false-positive counts by inferred root-cause category across the whole sample, ranked by frequency.
7. **Recommend** per top category: whether it looks like a vocabulary-overlap problem (tunable via an allowlist/context rule) or a genuinely hard semantic distinction (needs a trained classifier, not a quick rule). Never recommend disabling a guardrail category outright — only tuning, exempting specific patterns, or escalating to the custom-classifier project, each with a human sign-off step named explicitly.
8. **Output** the full report per the format below.

## Output format
A single Markdown report with these sections, in order:

1. **Diagnostic Summary** — sample size, how many were benign-technical / genuinely-malicious / ambiguous, and the top 2–3 root-cause categories by frequency.
2. **Per-Query Breakdown** — a table: `Query | Guardrail Verdict | Trigger Vocabulary | Inferred Intent | Notes`.
3. **Draft Eval-Set Pairs** — a fenced code block, CSV-style: `id,benign_text,malicious_text,vocabulary,domain` — one row per benign-technical query from the sample. This is the starter corpus for the full project (which needs 200–300 pairs); label it clearly as a seed, not a finished eval set.
4. **Root-Cause Recommendations** — ranked list of categories with a tuning vs. train-a-classifier call for each, and the human sign-off step required before acting.
5. **Next Steps** — how many more labeled samples are needed to reach a usable eval set size, and a note on who should review the ambiguous queries.

## Guardrails
- Never generate real exploit code, working payloads, or step-by-step attack instructions when drafting the "malicious" side of an eval pair — keep it abstract and intent-level only. This skill produces training-data *shape*, not weaponizable content.
- Never override a human-confirmed ground-truth label silently — if your read disagrees, say so and explain why, and let the human decide.
- Never recommend disabling a guardrail category wholesale as a "fix" — only scoped tuning, pattern exemptions, or a path to a trained classifier, each flagged as needing human sign-off before deployment.
- Never present a diagnosis as final if the sample is under 10 queries or lacks any ground-truth labels — say the read is provisional and ask for more data instead.
- Never fabricate guardrail category names or false-positive statistics not present in the input — if the team didn't supply a category, say "category not provided" rather than guessing one as fact.
- This skill does not train, deploy, or evaluate a production classifier — it produces the diagnostic and seed data a team needs before that project starts. Don't imply the output alone fixes the guardrail.
