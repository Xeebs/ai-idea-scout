# Legal-Aid Glossary-Grounded Translation Draft

A paste-and-go prompt for drafting a legal-aid translation that clearly flags any legal term not covered by your own verified glossary — instead of a generic machine-translation tool silently guessing at high-stakes terms like "eviction," "garnishment," or "ex parte."

## When to use this

Use this when you (a legal-aid staff member, a volunteer or community interpreter, or a developer building a multilingual legal-aid chatbot) have a piece of legal-aid text — an intake question, a notice, a short explainer, a form field — and need a first-pass translation into another language, with full visibility into which legal terms are backed by a glossary you trust and which ones still need a human to check.

Don't use this for: translating case law or statutes for legal research (that needs certified translation, not a drafting aid); producing a final translation to hand a client without interpreter review (this never replaces that step); or plain text with no legal terminology in it (you don't need a glossary gate for that).

## What you need to provide

**Data source: Manual.** You paste everything yourself — there is no connected database behind this prompt. In particular:

1. **Source text** — the exact text to translate.
2. **Target language** — what you're translating into.
3. **Your glossary** — your own list of verified legal term-pairs. Format each entry as: English term, translation, jurisdiction (if known), practice area (if known), and an example sentence showing it in context. It's fine if this list is short, partial, or something you jot down on the spot — a small real glossary is still worth more than none. If you genuinely have no glossary yet, say so; the prompt will still run, but every legal term in the output gets flagged as unverified instead of silently trusted.
4. **Optional**: the jurisdiction and practice area of the document overall (e.g., "California housing law," "federal immigration"), so a glossary entry can be checked for context match, not just a term-name match.

## The prompt

Paste this into any AI chat tool, filling in the four items above:

```
You are drafting a legal-aid translation. Follow this procedure exactly:

SOURCE TEXT: <paste the text to translate>
TARGET LANGUAGE: <language>
DOCUMENT JURISDICTION/PRACTICE AREA (optional): <e.g., California housing law>
GLOSSARY:
<paste your term-pairs, one per line, as: English term | translation | jurisdiction | practice area | example sentence>
<or write "NO GLOSSARY PROVIDED" if you have none>

Steps:
1. Scan the source text and list every term carrying precise legal meaning in a
   legal-aid context (e.g., eviction, garnishment, lease, ex parte, continuance,
   exemption, standing, custody, specific benefits or immigration-status terms) —
   as distinct from ordinary vocabulary that needs no special handling.
2. For each term found, check it against the glossary I provided:
   - If there's a matching entry AND its jurisdiction/practice area matches
     (or none was specified), use that translation. Mark it [GLOSSARY].
   - If there's a matching entry but the jurisdiction/practice area conflicts
     with what I told you about this document, mark it [JURISDICTION MISMATCH]
     and treat it as a candidate only, not confirmed.
   - If there's no matching entry at all, give your best translation but mark
     it [UNVERIFIED]. Never treat an unverified term with the same confidence
     as a glossary match.
3. Translate the full source text, inserting the inline markers next to each
   flagged term directly in the translated draft.
4. Produce the output in exactly this structure:

# Draft Translation — <source language> → <target language>

## Translated Draft
<the translated text with inline [GLOSSARY] / [UNVERIFIED] / [JURISDICTION MISMATCH] markers>

## Glossary-Backed Terms (<count>)
- "<English term>" → "<translation>" — jurisdiction: <x>, practice area: <y>

## Needs Verification (<count>)
- "<English term>" → "<best-effort translation>" [UNVERIFIED — no glossary entry found]
  Why it matters: <one line on what's risky if this is wrong>
- "<English term>" → "<candidate>" [JURISDICTION MISMATCH — glossary entry was for <other context>]

## Glossary Coverage
<n> of <total> legal terms were glossary-backed. <n> had no coverage at all.

## Verification & Contribution Note
This is a first-pass draft only. Every UNVERIFIED or JURISDICTION MISMATCH term
must be checked by a certified or community interpreter before this is used
with a client. If you confirm a flagged term, consider adding it to your
glossary (with jurisdiction and practice area) so you don't have to re-verify
it next time.

Rules you must follow:
- Never mark a term [GLOSSARY] unless I actually gave you a matching entry this
  session. Your own fluency in the target language is not a substitute for a
  glossary entry I provided.
- Never resolve a jurisdiction/practice-area mismatch in the glossary's favor —
  always flag it instead of assuming the term transfers.
- Never present this as a client-ready or certified translation. Always include
  the Verification & Contribution Note, even if nothing was flagged.
- Never invent glossary entries I didn't paste, even if I mention "our glossary"
  without pasting it — ask me for it instead.
- If I provided no glossary at all, say so clearly before the draft, not buried
  at the bottom.
```

## What you get back

A translated draft with inline flags showing exactly which legal terms came from your verified glossary and which ones still need a human (ideally a certified or community interpreter) to check before the translation goes anywhere near a client — plus a short coverage summary so you can see at a glance how much of the document was actually glossary-backed.

## What this is not

This is not a certified or sworn translation, not a substitute for interpreter review, and not a tool for translating case law or statutory text for legal research. It is a drafting aid that makes the boundary between "verified" and "guessed" visible, so nobody mistakes a flagged guess for a checked term.
