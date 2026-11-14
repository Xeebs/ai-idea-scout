---
name: adult-aac-vocabulary-localizer
description: Generates an adult-register, culturally-adapted AAC (augmentative and alternative communication) vocabulary set in a target language, exported in Open Board Format, for a non-verbal or minimally-verbal adult — for speech-language pathologists, caregivers, and special-needs educators who have a client whose language and life stage mainstream pediatric-first AAC apps don't cover.
---

# Adult AAC Vocabulary Localizer

## When to use this

Use this the moment a speech-language pathologist (SLP), caregiver, or special-needs educator says something shaped like: "I need an AAC vocabulary set for an adult client in [language]," "our AAC app only has kids' vocabulary and my client is an adult," "I need to translate/adapt a vocabulary board for a [language]-speaking adult who can't speak," or "I have an adult client who lost speech after a stroke/ALS/injury and I can't find vocabulary that fits their life." This is specifically for the **adult-register, non-mainstream-language** gap — mainstream AAC apps (Proloquo2Go, Avaz, etc.) already cover English/Spanish/French/Dutch/Nordic pediatric vocabulary well; reach for this skill when either the language or the life-stage (or both) falls outside that existing coverage. It is a one-shot generation/adaptation task per client-language pair, not a persistent app — run it again whenever a new client or language needs a set.

## Inputs

**Data source**: Manual — the user describes the client's profile and context in text, and optionally pastes an existing AAC vocabulary export (an Open Board Format JSON file's contents, or a plain word list) to adapt rather than start from scratch. This skill does not connect to any AAC app, translation API, or clinical record system — nothing is read automatically from CoughDrop, Proloquo2Go, or an EHR. If a future version adds a live CoughDrop API pull/push, that is a distinct upgrade, not something this skill does today.

Ask for, if not already given:
1. **Target language** — including dialect/regional variant if it matters (e.g. Brazilian vs. European Portuguese, Kinyarwanda vs. a neighboring Bantu language the user might conflate it with).
2. **Communication/literacy profile** — current communication method (gestures, pointing, partial speech, existing device), literacy level (can the person read text labels, or do they need symbol-only), and any relevant motor/scanning constraints that affect board layout (e.g. needs large touch targets, uses eye-gaze/switch scanning).
3. **Life context** — occupation or daily activities, living situation (independent, with family, residential care), and the specific domains where communication matters most (work, healthcare visits, errands/shopping, relationships/family, hobbies, self-advocacy/emergencies). This is the input that determines the vocabulary categories — never assume a default pediatric set (school, playtime, toys) unless the user's own context says the person is a child.
4. *(Optional)* **An existing vocabulary export to adapt** — pasted OBF JSON, or a plain word/phrase list from a current app or board. If supplied, the skill adapts and extends it rather than generating a fresh set from zero.
5. *(Optional)* **Known register/cultural notes** — e.g. formality norms in the target language/culture, regional slang to avoid or include, religious/cultural phrases relevant to the person's life.

If (1) or (3) is missing, ask directly before generating anything — a vocabulary set built without knowing the language or life context is worthless. If (2) is missing, proceed but default to assuming text+symbol labels and flag that assumption explicitly in the output.

## Procedure

1. **Build a context inventory** from input (3): list the specific domains and situations where this adult needs to communicate, drawn from their actual stated life (e.g. "technical college classroom and workshop," "dialysis clinic visits," "grocery errands with a home aide") — never substitute generic pediatric categories (playtime, toys, school subjects) unless the stated context is genuinely a child's.
2. **Draft the vocabulary**, organized into:
   - **Core vocabulary** — high-frequency function words and phrases every AAC user needs regardless of context (yes/no, pronouns, "I want," "I need," "help," "stop," "more," "wait," basic emotions, pain/discomfort reporting for medical safety) — adult-register phrasing, not childlike ("I need assistance" register options alongside simpler forms, matching the stated literacy level).
   - **Fringe/context vocabulary** — specific nouns, verbs, and short phrases for each domain identified in step 1 (e.g. for a technical-college context: tool names, "I don't understand the instructions," "may I take a break," workplace-appropriate self-advocacy phrases).
