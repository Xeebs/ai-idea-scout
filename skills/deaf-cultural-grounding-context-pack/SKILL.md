---
name: deaf-cultural-grounding-context-pack
description: Reviews a specific LLM response (plus the message it answered) for hearing-centric assumptions and Deaf-cultural missteps, citing each flag against a named corpus entry, and produces a rewritten version. Use when a DHH user, a product team, or a researcher has one concrete chatbot/LLM response they're unsure is Deaf-culturally appropriate.
---

# Deaf Cultural Grounding Context Pack

## When to use this
The exact trigger moment: someone has a **specific LLM response already in hand** — a chatbot reply, a drafted email, a support-bot script — and wants to know whether it embeds hearing-centric assumptions or gets Deaf culture wrong before it reaches (or stays in front of) a DHH user. This is a one-shot review/rewrite task, not a standing moderation pipeline and not an ASL-video tool — it only reviews text.

Reach for this skill when someone says things like "is this response okay to send to a Deaf user", "can you check this bot reply for Deaf-cultural issues", or "rewrite this so it doesn't assume the person can hear."

## Inputs
**Data source**: Manual — the user pastes the exact LLM response to be reviewed (required), the preceding user message/question that produced it (required, for context), and optionally a target-audience flag: `general DHH` (default) or `ASL-primary`. Nothing is fetched from any API or connector — the grounding corpus below ships bundled with this skill file, not pulled live, because no mature "Deaf-cultural knowledge" data source exists to connect to.

## Procedure

1. **Confirm you have both required inputs.** If the preceding user message is missing, ask for it before flagging anything — several corpus entries below depend on knowing what was actually asked (e.g. whether a phone call was the user's own idea or the bot's suggestion).
2. **Read the response against every entry in the Grounding Corpus (v1, 15 entries)** below. For each entry, decide: does the response contain language or an assumption this entry describes? Judge from the actual words in the response, not from a general impression — if you can't point to a specific phrase, it isn't a flag.
3. **For every match**, record: the entry ID, the exact quoted phrase from the response, a one-line explanation of the hearing-centric assumption or cultural misstep, and a fix direction.
4. **If the target audience is `ASL-primary`**, additionally check: does the response treat ASL as a word-for-word re-encoding of English rather than its own language with independent grammar (entry C11), and does it assume English literacy is an acceptable substitute for interpretation (related to C7)?
5. **Produce one rewritten version** of the full response that resolves every flag found while preserving the original's actual information content and intent. Don't pad the rewrite with disclaimers the user didn't ask for.
6. **If zero entries match**, say so explicitly — "No flags against corpus v1" — rather than inventing a minor stylistic nit to look thorough.
7. **If you notice something that reads off but doesn't map to any of the 15 entries**, report it separately under "Possible gap, not in corpus v1" — never fold an ad hoc judgment into the numbered flag list as if it were a sourced corpus entry.

## Grounding Corpus (v1 — 15 entries)

| ID | Pattern |
|----|---------|
| C1 | Assumes a phone call is a neutral/easy next step ("just call them back") without first checking whether the user can place a voice call, or offering a text/video-relay/email alternative. |
| C2 | Treats interpreting or captioning as an optional afterthought ("if an interpreter isn't available...") rather than a baseline requirement for the situation described. |
| C3 | Uses deficit/medical-model terms — "hearing impaired," "suffers from deafness," "handicapped" — instead of the person's own preferred term (commonly "Deaf," "deaf," or "hard of hearing"; which one depends on the person, not the skill). |
| C4 | Flattens the capital-D/lowercase-d distinction — "Deaf" (cultural identity, Deaf community, ASL use) vs. "deaf" (audiological status only) — treating all DHH people as the same group. |
| C5 | Uses sound-based idioms dismissively against the person being discussed (e.g. "fell on deaf ears" to mean "ignored") rather than neutrally; note this is distinct from a DHH person's own casual use of hearing-idioms, which is not a flag. |
| C6 | Frames English (written or spoken) as the DHH person's "real" or default language and ASL/sign as a secondary accommodation layered on top of it. |
| C7 | Positions lipreading or speechreading as a reliable universal fallback when an interpreter isn't available, rather than naming it as unreliable for most DHH people and context-dependent at best. |
| C8 | Uses cure/fix framing — suggesting hearing aids, cochlear implants, or "solutions" to deafness unprompted, when the user asked about something unrelated (e.g. a job interview, a bill). |
| C9 | Suggests a hearing family member, friend, or coworker as the default communication intermediary instead of a professional interpreter or a direct accessible channel. |
| C10 | Describes ASL as a simplified or incomplete version of English rather than a full independent language with its own grammar, syntax, and regional variation. |
| C11 | Calls an ASL interpreter a "translator" or implies interpretation is a literal word-for-word rendering, rather than real-time meaning-for-meaning interpretation between two distinct languages. |
| C12 | Treats captions alone as a full substitute for live interpretation in a high-stakes setting (medical, legal, interview, emergency) rather than naming captions and interpretation as serving different needs. |
| C13 | Describes a DHH person's or group's communication as "struggling" or "limited" rather than neutrally describing the language/modality being used. |
| C14 | Treats "the Deaf community" as a single monolithic group with one shared opinion, ignoring regional, generational, or individual variation that the response itself has no basis to assume away. |
| C15 | Addresses a hearing third party about the DHH person ("tell your interpreter to ask them...") instead of addressing the DHH person directly when they are the one present and being spoken to. |

## Output format

```markdown
## Flags Found
| Entry | Quoted phrase | Why | Fix direction |
|-------|---------------|-----|----------------|
| C# | "<exact text>" | <one line> | <one line> |

(If none: "No flags against corpus v1.")

## Possible Gap, Not in Corpus v1
(Omit this section entirely if nothing applies — do not force an entry.)

## Rewritten Response
<the full rewritten text, ready to send as-is>
```

## Guardrails
- Never flag a phrase without quoting the exact text from the response — a flag without a quote is not checkable.
- Never cite a corpus entry number for something that entry doesn't actually describe; if nothing fits, use the "Possible Gap" section instead of stretching an entry.
- Never treat "Deaf" or "deaf" as a word to avoid or soften — the problem is deficit framing and wrong assumptions, not the identity term itself.
- Never add disclaimers, hedges, or extra accessibility advice beyond what's needed to fix a flagged issue — the rewrite should read like a normal, good response, not a corrected-essay.
- Never present this 15-entry pack as the full, community-validated corpus described in the parent idea — it's a seed set for the skill's one-shot review task; the standing, continuously-maintained, community-governed corpus and eval harness are the separate project, not this skill.
- Never invent engagement numbers, survey statistics, or named sources inside a flag's "Why" explanation — ground each explanation in the corpus entry's own description, not a fabricated citation.
