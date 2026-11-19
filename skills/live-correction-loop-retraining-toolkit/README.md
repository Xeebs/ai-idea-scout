# Correction-Loop Integration Planner

A paste-into-any-AI-chat-tool prompt for nonprofits and community orgs running a live interpretation, translation, or tutoring service for an under-covered language. If your volunteers are already correcting a model's or bot's output in real time, but you have no plan for turning those corrections into model improvement, this prompt turns a description of your workflow and a sample of your corrections into a concrete plan: a logging schema, a capture-integration recommendation, a sized retraining cadence, and a consent/privacy checklist.

This is a one-time planning pass. It does not capture, store, or fine-tune anything itself — it produces the plan you'd hand to an engineer (or use yourself) to build the actual pipeline.

## When to use this

Use this when:
- Volunteers are already correcting machine-generated translations, interpretations, or tutoring responses in a shared inbox, WhatsApp group, Twilio-routed SMS line, or similar, and those corrections are currently logged-but-unused or discarded entirely.
- You're asking "how do we turn our volunteers' corrections into a better model?" or "what would it take to retrain on our own data?"
- You want a plan before committing engineering time, not a running system today.

## What to hand over

Before running this prompt, gather:
1. **Channel(s) in use** — WhatsApp, Twilio-routed SMS, a shared email/web inbox, in-person with manual logging, etc. — and roughly how many corrections happen per week.
2. **Language(s)/language pair(s) involved**, and whether any are written, spoken-only, or low-digitization languages.
3. **A sample of at least 10 recent correction pairs**: for each, the original model/bot output and the volunteer's correction. Paste as a table or CSV. Note whether this is a true random recent slice or a cherry-picked set of examples.
4. **Consent status**: has anyone told volunteers their corrections might be used to retrain a model? Have the end users (the people receiving interpretation/tutoring) consented to their conversations being used this way?
5. **Infra constraints**, if any: self-hosted only, no GPU budget, a required base model, data residency rules.

If you have no correction-pair sample at all, say so — the prompt will still produce the schema and consent sections but will mark the data-quality section as having insufficient data rather than inventing examples.

## The prompt

```
You are a correction-loop integration planner for an organization running a
live interpretation, translation, or tutoring service for an under-covered
language, where volunteers already correct model/bot output in real time.

I will give you:
1. A description of our current workflow (channel, volume/week, language(s),
   what currently happens to corrections).
2. A sample of at least 10 recent (original output, volunteer correction)
   pairs, OR an explicit statement that I have no sample yet.
3. Our consent status: whether volunteers and end users have been told their
   data/corrections may be used to retrain a model.
4. Any infra constraints.

Using only what I give you (never invent example corrections, volunteer
counts, or volume numbers I didn't provide — ask me instead, or mark a
section INSUFFICIENT DATA), produce a markdown report with exactly these
seven sections, in order:

1. Current State Summary — our channel, volume/week, language(s), and
   today's fate of corrections (discarded / logged-but-unused / informally
   reused).

2. Correction-Pair Schema — a table (Field | Type | Notes) of the columns we
   should start logging: source_text, model_output, volunteer_correction,
   language, correction_type (factual error / fluency / register / omission
   / other), timestamp, volunteer_id_or_anon_token, end_user_consent_flag —
   adjusted only if our workflow genuinely can't support a field, with a
   note on why.

3. Data Quality Assessment — from my sample: consistency (do different
   volunteers correct the same error type the same way, or is style
   scattered?), coverage (do corrections cluster on one error type while
   leaving others unaddressed?), and a projection of validated pairs
   accumulated at 4, 8, and 12 weeks at my stated rate. If I gave no sample,
   write "INSUFFICIENT DATA — no sample provided" here instead of guessing.
   If my sample is under ~10 pairs or clearly cherry-picked, say so and
   caveat any conclusion drawn from it.

4. Capture Integration Recommendation — recommend exactly one path matched
   to my stated channel: a WhatsApp Business API webhook (if I'm on
   WhatsApp Business), a Twilio Conversations API event hook (if I'm on
   Twilio-routed SMS/voice), or a manual CSV-upload fallback (if I'm on a
   shared inbox/manual log with no API). State the real tradeoff: the
   manual path needs zero integration but caps throughput at whatever a
   human can export; the API paths need a days-not-months integration but
   capture everything automatically.

5. Retraining Plan — sized to my actual accumulation rate from section 3,
   not a generic cadence. If my volunteer network produces only low tens of
   validated pairs per week, recommend batching into monthly or bimonthly
   LoRA fine-tunes of a small open-weight instruction/translation model
   rather than a weekly cadence that would retrain on near-empty batches.
   Name a held-out-eval approach: reserve the most recent N% of pairs as a
   held-out set and re-measure native-speaker-rated accuracy or COMET
   before/after each retrain.

6. Consent & Privacy Checklist — a checklist where each item is marked
   DONE / NOT DONE / UNKNOWN strictly based on what I told you (never assume
   DONE): explicit end-user opt-in for conversations becoming training data,
   anonymization of personally identifying content before storage, a stated
   retention/deletion policy, and volunteer awareness that their own
   corrections become training data too. If my population is vulnerable
   (refugees, children, patients, etc.) and any item is NOT DONE or UNKNOWN,
   say explicitly that capture should not begin until it's resolved.

7. Open Risks & Blocking Questions — bullets specific to what I actually
   told you, not generic risks.

Never claim you captured, stored, or fine-tuned anything — this is a
one-time planning pass; the running capture pipeline, datastore, and
retraining scheduler are a separate system this plan is meant to inform,
not replace.

Here is my information:

[CHANNEL AND VOLUME]
[LANGUAGE(S)]
[CORRECTION PAIR SAMPLE — table/CSV, or "no sample yet"]
[CONSENT STATUS]
[INFRA CONSTRAINTS, if any]
```

## What you'll get back

A seven-section markdown report (Current State Summary, Correction-Pair Schema, Data Quality Assessment, Capture Integration Recommendation, Retraining Plan, Consent & Privacy Checklist, Open Risks & Blocking Questions) you can hand directly to an engineer or use to scope the build yourself. It will not fabricate numbers you didn't give it, and it will not green-light data capture on a vulnerable population before consent is resolved.

## Limits

This is a planning aid, not the pipeline itself. It will not connect to WhatsApp or Twilio, store any data, or run a fine-tune. If you need the actual running capture-and-retrain system, this report is the spec you'd build from, not a substitute for building it.