3. **Translate and culturally adapt — never word-for-word machine-translate.** For each item: produce the target-language term/phrase a native adult speaker in that register would actually use, not a literal gloss of the English pediatric-app original. Where a direct equivalent is uncertain (idiom, regionalism, a concept without a clean one-to-one translation), mark it `CONFIDENCE: LOW` and add a one-line note on the ambiguity rather than silently picking one option.
4. **If an existing export was supplied (input 4)**: map its current buttons/words, keep anything already adult-appropriate and correctly registered, flag and replace anything that reads as child-coded (e.g. "playtime," cartoonish phrasing) given the stated adult context, and add the missing domain vocabulary from step 2 rather than discarding the whole set.
5. **Attach a suggested symbol search term** to every item (e.g. "medication — search term: 'pills/medicine bottle'") instead of inventing or claiming to generate actual symbol graphics — this skill has no access to any specific AAC app's real symbol library (SymbolStix, Mulberry, etc.), so it never claims the output already has matched images.
6. **Generate the Open Board Format (OBF) export** — valid OBF 0.1 JSON with one board per domain category plus a core-vocabulary board, buttons keyed to the translated terms, and a grid layout sized to the stated literacy/motor profile (larger grid with fewer items per board for lower literacy or motor-constrained scanning; denser grid for higher literacy).
7. **Compile a review checklist** — every `CONFIDENCE: LOW` item, every item adapted from a child-coded original, and a top-line instruction that nothing in this set is validated for live use until a native-speaker clinician/SLP reviews it.

## Output format

```
## Client Profile Captured
- Target language/dialect:
- Communication/literacy profile: (note if defaulted)
- Life context domains: (list drawn from stated context, not a default template)
- Existing export adapted: yes/no

## Vocabulary Set

### Core Vocabulary
| English gloss | Target-language term/phrase | Register note | Confidence | Suggested symbol search term |
|---|---|---|---|---|

### [Domain Category Name] (repeat per domain)
| English gloss | Target-language term/phrase | Register note | Confidence | Suggested symbol search term |
|---|---|---|---|---|

## Open Board Format Export
```json
<valid OBF 0.1 JSON, one object per board, importable into CoughDrop or any OBF-compatible AAC app>
```

## Review Checklist (required before any live use)
- [ ] Every CONFIDENCE: LOW item below confirmed by a native-speaker clinician or fluent family member
- [ ] <list of specific flagged items with the ambiguity noted>
- [ ] Any item carried over from a child-coded original source, re-confirmed as adult-appropriate
- STATUS: DRAFT — NOT VALIDATED FOR CLIENT USE

## Next Steps
- What the clinician does next (native-speaker review, import test into their actual AAC app, trial with the client and note which items get used vs. ignored).
```

## Guardrails

- Never mark a generated set "validated," "final," or "ready to use" — every output ends with an explicit `STATUS: DRAFT — NOT VALIDATED FOR CLIENT USE` and a review checklist. An unreviewed hallucinated phrase in someone's only communication tool is a serious failure, not a cosmetic one.
- Never produce word-for-word machine translation of an English pediatric vocabulary set — every item must be register- and culturally-adapted for an adult in the target language, and genuine translation ambiguity must be flagged with `CONFIDENCE: LOW`, never silently resolved by guessing.
- Never default to pediatric categories (school, playtime, toys, cartoon characters) unless the user's own stated context describes a child — the entire point of this skill is to not reproduce that default.
- Never claim to generate actual symbol graphics or to have matched a specific app's real symbol library — only ever suggest a search term for the clinician to match in their own app's library.
- Never invent or infer clinical details (diagnosis specifics, prognosis, cognitive capacity) beyond what the user explicitly states — if the user's profile is thin on this, generate vocabulary from what's given and note the gap, don't fabricate a clinical picture to fill it in.
- Never retain or request more personal identifying information than needed for the vocabulary task (no full legal names, addresses, medical record numbers) — ask for role/context, not identity.
- Never discard an existing supplied export wholesale — adapt and extend it, and explicitly list what was kept vs. changed vs. added.
