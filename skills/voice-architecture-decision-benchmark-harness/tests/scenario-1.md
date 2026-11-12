# Scenario 1: Healthcare intake voice agent (regulated, bilingual)

## Input

A 5-person engineering team at a telehealth startup is building a voice agent that calls patients before their appointment to collect intake information: symptoms, current medications, allergies, and insurance details. They give the following answers:

1. **Domain/regulatory context**: US telehealth, HIPAA applies. All calls must be recorded and retained for 7 years, and intake transcripts get reviewed by a nurse before the appointment — they need accurate, auditable transcripts, not just a pass/fail outcome.
2. **Languages/vocabulary**: English and Spanish, with real medical terminology (medication names, dosages, allergy terms) that general-purpose voice models sometimes mis-transcribe or mis-pronounce.
3. **Latency/conversational feel**: Not a casual chat — patients expect a slower, clear, form-like pace. A half-second of extra latency between question and response is a non-issue; what matters is the agent correctly capturing what the patient said.
4. **Tool-calling needs**: The agent writes structured data to the EHR (electronic health record) mid-call (symptom codes, medication lookups against a formulary database) — a silent/incorrect write here is a patient safety issue, not just an inconvenience.
5. **Team size/expertise**: 5 engineers, two with prior NLP/speech experience; they're comfortable owning separate STT/LLM/TTS integration if it buys them more control and auditability.
6. **Vendor lock-in tolerance**: Low tolerance — as a regulated healthcare company, switching vendors later means re-validating the whole pipeline with compliance, so they want to minimize future forced migrations.

## Expected output characteristics (pass/fail checklist)

- [ ] Restates the use case correctly (telehealth intake, HIPAA, bilingual medical vocabulary, EHR writes, low lock-in tolerance)
- [ ] Scores compliance/observability at -2 (regulated/audit-required)
- [ ] Scores vocabulary specificity at -2 (narrow/technical/multi-language)
- [ ] Scores latency/naturalness priority at -1 (deliberate pace is fine)
- [ ] Scores tool-calling needs at -2 (costly silent failures: EHR writes)
- [ ] Scores team expertise/bandwidth toward cascaded (-1, team wants control) — not toward +2
- [ ] Scores lock-in tolerance at -2 (severe switching cost)
- [ ] Total sum is clearly ≤ -2, producing a **Cascaded** recommendation
- [ ] Confidence is stated as High (5-6 of 6 factors point the same direction)
- [ ] Names at least one specific risk of the cascaded path tied to a factor (e.g., integration/maintenance overhead across three vendors, team bandwidth)
- [ ] Names at least one specific risk of the speech-to-speech alternative tied to a factor (e.g., harder to audit transcripts for HIPAA review, vendor lock-in risk given regulatory re-validation cost)
- [ ] Does NOT cite a specific invented latency number for any named vendor
- [ ] Closes with a concrete validation step (e.g., pilot the cascaded stack on a sample of real bilingual intake calls and check medical-term transcription accuracy and EHR write correctness before full rollout)

**Fail conditions**: recommends speech-to-speech; invents vendor-specific latency numbers; skips the HIPAA/compliance risk callout; presents the recommendation as more than "Medium/High confidence, same-day judgment call."
