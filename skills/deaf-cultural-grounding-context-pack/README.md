# Deaf Cultural Grounding Context Pack

A paste-anywhere prompt for checking one specific AI chatbot response for hearing-centric assumptions and Deaf-cultural missteps before it goes out — and getting a rewritten version back. Works in any chat tool; no app, account, or installation needed.

## When to use this

You have **one concrete AI-generated response in hand** — a chatbot reply, a drafted email, a support script — and you want to know whether it assumes the reader can hear, uses deficit-framed language about deafness, or otherwise gets Deaf culture wrong, before it reaches (or stays in front of) a Deaf or hard-of-hearing (DHH) person. This is not a tool for live ASL interpretation and not a standing moderation system — it checks one piece of text at a time.

## What to hand over

Paste all of the following into the chat:

1. **The exact AI response you want checked** (required).
2. **The question or message that produced it** (required) — several of the checks below depend on knowing what was actually asked, e.g. whether a phone call was the user's own idea or something the bot suggested unprompted.
3. **Optional**: whether the intended reader is "general DHH" (default) or "ASL-primary" — this adds two extra checks about ASL being treated as a full independent language.

Everything here is pasted by you; nothing is looked up automatically. The 15-entry reference list below ships with this prompt — it is not pulled from any live source, because no mature, continuously updated "Deaf-cultural knowledge" API or database exists to connect to.

## What the reviewer does

Give the AI this instruction along with your three inputs above:

> Review the response below against the 15-entry Deaf-cultural grounding list that follows. For each entry, check whether the response contains language or an assumption matching it — judge only from exact words in the response, don't flag a general impression. For every match, give the entry ID, the exact quoted phrase, a one-line reason, and a one-line fix direction. Then write one full rewritten version of the response that resolves every flag while keeping the original's actual content and intent — don't add disclaimers or extra accessibility advice beyond what fixes a flagged issue. If nothing matches, say "No flags against this list" instead of inventing a minor nitpick. If something seems off but doesn't match any of the 15 entries, note it separately as a possible gap rather than stretching an entry to cover it.

### The 15-entry reference list

1. **Phone-call-as-default** — assumes a phone call is a neutral, easy next step ("just call them back") without checking whether the reader can place a voice call, or offering a text/video-relay/email alternative.
2. **Interpreting as afterthought** — treats an interpreter or captions as optional ("if one isn't available...") instead of a baseline requirement for the situation.
3. **Deficit/medical-model terms** — "hearing impaired," "suffers from deafness," "handicapped," instead of a person's own preferred term ("Deaf," "deaf," or "hard of hearing" — which one depends on the person).
4. **Flattens Deaf vs. deaf** — ignores the difference between "Deaf" (cultural identity, Deaf community, sign-language use) and "deaf" (audiological status only), treating all DHH people as one group.
5. **Dismissive sound idioms** — uses phrases like "fell on deaf ears" to mean "ignored," applied dismissively to a person being discussed. (A DHH person's own casual use of hearing idioms about themselves is not a flag.)
6. **English as "real" language** — treats written/spoken English as the DHH person's default language and sign language as a secondary accommodation layered on top.
7. **Lipreading as reliable fallback** — suggests lipreading/speechreading as a dependable substitute when an interpreter isn't available, rather than naming it as unreliable for most DHH people.
8. **Unprompted cure framing** — brings up hearing aids, cochlear implants, or "fixing" deafness when the person asked about something unrelated (a job interview, a bill, etc.).
9. **Family member as default interpreter** — suggests a hearing relative, friend, or coworker as the default communication go-between instead of a professional interpreter or a direct accessible channel.
10. **ASL as "simplified English"** — describes ASL as an incomplete or simplified version of English rather than its own full language with independent grammar.
11. **Interpreter called "translator"** — implies ASL interpretation is a literal word-for-word rendering rather than real-time meaning-for-meaning interpretation between two distinct languages.
12. **Captions as full substitute** — treats captions alone as equivalent to live interpretation in a high-stakes setting (medical, legal, interview, emergency).
13. **"Struggling" framing** — describes a DHH person's communication as "struggling" or "limited" rather than neutrally naming the language or modality in use.
14. **Monolithic "the Deaf community"** — assumes one shared opinion across all DHH people, ignoring regional, generational, or individual variation.
15. **Talking past the DHH person** — addresses a hearing third party about the DHH person ("tell your interpreter to ask them...") instead of addressing the DHH person directly when they're the one present.

### Output you should get back

```markdown
## Flags Found
| Entry | Quoted phrase | Why | Fix direction |
|-------|---------------|-----|----------------|
| # | "exact text" | one line | one line |

(or: "No flags against this list.")

## Possible Gap, Not in List
(only if something doesn't fit the 15 entries above)

## Rewritten Response
(the full corrected response, ready to send as-is)
```

## What this is not

This 15-entry list is a seed set for reviewing one response at a time — it is not a claim of a complete, community-validated Deaf-cultural corpus. A real community-governed version of this (built and corrected over time by Deaf contributors, with a proper evaluation harness) is a bigger, separate project. This prompt is the fast, one-shot version of that idea: good for catching the common, well-documented mistakes above, not a substitute for review by Deaf community members on anything high-stakes.

## Guardrails

- Don't flag a phrase without quoting the exact text — an unquoted flag can't be checked.
- Don't use an entry number for something that entry doesn't describe; use the "Possible Gap" section instead.
- Don't treat "Deaf" or "deaf" themselves as words to avoid — the problem is deficit framing and wrong assumptions, not the identity terms.
- Don't add extra hedges or accessibility advice beyond what's needed to fix a flagged line.
- Don't invent statistics, survey numbers, or named sources inside a "Why" explanation — ground it in the listed pattern, not a fabricated citation.
