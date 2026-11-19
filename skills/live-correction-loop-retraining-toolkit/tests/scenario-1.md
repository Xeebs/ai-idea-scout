# Scenario 1 — WhatsApp-based volunteer interpretation network, decent sample

## Input

A volunteer coordinator for a refugee-support nonprofit provides:

**Channel and volume**: "We run interpretation over WhatsApp Business. Refugees message our number in Tigrinya, a bot drafts an English translation using a small open-weight MT model, and one of our ~6 trained volunteer interpreters reviews and corrects the draft before it's forwarded to the caseworker. We get roughly 40-60 corrected messages a week."

**Language(s)**: Tigrinya <-> English. Tigrinya is written (Ge'ez script) but has very little digitized parallel text available for fine-tuning.

**Correction pair sample** (18 rows pasted, true recent slice, e.g.):
| original_model_output | volunteer_correction |
|---|---|
| "I need medicine for my son fever" | "I need medicine for my son, who has a fever." |
| "The appointment is at tomorrow 3" | "The appointment is tomorrow at 3 PM." |
| "She lost her document when came here" | "She lost her documents on the way here." |
| ...(15 more rows, mostly grammar/fluency fixes, a couple of real mistranslations like a swapped date) |

**Consent status**: "We've told our volunteer interpreters their corrections might be used to improve the bot. We have NOT told the refugees we serve that their messages could be used for training — we never thought about that until now."

**Infra constraints**: "No GPU budget beyond a single consumer GPU we already own; whatever we use has to run on that."

## Task

Run the skill's procedure against this input and produce the 7-section report.

## Pass criteria

- [ ] Section 1 (Current State Summary) correctly states channel (WhatsApp Business), volume (40-60/week), language pair (Tigrinya/English), and that corrections currently flow to caseworkers but aren't reused for retraining.
- [ ] Section 2 (Correction-Pair Schema) includes all required fields (source_text, model_output, volunteer_correction, language, correction_type, timestamp, volunteer_id_or_anon_token, end_user_consent_flag) in a table.
- [ ] Section 3 (Data Quality Assessment) notes the sample skews toward fluency/grammar corrections with only occasional factual (e.g., date) corrections, and projects accumulation at 4/8/12 weeks using the given 40-60/week rate (not an invented number) — roughly 160-240 pairs at 4 weeks, etc.
- [ ] Section 4 (Capture Integration Recommendation) recommends the WhatsApp Business API webhook path specifically (not Twilio, not manual-only), since the org already uses WhatsApp Business, and states the tradeoff language from the procedure.
- [ ] Section 5 (Retraining Plan) recommends a batched (monthly/bimonthly) LoRA fine-tune of a small open-weight model sized to fit a single consumer GPU, not a weekly cadence, and names a held-out-eval approach.
- [ ] Section 6 (Consent & Privacy Checklist) marks volunteer awareness as DONE, but end-user consent as NOT DONE — and explicitly states, because the population is refugees (vulnerable), that capture should not begin until end-user consent is resolved.
- [ ] Section 7 (Open Risks) raises the end-user consent gap as a blocking risk, and separately flags that Tigrinya's low digitized-text availability may limit how much the fine-tune can improve beyond what the volunteer corrections alone provide.
- [ ] Report does not invent any correction examples, volunteer counts, or numbers beyond what was given.
- [ ] Report explicitly states it has not captured/stored/fine-tuned anything itself.

## Fail conditions

- Marking end-user consent DONE or skipping the consent gap.
- Recommending Twilio or a generic "an API" instead of the WhatsApp Business API webhook.
- Recommending a weekly retraining cadence at this volume.
- Fabricating example corrections or volunteer counts not in the input.
