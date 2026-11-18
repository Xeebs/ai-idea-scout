---
name: dialect-speech-community-data-collection-toolkit
description: Drafts the three launch artifacts a community organizer needs before starting a spontaneous/colloquial speech data-collection campaign for an under-resourced language or dialect — a consent & IP disclosure script, an open-ended elicitation prompt set tuned to surface colloquial speech, and a native-speaker moderator review rubric. Use before launching any such campaign, not after.
---

# Dialect & Colloquial Speech Collection Launch Packet

## When to use this
A grassroots language-preservation group, diaspora organization, or small NLP researcher collective is about to start collecting spontaneous/colloquial speech from an under-resourced language or dialect community (for ASR training, documentation, TTS, or a translation-memory substrate) and has no written consent script, no elicitation prompts, and no review process yet — they have a channel to collect audio (WhatsApp, Telegram, web upload, or in-person recording) but nothing drafted for what to say to contributors or how to check what comes in. This is a pre-launch drafting step, never a replacement for actually running the collection platform or for local legal review.

## Inputs
**Data source**: Manual — the organizer types in the language/dialect name, region, intended use of the data, who is organizing the campaign, which channel will be used, and any legal/governance context they already know. This skill does not connect to WhatsApp Business API, Telegram Bot API, or any other API — those are the parent project's Connected data sources for actually *receiving* voice-note submissions once a campaign is live; this skill only drafts the paperwork and prompts that have to exist *before* that platform goes live, from what the organizer tells it directly.

The organizer provides:
1. **Language/dialect name and region** (required) — e.g. "Siwu, Ghana" or "Lunfardo-inflected Rioplatense Spanish, Buenos Aires".
2. **Intended use of the data** (required) — ASR training, documentation/archival, TTS, translation-memory substrate, academic research, or a mix.
3. **Who is organizing** (required) — grassroots community group, diaspora organization, academic/NLP researcher collective, NGO — this changes the tone and trust framing of the consent script.
4. **Collection channel** (required) — WhatsApp voice notes, Telegram voice notes, web upload, in-person recording — this changes whether consent needs to be spoken (recorded) or can be written/clicked.
5. *(Optional)* Known legal/governance context — country, any applicable data-protection law, a tribal/community governance body, or an Indigenous data sovereignty framework the community already follows. If the organizer doesn't know, say so; do not guess.
6. *(Optional)* Whether minors or other vulnerable speakers might contribute.

## Procedure
1. **Check for missing or ambiguous required inputs first.** If language/region, organizer type, or channel is missing, ask for it before drafting anything — do not fill gaps with assumptions. If intended use is given but left open across multiple options (e.g. "could be ASR, could be archival"), either ask which applies or, if proceeding without asking, draft for the broader combined case and say so explicitly in the output rather than silently picking one.
2. **Flag the legal-review gap immediately.** If no legal/governance context was given, state plainly, before drafting anything else, that the consent script below is a starting draft only and must be reviewed by someone with actual knowledge of the community's legal and cultural context before real use.
3. **Draft the Consent & IP Disclosure Script**, in plain language appropriate to a spoken read-aloud (if the channel is voice-note) or a written click-through (if web upload), covering all of:
   - Purpose of collection and the specific intended use named in step 1 (not a vague "research purposes").
   - Voluntary participation and the right to stop or withdraw a submission, and how to actually do that on the stated channel.
   - Who owns the recording afterward and what rights the contributor keeps (this must be stated plainly, not buried).
   - How the data will be stored, who can access it, and whether it will ever be shared outside the organizing group (e.g. released as an open dataset, used to train a model others can use).
   - Any community-specific governance note the organizer supplied (e.g. an Indigenous data sovereignty principle), inserted verbatim rather than paraphrased if given exactly.
   - A specific check for minors/vulnerable speakers if flagged in input 6, requiring guardian consent language.
   - Produce both a **spoken-script version** (if the channel is voice-note) and a **short written/click-through version** (for a web form), even if only one channel was named, since campaigns often add a web fallback later.
