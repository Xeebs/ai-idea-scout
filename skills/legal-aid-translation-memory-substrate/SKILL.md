---
name: legal-aid-translation-memory-substrate
description: Drafts a legal-aid translation of a phrase or short document into a target language using a glossary of verified term-pairs the user supplies, explicitly flagging any legal term not covered by that glossary instead of silently guessing. Use when a legal-aid staff member, volunteer/community interpreter, or a developer building a multilingual legal-aid chatbot needs a first-pass translation draft with clear visibility into which legal terms are glossary-backed and which still need human verification — not for case-law translation or certified/sworn translation output.
---

# Legal-Aid Glossary-Grounded Translation Draft

## When to use this
A legal-aid staff member, volunteer or community interpreter, or a developer building/maintaining a multilingual legal-aid chatbot has a piece of legal-aid-relevant text (an intake question, a notice, a short explainer paragraph, a form field) and needs a draft translation into a target language — but wants legal terms with precise, high-stakes meaning (eviction, garnishment, ex parte, lease, standing, continuance, exemption, etc.) handled against a known-good glossary rather than flattened by generic machine translation. Reach for this skill at the point of drafting that translation, before it goes anywhere near a client.

Do not use this for: translating case law or statutory text for legal research (a different, higher-stakes task requiring certified translation); producing a final, client-ready translation without human interpreter sign-off (this skill never claims to replace that review); or any translation where no legal-aid-specific terminology is actually present (plain general-language translation needs no glossary gate).

## Inputs
**Data source**: Manual — the user pastes (a) the source text to translate, (b) the target language, and (c) their own glossary of verified legal-aid term-pairs (term, translation, jurisdiction, practice area, example sentence) as plain text or a simple table. There is no connected glossary API today — the shared, queryable translation-memory substrate this skill is designed to eventually draw from is itself unbuilt (per the parent idea, OPEN as of 2026-11-17); until it exists, this skill works entirely from whatever glossary the user has on hand, even if that glossary is small, partial, or improvised for the session.

Required:
1. **Source text** — the phrase, sentence, or short document to translate, pasted in full.
2. **Target language** — the language to translate into.
3. **Glossary** — the user's verified term-pairs, each ideally with: English term, target-language term, jurisdiction (if known), practice area (if known), and an example sentence showing the term in context. If the user has zero glossary entries, proceed anyway but say explicitly up front that every legal term in the output will be flagged as unverified — never silently fall back to treating general MT knowledge as glossary-verified.

Optional:
4. **Jurisdiction / practice area** for the document as a whole, used to check whether a glossary entry that matches the term also matches the right jurisdiction/practice-area context (a term verified for one jurisdiction's housing law is not automatically valid for another jurisdiction or a different practice area).

## Procedure
1. **Identify legal-aid-specific terms in the source text.** Scan for words/phrases carrying precise legal meaning in a legal-aid context (eviction, garnishment, lease, ex parte, continuance, exemption, standing, custody, benefits categories, immigration status terms, etc.) as distinct from general vocabulary that any MT system handles fine. List each one found, in order of appearance.
2. **Check each identified term against the pasted glossary.** For each term:
   - **Glossary match, jurisdiction/practice-area aligned (or none specified)** → use the glossary's provided translation and example sentence as the basis for that span of the draft. Mark it `[GLOSSARY]`.
   - **Glossary match, but jurisdiction or practice area tag conflicts with the document's stated context** → do not treat as verified. Mark it `[JURISDICTION MISMATCH]` and use it only as a candidate, not a confirmed translation.
   - **No glossary match at all** → produce a best-effort translation using general language knowledge, but mark it `[UNVERIFIED]`. Never present an unverified term's translation with the same confidence as a glossary match.
3. **Translate the full source text**, substituting glossary-backed terms where found and best-effort terms elsewhere, preserving the original sentence structure and register as closely as the target language allows.
4. **Produce the flagged-terms list** (see Output format) separating glossary-backed terms from unverified and jurisdiction-mismatched ones, so a reviewer can scan exactly what needs checking without re-reading the whole draft.
5. **Never upgrade an unverified or mismatched term to glossary-backed status based on general confidence** — if it wasn't in the pasted glossary with a matching jurisdiction/practice area, it stays flagged, no matter how certain the translation seems.
6. **Close with the verification and contribution note** (see Output format) — every output ends with the same reminder, not just when terms were flagged.

## Output format
```
# Draft Translation — <source language> → <target language>

## Translated Draft
<full translated text, with inline markers next to each flagged term, e.g.:
"...will receive a notice of eviction [GLOSSARY] before any garnishment [UNVERIFIED] of wages can begin...">

## Glossary-Backed Terms (<n>)
- "<English term>" → "<target-language term>" — jurisdiction: <x>, practice area: <y>
  (source: glossary entry provided)

## Needs Verification (<n>)
- "<English term>" → "<best-effort translation>" [UNVERIFIED — no glossary entry found]
  Why it matters: <one line on why this term's precise meaning affects the client's situation>
- "<English term>" → "<candidate translation>" [JURISDICTION MISMATCH — glossary entry found for <other jurisdiction/practice area>, not <this document's context>]

## Glossary Coverage
<n> of <total> legal terms identified were glossary-backed. <n> had no glossary coverage at all.

## Verification & Contribution Note
This is a first-pass draft only. Every term marked UNVERIFIED or JURISDICTION MISMATCH must be checked by a certified or community interpreter before this translation is used with a client. If a flagged term's translation is confirmed correct, consider adding it (with jurisdiction and practice area) to your glossary — and if you're part of a legal-aid chatbot project, to the shared legal-aid translation-memory substrate once one exists, so other teams don't have to re-verify the same term from scratch.
```

## Guardrails
- Never mark a term `[GLOSSARY]` unless it has an actual matching entry in the glossary text the user pasted this session — training-data fluency in the target language is not a substitute for a verified glossary entry.
- Never silently resolve a jurisdiction or practice-area mismatch in the glossary's favor — a term verified for one jurisdiction's family law is not automatically correct for another jurisdiction or a different practice area (housing vs. immigration vs. benefits); always flag the mismatch rather than assume it transfers.
- Never present this output as a client-ready or certified translation — it is explicitly a drafting aid for a human reviewer, and the closing verification note must appear on every single output, not only when something was flagged.
- Never fabricate glossary entries or cite a glossary source the user didn't actually paste — if the user references "our glossary" without pasting it, ask for it rather than proceeding on assumed content.
- Never use this for case-law or statutory-text translation, or anywhere a certified/sworn translator is legally required — redirect the user to that requirement instead of producing a draft that could be mistaken for satisfying it.
- If zero glossary entries are provided, say so explicitly before the draft, not buried at the bottom — a reviewer scanning only the top of the output must immediately know nothing here is glossary-verified.
