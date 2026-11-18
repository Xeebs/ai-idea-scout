# Dialect & Colloquial Speech Collection Launch Packet

A paste-into-any-AI-chat-tool prompt that drafts the three documents a community organizer needs before launching a spontaneous/colloquial speech data-collection campaign for an under-resourced language or dialect — a consent & IP disclosure script, a set of open-ended elicitation prompts that actually surface colloquial speech instead of scripted reading, and a native-speaker moderator review rubric.

## When to use this

You are a grassroots language-preservation group, a diaspora organization, or a small NLP researcher collective about to collect real, spontaneous speech from a community (for ASR training, documentation, text-to-speech, or a translation-memory project) and you have a way to receive audio — WhatsApp voice notes, Telegram voice notes, a web upload form, or in-person recording — but you haven't yet written down what to tell contributors, what to ask them to say, or how your moderators will check what comes in.

This tool does not collect, store, or transmit any audio. It only drafts the text artifacts you need before you go live. It is also not a substitute for real legal or community-governance review — it tells you explicitly, every time, what still needs that review.

## What you need to provide

**Data source note**: Everything below is information you type in yourself (Manual). This tool never connects to WhatsApp, Telegram, or any other API on its own — those are the channels your campaign will actually use to receive voice notes once it's live, and this tool doesn't touch them. It only works from what you tell it directly.

Give the AI:
1. **Language/dialect name and region** (required) — e.g. "Siwu, Ghana" or "Lunfardo-inflected Rioplatense Spanish, Buenos Aires."
2. **Intended use of the data** (required) — ASR training, documentation/archival, text-to-speech, translation-memory, academic research, or a combination.
3. **Who is organizing the campaign** (required) — a grassroots community group, a diaspora organization, an academic/NLP research collective, or an NGO.
4. **Collection channel** (required) — WhatsApp voice notes, Telegram voice notes, web upload, or in-person recording.
5. *(Optional)* Any legal or governance context you already know — country, applicable data-protection law, a tribal or community governance body, or an Indigenous data sovereignty framework the community follows. If you don't know, say so plainly rather than guessing.
6. *(Optional)* Whether minors or other vulnerable speakers might be contributing.

## The prompt to paste

```
You are helping me draft the launch packet for a speech data-collection campaign
for an under-resourced language/dialect community. You are NOT collecting,
storing, or transmitting any data — you are only drafting three text artifacts:
a consent & IP disclosure script, a set of elicitation prompts, and a moderator
review rubric.

My inputs:
- Language/dialect and region: <fill in>
- Intended use of the data: <fill in>
- Who is organizing this: <fill in>
- Collection channel: <fill in>
- Known legal/governance context (or "none known"): <fill in>
- Minors/vulnerable speakers possible? <yes/no/unsure>

Before drafting anything:
1. If I left any required field blank, ask me for it instead of guessing. If my
   intended use is open across multiple options (e.g. "could be ASR, could be
   archival"), either ask which applies or draft for the combined broader case
   and say so explicitly rather than silently picking one.
2. Regardless of what I said about legal/governance context, state plainly, up
   front, that everything you draft is a starting point only and needs review by
   someone with real legal/community-governance knowledge of this specific
   population before I use it with real contributors — even if I named a law
   that applies, that is not the same as a lawyer having reviewed this script.
3. If my answer on minors/vulnerable speakers is a hedge rather than a clear
   yes/no (e.g. "probably not, but we haven't restricted it"), treat it as
   unresolved: default to including guardian-consent language and list the
   minors policy as an open item, rather than treating a hedge as a firm "no."

Then produce:

## 1. Consent & IP Disclosure Script
Draft BOTH a spoken-script version (for a voice-note channel, read aloud before
recording starts) and a short written/click-through version (for a web form),
even if I only named one channel. Cover: the specific purpose/use I named (not a
vague "research purposes"); that participation is voluntary and how to withdraw
on my stated channel; who owns the recording afterward and what rights I as a
contributor keep, stated plainly; how the data will be stored and whether it's
ever shared outside the organizing group or released as an open dataset; my
governance context verbatim if I gave you exact wording; and, if I said minors
might contribute, explicit guardian-consent language.

## 2. Elicitation Prompts (15-25 total)
Open-ended prompts only — nothing that invites reading a fixed sentence aloud,
since that's what Mozilla Common Voice already does and is NOT this gap. Group
into five bands: personal narrative, local knowledge/culture, a community-
specific topic, opinion/debate, and procedural/how-to — weighted toward whichever
bands fit my stated intended use (e.g. more procedural prompts for a voice-
assistant ASR use case, more personal-narrative/cultural prompts for a
documentation/archival use case). Never invent a specific local custom, place
name, or community debate topic I didn't give you — write generically instead
if you don't have real specifics.

## 3. Moderator Review Rubric
A table for native-speaker moderators reviewing incoming clips, covering:
consent confirmation, audio usability, authenticity (spontaneous speech in the
target dialect, not read-aloud or a different dialect), the dialect/region tag
to apply, and an escalation note field for anything (like a possibly-underage
contributor) that needs to go back to me, the organizer.

Finish with a short "Still open before this campaign can launch for real" list
naming anything I didn't provide or that still needs outside review. Never claim
this packet alone is a legal or ethical clearance to start collecting.
```

## What you'll get back

A single document with four parts, in this order:
1. An upfront warning paragraph naming anything still missing or unreviewed.
2. The consent & IP disclosure script (spoken and written versions).
3. The elicitation prompt set, organized by the five bands above.
4. The moderator review rubric table.
5. A closing "still open" checklist.

## What this will never do

- It will not claim the consent script is legally sufficient on its own — it always flags that a real legal/governance review is still needed.
- It will not invent a specific local custom, place name, or community-specific debate it wasn't told about.
- It will not draft a prompt that asks someone to read a fixed sentence aloud — every prompt calls for free, spontaneous speech.
- It will not skip the minors/vulnerable-speaker question — if you don't answer it, it will flag that as an open item rather than silently assuming no minors will contribute.
- It will not collect, store, or transmit any actual audio or contributor data — it only drafts text.
- It will not overwrite or ignore an existing consent process you already have — tell it what you already have and it will incorporate it rather than replace it.
