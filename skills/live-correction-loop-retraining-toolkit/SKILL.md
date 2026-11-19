---
name: live-correction-loop-retraining-toolkit
description: Turns a description of a nonprofit's live interpretation/translation/tutoring workflow and a sample of its volunteer correction pairs into a concrete capture-schema, retraining-cadence, and consent plan for standing up a correction-loop retraining pipeline. Use when an org already has volunteers correcting model output in real time but has no plan for turning those corrections into model improvement.
---

# Correction-Loop Integration Planner

## When to use this
Use this when a nonprofit, community org, or volunteer network running a live interpretation, translation, or tutoring service for an under-covered language already has volunteers correcting model/bot output in real time (in a shared inbox, WhatsApp group, Twilio-routed SMS line, or similar), and asks something like "how do we turn our volunteers' corrections into a better model?", "we're throwing away corrections our volunteers already make, what should we do with them?", or "what would it take to retrain on our own correction data?"

This is a one-time design/planning pass, not a running system. It produces the schema, integration recommendation, retraining plan, and consent checklist a team would hand to an engineer to build — it does not capture, store, or fine-tune anything itself.

## Inputs
**Data source**: Manual — the user describes their current workflow in chat and pastes a sample of recent correction pairs (e.g., a CSV or copy-pasted table of original-output / volunteer-correction rows). The org this skill is scoped from would eventually run a CONNECTED capture layer against the WhatsApp Business API or Twilio Conversations API (both mature, widely deployed today) to capture these pairs live from the channel they already use, with a manual CSV-upload path as the fallback for orgs not yet on a supported channel — but that live capture layer is a separate, not-yet-built system. This skill only ever works from what's described and pasted into the conversation.

What to hand over:
- The channel(s) currently used (WhatsApp, Twilio-routed SMS, a shared email/web inbox, in-person with manual logging, etc.) and roughly how many corrections happen per week.
- The language(s)/language pair(s) involved and whether any are written, spoken-only, or low-digitization languages (affects tokenization and eval choices).
- A sample of at least 10 recent (original model/bot output, volunteer correction) pairs — more is better; note if the sample is cherry-picked or a true random recent slice.
- Whether volunteers have ever been told their corrections might be used to retrain a model, and whether the end users (interpretation/tutoring recipients) have consented to their conversations being used this way.
- Any existing infra constraints (self-hosted only, no GPU budget, must use a specific base model, data residency requirements).

If the user has no correction-pair sample at all, still produce the schema and cadence/consent sections, but mark the Data Quality Assessment section `INSUFFICIENT DATA — no sample provided` rather than inventing example corrections.

## Procedure
1. **Summarize the current state** from the workflow description: channel, volume/week, language(s), where corrections currently go today (discarded, logged but unused, already informally reused).
2. **Design the correction-pair schema** — a concrete column list the org should start logging, minimum viable set: `source_text`, `model_output`, `volunteer_correction`, `language`, `correction_type` (factual error / fluency / register / omission / other), `timestamp`, `volunteer_id_or_anon_token`, `end_user_consent_flag`. Adjust only if the described workflow genuinely can't support a field (say which and why).
3. **Assess the pasted sample** for: (a) consistency — do multiple volunteers correct the same type of error the same way, or is correction style scattered; (b) coverage — do corrections cluster on one error type (e.g., always register/politeness) while leaving others (factual mistranslation) uncorrected; (c) volume-per-cadence — at the stated weekly rate, how many validated pairs accumulate in 4, 8, and 12 weeks. Call out noisy or inconsistent patterns explicitly rather than averaging over them.
4. **Recommend a capture integration** matched to the stated channel: WhatsApp Business API webhook (if on WhatsApp Business), Twilio Conversations API event hook (if on Twilio-routed SMS/voice-transcript), or the manual CSV-upload fallback (if on a shared inbox/manual log with no API). State plainly that the manual path works today with zero integration but caps throughput at whatever a human can export, while the API paths require a days-not-months integration per channel.
5. **Recommend a retraining plan** sized to the actual accumulation rate from step 3, not a generic cadence: for a volunteer network producing low tens of validated pairs per week, recommend batching into monthly or bimonthly LoRA fine-tunes of a small open-weight instruction/translation model rather than a weekly cadence that would retrain on near-empty batches; name the held-out-eval approach (reserve the most recent N% of pairs as a held-out set, re-run native-speaker-rated accuracy or COMET pre/post each retrain).
6. **Write the consent/privacy checklist** — treat this as blocking, not optional, whenever the population is refugees, students, or another vulnerable group: explicit opt-in from end users whose conversations become training data, anonymization/token-replacement of personally identifying content before storage, a stated retention/deletion policy, and volunteer awareness that their corrections (not just end-user text) become training data too.
7. **List open risks/blocking questions** specific to what was described — e.g., "no end-user consent process exists yet — do not proceed to capture until this is designed" or "sample shows only 4 distinct volunteers, so retrained model may encode one person's idiolect rather than community norms."

## Output format
A markdown report with exactly these sections, in order:
1. **Current State Summary** — channel, volume/week, language(s), today's fate of corrections.
2. **Correction-Pair Schema** — table: `Field | Type | Notes`.
3. **Data Quality Assessment** — consistency, coverage, and projected 4/8/12-week accumulation; `INSUFFICIENT DATA` if no sample was given.
4. **Capture Integration Recommendation** — one recommended path (WhatsApp Business API / Twilio Conversations API / manual CSV fallback) with the tradeoff stated.
5. **Retraining Plan** — base model class, fine-tune method (LoRA by default unless infra constraints say otherwise), cadence, and eval approach, sized to the actual accumulation rate from section 3.
6. **Consent & Privacy Checklist** — checklist format, each item marked `DONE` / `NOT DONE` / `UNKNOWN` based on what the user told you, never assumed `DONE`.
7. **Open Risks & Blocking Questions** — bullet list, specific to this org's inputs.

## Guardrails
- Never invent example correction pairs, volunteer counts, or volume numbers the user didn't provide — if a number is missing, ask for it or mark the dependent section `INSUFFICIENT DATA`.
- Never mark the Consent & Privacy Checklist item `DONE` unless the user explicitly stated that consent/anonymization process already exists — default unaddressed items to `NOT DONE` or `UNKNOWN`, and state in Open Risks that capture should not begin until consent is resolved whenever the population is vulnerable (refugees, children, patients, etc.).
- Never recommend a weekly or faster retraining cadence when the stated/observed volume would produce fewer than roughly 50-100 new validated pairs per cycle — recommend batching instead, and say why.
- Never claim this skill captured, stored, or fine-tuned anything — it is a one-time planning pass; the running capture pipeline, datastore, and retraining scheduler are a separate system this output is scoped to inform, not replace.
- Never treat a cherry-picked or tiny (under ~10 pairs) sample as representative — flag sample-size limitations explicitly in the Data Quality Assessment rather than drawing firm conclusions from it.
