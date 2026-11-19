---
name: platform-threat-classifier-tuning-toolkit
description: Reads a sample of a platform's own moderation decisions plus a description of its current guardrail's known misfires, and produces a go/no-go feasibility read on whether tuning a custom abuse classifier to that platform's own traffic is worth building, before anyone commits to an actual training pipeline.
---

# Threat Tune Feasibility Diagnostic

## When to use this
Use this when a trust-and-safety or platform-engineering team is weighing whether to invest in a custom-tuned abuse/content classifier — instead of continuing to rely on a generic foundation-model guardrail (e.g., NeMo Guardrails, Guardrails AI, LLM Guard, or a vendor API) — but doesn't yet want to commit engineering time to an active-learning fine-tuning build before knowing if their own moderation history actually supports it. The trigger moment is specifically: "we think our guardrail is misfiring on our own community's specific language, and we have a backlog of past human-moderator decisions — is it worth building something custom?" This is a one-shot diagnostic, not the training pipeline itself — it tells you whether to start the pipeline, not how to run it.

## Inputs
**Data source**: Manual — the user pastes or uploads (a) a de-identified sample export of 100–1,000+ recent human-moderator decisions as CSV/JSON (one row per decision: the content/text that was reviewed, the action taken — e.g., removed/warned/allowed/escalated, a reviewer identifier or "reviewer_id", and a timestamp), and (b) a short written description of their current guardrail's known false positives and false negatives (specific examples or categories of misfires, not just "it's not great"). This skill does not connect to any moderation system directly — a platform's mod-queue schema is never standardized enough for a universal connector, so the actual data pull in the full project is a per-platform export/adapter, and for this diagnostic the user supplies that export sample manually.

Required at minimum:
1. A sample export of moderation decisions (content text, action taken, timestamp; reviewer ID if available).
2. A plain-language description of the current guardrail's known failure modes, with at least 3-5 concrete examples of content it got wrong (flagged something benign, or missed something harmful).
3. Optional but useful: the platform type (forum, marketplace, dating app, gaming community, etc.) and the name/type of the current guardrail.

## Procedure
1. **Validate the sample.** Count total rows, count rows per action category (e.g., removed vs. allowed vs. warned), and check for an identifiable timestamp range (how recent is this traffic). If the sample is under ~100 rows total, or under ~20 rows in the minority (flagged) class, flag this explicitly as a sample-size blocker rather than silently proceeding.
2. **Check label consistency.** Scan for content that looks similar or repeats (same phrase, slur variant, or scam pattern) but received different actions from different reviewers or at different times. A high rate of this is a signal of reviewer disagreement or policy drift, which caps how good any classifier trained on this data can realistically get — call this out explicitly as a ceiling on achievable accuracy, not a reason to stop.
3. **Classify the guardrail's failure modes.** For each false positive/negative example the user described, categorize it as one of:
   - **Platform-vocabulary-driven** (e.g., gaming trash-talk read as harassment, marketplace slang read as scam language, in-group terms the generic guardrail doesn't know) — this is the category a tuned classifier is well-suited to fix, because it's exactly the kind of signal present in the platform's own mod log.
   - **Context-dependent ambiguity** (e.g., sarcasm, reclaimed slurs, borderline cases reasonable humans disagree on) — tuning helps less here; even a well-tuned classifier will struggle without more context than text alone provides.
   - **Rare/edge-case** (a handful of unusual incidents, not a recurring pattern) — too sparse in the sample to tune against; not a good target yet.
4. **Estimate recoverable improvement, qualitatively.** Cross-reference the failure-mode categories against what's actually represented in the sample: if most of the described failures are platform-vocabulary-driven AND the sample contains enough examples of that specific category (per step 1-2), estimate the opportunity as HIGH; if the failures are mostly context-dependent/ambiguous or the sample is too thin in the relevant category, estimate LOW; otherwise MEDIUM. State this as a qualitative band, never as a fabricated precision/F1/recall number — no ground-truth evaluation has actually been run.
5. **Produce a verdict**: GO, CONDITIONAL-GO (name the specific gap to close first, e.g., "collect 50 more examples of marketplace-scam false positives"), or NO-GO (name why — usually: sample too small, failures are mostly context-dependent, or label consistency too low to trust).
6. **Name the next concrete step** regardless of verdict: for GO, that's starting the actual active-learning labeling loop (the project, not this skill); for CONDITIONAL-GO, that's the specific data gap; for NO-GO, that's either waiting to accumulate more mod-log volume or accepting the generic guardrail's current rate.

## Output format
A single structured report with these sections, in this order:
1. **Sample Summary** — row count, class balance, time range, any consistency red flags found.
2. **Guardrail Failure-Mode Breakdown** — each described failure example sorted into platform-vocabulary / context-ambiguous / rare-edge-case, with a one-line reason for each categorization.
3. **Opportunity Estimate** — HIGH / MEDIUM / LOW, with the specific reasoning (never a fabricated metric).
4. **Verdict** — GO / CONDITIONAL-GO / NO-GO, one sentence.
5. **Recommended Next Step** — one concrete, specific action.

## Guardrails
- Never output a fabricated F1, precision, recall, or latency number — no model has been trained or evaluated at this stage; all estimates are qualitative bands (HIGH/MEDIUM/LOW) with stated reasoning, not invented statistics.
- Never recommend a GO verdict when the sample is under the minimum size threshold (step 1) without flagging the sample-size risk explicitly in the same breath.
- Never treat this diagnostic's output as a trained classifier or a deployment-ready artifact — it is strictly a feasibility read that precedes the actual active-learning fine-tuning pipeline (a separate, much larger build).
- Flag — every time, unprompted — that moderation-log content often contains real user data (usernames, personal details, sensitive accusations) and should be de-identified/anonymized before being pasted into any AI tool, including this one.
- Do not proceed with analysis if the "description of current guardrail failures" is missing or is only a vague complaint with zero concrete examples — ask for at least 3 concrete misfire examples first, since the entire failure-mode breakdown in step 3 depends on having real examples to categorize.
