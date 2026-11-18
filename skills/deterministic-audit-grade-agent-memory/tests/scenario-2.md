# Scenario 2: Healthcare triage copilot, HIPAA audit prep

## Input

**Memory schema/config:**
- Zep, used as the memory layer for a clinical triage assistant.
- Retrieval: hybrid search — BM25 keyword match combined with semantic (embedding) similarity, blended score, top-k = 8.
- Post-retrieval step: the 8 raw retrieved facts are passed through an LLM "condensation" call (same model, temperature 0) that summarizes them into a short paragraph before the paragraph is shown to the clinician-facing agent — raw facts are not shown directly.
- No metadata filtering beyond `patient_id` (exact match, applied before hybrid search).

**Audit context:** Internal HIPAA audit-trail prep — the compliance team wants to document, for every patient-facing recall, exactly why a specific fact appeared (or didn't) in what the clinician saw.

**Query/recall variance examples:**
1. Query: "What are this patient's documented allergies?" (patient_id=70921). Two different clinicians asked this identical question nine minutes apart, same session day, no corpus changes in between. Clinician A's agent response (via the condensation step) read: "Patient has documented allergies to penicillin and shellfish." Clinician B's agent response read: "Patient has a documented penicillin allergy." The shellfish allergy fact was present in Zep's raw retrieved set both times (confirmed via Zep's own trace logs) but was dropped from the condensation output only on the second call.
2. Query: "Any recent patient-reported pain symptoms?" (patient_id=70921). Run twice back-to-back with no corpus change: hybrid search's raw top-8 set was identical both times (confirmed via trace logs), but the condensation paragraph phrased the same two facts in a different order and slightly different wording each time — clinically equivalent content, but compliance is unsure if this phrasing variance itself is an audit concern or a non-issue.

## Pass criteria

The output should:
- Inventory at least three distinct paths: the `patient_id` exact-match filter, the hybrid (BM25 + semantic) search, and the LLM condensation step — three separate entries, not merged.
- Classify the condensation step as NON-DETERMINISTIC explicitly because it is LLM-based, even though temperature is 0 — and must not claim temperature 0 makes it deterministic.
- Correctly attribute example #1 (the dropped shellfish allergy) specifically to the condensation step, not to the hybrid search — the scenario explicitly states the raw retrieved set was identical (confirmed via trace logs) both times, so blaming retrieval would be a factual misread of the given evidence.
- Rank the condensation step as the top (or tied-top) audit risk, and give a reason that reflects it can drop clinically relevant content (the allergy), not merely reorder it — distinguishing this from example #2's purely cosmetic phrasing variance.
- For the condensation step, NOT propose a canonicalization key as the fix (that is the wrong tool for a summarization-drop failure) — instead recommend the appropriate fix, such as returning the raw structured fact list (already deterministic per-path once hybrid search's own non-determinism is addressed) to the clinician-facing output instead of, or in addition to, the condensed paragraph, removing the lossy step from the audited path.
- Still classify the hybrid search path as NON-DETERMINISTIC in general (semantic component) and may optionally sketch a canonicalization key for it (e.g. `patient_id + fact_type (allergy/pain_symptom) + onset_date`), but must not claim hybrid search caused example #1.
- Address example #2 by noting the cosmetic-wording variance is a separate, lower-severity issue than the content-dropping variance in example #1, rather than treating them as equally severe.
- Not assert "HIPAA requires X" as a legal conclusion — may reference HIPAA audit-trail expectations generically since the user did name HIPAA this time, but should stay in the lane of a technical/engineering review, not legal advice.

## Fail conditions

- Misattributing the dropped allergy fact to the search/retrieval path instead of the condensation step.
- Treating temperature-0 LLM output as deterministic.
- Proposing a canonicalization key as the fix for the condensation step's content-dropping behavior.
- Treating examples #1 and #2 as equally severe.
- Issuing a legal compliance verdict (e.g. "this setup is/is not HIPAA compliant") rather than a technical reproducibility assessment.