4. **Generate the Elicitation Prompt Set** — 15 to 25 open-ended prompts, grouped into these bands, calibrated toward the intended use named in step 1 (e.g. favor procedural/how-to prompts if the use is ASR for a voice assistant; favor personal-narrative and cultural prompts if the use is documentation/archival):
   - Personal narrative (describe your day, a memory, a recent event).
   - Local knowledge / culture (a recipe, a local custom, a piece of advice elders give).
   - Community-specific topic (something unique to this region/dialect, supplied or inferred only from what the organizer stated — never invent a specific local custom or place name that wasn't given).
   - Opinion / debate (something people in the community disagree about or discuss).
   - Procedural / how-to (explain how to do or make something).
   Every prompt must be answerable in free spontaneous speech — never a prompt that invites reading a fixed sentence aloud.
5. **Draft the Moderator Review Rubric** for native-speaker moderators checking incoming submissions, covering:
   - Consent confirmation (was the consent script actually heard/read and affirmed before the clip begins).
   - Audio usability (audible, not cut off, actual speech present).
   - Authenticity check (is this spontaneous speech in the target dialect, not a read-aloud sentence or a different dialect/language).
   - Dialect/region tag to apply.
   - Flag categories: needs re-recording, needs clarification from contributor, exclude (no consent / off-topic / unusable), accept.
   - A one-line note field for anything moderators should escalate to the organizer (e.g. a contributor who seems underage, content that needs community-specific sensitivity review).
6. **Compile the Launch Packet** as one document with the disclaimer banner (guardrail below) at the top, the three sections in order (Consent, Prompts, Rubric), and a closing line restating that this is a drafting aid, not a legal or ethical clearance.

## Output format
```
## ⚠ Before you launch
<One paragraph: this packet is a starting draft, not a substitute for legal/community
governance review; name what's still missing (e.g. "no legal context was provided —
have this reviewed before using it with real contributors").>

## 1. Consent & IP Disclosure Script
### Spoken version (voice-note channel)
<script text>
### Written version (web/click-through channel)
<script text>

## 2. Elicitation Prompts (<N> total)
### Personal narrative
- ...
### Local knowledge / culture
- ...
### Community-specific
- ...
### Opinion / debate
- ...
### Procedural / how-to
- ...

## 3. Moderator Review Rubric
| Check | Pass criteria | Flag if... |
|---|---|---|
| Consent confirmed | ... | ... |
| Audio usability | ... | ... |
| Authenticity | ... | ... |
| Dialect/region tag | ... | ... |
| Escalation note | ... | ... |

## Still open before this campaign can launch for real
- <bulleted list of anything the organizer didn't provide or that needs outside review>
```

## Guardrails
- **Never present the drafted consent/IP script as legally sufficient.** Always state explicitly that it needs review by someone with real legal or community-governance knowledge of this specific population before use with real contributors — this is a drafting aid, not legal clearance.
- **Never invent a specific local custom, place name, community debate topic, or legal/governance detail** that the organizer didn't supply. If a prompt band needs local specificity and none was given, write the prompt generically (e.g. "describe a local tradition you grew up with") rather than fabricating a named tradition.
- **Never draft a prompt that invites scripted/read-aloud speech** — every elicitation prompt must call for spontaneous, free-form answers; this skill exists specifically because scripted-sentence tools (e.g. Mozilla Common Voice) already cover read-aloud ASR and this gap does not.
- **Never skip the minors/vulnerable-speaker check** — if the organizer didn't say whether minors might contribute, or gave an unclear/hedged answer (e.g. "probably not, but we haven't restricted it"), treat it the same as unknown: ask, or default to including guardian-consent language and list the policy as a flagged open item rather than treating a hedge as a firm "no."
- **Never claim this skill runs, stores, or transmits any data** — it drafts text artifacts only; actually collecting audio requires the organizer's own platform (WhatsApp/Telegram/web upload), which this skill does not touch.
- **Never overwrite an existing consent process or legal review the organizer already has** — if they mention one exists, incorporate it rather than replacing it, and ask to see its key points if not supplied.
