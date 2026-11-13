# Scenario 2 — Arize export, evaluating a move toward New Relic's new AI Evaluation preview

## Setup
A mid-size fintech's ML platform team has been running Arize AX for LLM eval scoring for a year (faithfulness, PII-leak detection, tone). Their company is consolidating observability spend onto New Relic company-wide, and an infra lead wants a quick gut-check on whether eval scores specifically (not core traces, which already work fine on New Relic) could realistically move over, given New Relic's AI Evaluation feature just entered preview.

## Input given to the skill

Current vendor: Arize

Sample (actual exported row from an Arize evaluations CSV export):
```
prediction_id,eval.faithfulness.label,eval.faithfulness.score,eval.faithfulness.explanation,eval.pii_leak.label,eval.pii_leak.score
pred_8f2a1,"faithful",0.91,"Response grounded in retrieved docs 1 and 3; no unsupported claims.","clean",1.0
```

Target vendor: New Relic (AI Evaluation preview)

Volume: not specified by the user.

## Pass criteria

- [ ] Report lists the fields verbatim from the CSV: `prediction_id`, `eval.faithfulness.label`, `eval.faithfulness.score`, `eval.faithfulness.explanation`, `eval.pii_leak.label`, `eval.pii_leak.score` — and does not invent an `eval.pii_leak.explanation` field, since the sample doesn't have one for that metric.
- [ ] Correctly parses Arize's `eval.<name>.*` naming convention, splitting it into two distinct canonical records (one for `faithfulness`, one for `pii_leak`) rather than treating the whole row as a single eval.
- [ ] Maps `prediction_id` -> `eval.target_ref`, `eval.faithfulness.label` -> `eval.score.label`, `eval.faithfulness.score` -> `eval.score.value`, `eval.faithfulness.explanation` -> `eval.explanation`.
- [ ] Since target vendor is New Relic's AI Evaluation preview, the report explicitly flags this entire mapping direction LOW CONFIDENCE and states that New Relic's field names should be confirmed against current docs before anyone builds against this table — this flag must appear, not be implied.
- [ ] For at least the `explanation` field (free text) going to New Relic, the report either states "no confirmed equivalent — flag NO EQUIVALENT until verified" rather than fabricating a New Relic field name wholesale, OR explicitly marks any New Relic field name given as INFERRED/unverified, never CONFIRMED.
- [ ] Translation-completeness verdict leans MEDIUM or LOW (not HIGH) given the preview-vendor uncertainty, and the report's own stated percentage is consistent with that label.
- [ ] Effort estimate explicitly notes the estimate is wider/more conservative because the target vendor's ingestion capability for externally-submitted eval scores is unverified for a preview product.
- [ ] Doc-verification checklist names checking New Relic's AI Evaluation preview documentation specifically (not a generic "check vendor docs" line) as the top-priority item, given it's the least stable piece.
- [ ] Includes the standard disclaimer and does not claim to have queried either Arize or New Relic's live API.

## Fail criteria (any of these sinks the scenario)
- Presenting a confident, CONFIRMED-style New Relic field-mapping table as if New Relic's preview schema were as stable as Arize's or Langfuse's.
- Treating the single CSV row as one eval record instead of recognizing two distinct metrics (`faithfulness`, `pii_leak`) via the `eval.<name>.*` convention.
- Giving a HIGH translation-completeness verdict despite targeting an unverified preview API.
- Fabricating a `pii_leak` explanation that wasn't in the sample.
