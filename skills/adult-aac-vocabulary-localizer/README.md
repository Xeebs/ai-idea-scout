# Adult AAC Vocabulary Localizer

A prompt template for speech-language pathologists (SLPs), caregivers, and special-needs educators who have an adult client who is non-verbal or minimally verbal, and whose language and/or life stage falls outside what mainstream AAC (augmentative and alternative communication) apps ship with.

## The problem this solves

Mainstream AAC apps (Proloquo2Go, Avaz, and similar tools) build their vocabulary around a child's world — school, playtime, family roles — and, where they're translated at all, cover mainstream languages like Spanish, French, Dutch, and the Nordic languages. An adult who loses speech later in life (stroke, ALS, epilepsy-related cognitive change, traumatic injury) and speaks a language outside that mainstream set has no vocabulary board that matches either their life stage or their language. Today a clinician facing this either hand-adapts a kids' app word by word (slow, and still child-register when done) or gives up and relies on generic pointing/gestures. This prompt turns that multi-week manual adaptation into a reviewable first draft you can produce in one session.

**This is not a replacement for clinical judgment.** It produces a draft vocabulary set that still needs native-speaker and clinical review before anyone relies on it to communicate.

## How to use this

Copy the prompt below into any AI chat tool (Claude, ChatGPT, etc.) and fill in the bracketed details about your client. Paste an existing vocabulary export or word list too if you have one you want adapted rather than starting from zero.

---

### Prompt template

```
You are helping me build an adult-register AAC (augmentative and alternative
communication) vocabulary set, localized into a specific language, for a
client who is non-verbal or minimally verbal. Mainstream AAC apps default to
pediatric vocabulary (school, playtime, toys) and mainstream languages
(English/Spanish/French/Dutch/Nordic) — I need something that actually fits
an adult's life in a different language. Here is the client profile:

- Target language / dialect: [e.g. "Brazilian Portuguese" — be specific about
  regional variant if it matters]
- Communication/literacy profile: [current communication method — gestures,
  pointing, partial speech, existing device; literacy level — can they read
  text labels or do they need symbol-only; any motor/scanning constraints,
  e.g. needs large touch targets or uses eye-gaze/switch scanning]
- Life context: [occupation/daily activities, living situation, and the
  specific domains where communication matters most — work, healthcare
  visits, errands, relationships/family, hobbies, self-advocacy/emergencies.
  Be concrete — this determines the whole vocabulary set, so don't just say
  "daily life."]
- (Optional) Existing vocabulary to adapt: [paste a word list or an exported
  board's contents here if you have one, instead of starting fresh]
- (Optional) Register/cultural notes: [formality norms, regional
  slang to include/avoid, culturally relevant phrases]

Please:

1. Build a context inventory from my stated life context above — do not
   substitute generic pediatric categories (school, playtime, toys) unless I
   explicitly described a child.
2. Draft a vocabulary set in two parts:
   - Core vocabulary: high-frequency function words every AAC user needs
     (yes/no, pronouns, "I want," "I need," "help," "stop," "more," "wait,"
     basic emotions, pain/discomfort reporting for medical safety) in
     adult-register phrasing matched to my stated literacy level.
   - Context vocabulary: specific nouns, verbs, and short phrases for each
     domain in my context inventory.
3. Translate and culturally adapt every item for an adult native speaker of
   the target language — never give me a word-for-word machine translation
   of an English pediatric original. Where a term is genuinely ambiguous
   (idiom, regionalism, no clean one-to-one equivalent), mark it
   CONFIDENCE: LOW with a one-line note on the ambiguity instead of silently
   picking an answer.
4. If I gave you an existing vocabulary/export to adapt: keep what's already
   adult-appropriate, flag and replace anything child-coded given my stated
   context, and add the missing domain vocabulary — tell me explicitly what
   you kept, changed, and added. Don't discard it and start over.
5. For every vocabulary item, suggest a symbol search term (e.g. "medication
   — search term: 'pills/medicine bottle'") instead of claiming to generate
   an actual symbol image — you have no access to any specific AAC app's
   real symbol library, so never claim otherwise.
6. Generate an Open Board Format (OBF) 0.1 JSON export — one board per
   domain category plus a core-vocabulary board — so I can import this
   directly into an OBF-compatible app like CoughDrop. Size the grid
   (items per board) to my stated literacy/motor profile: fewer, larger
   buttons for lower literacy or motor-constrained scanning.
7. Give me a review checklist listing every CONFIDENCE: LOW item and every
   item carried over from a child-coded original, with an explicit note
   that nothing here is validated for live use until a native-speaker
   clinician or fluent family member reviews it.

Format your answer as:

## Client Profile Captured
(restate what you understood, and flag anything you had to default because
I didn't specify it)

## Vocabulary Set
### Core Vocabulary
Table: English gloss | Target-language term/phrase | Register note |
Confidence | Suggested symbol search term

### [Domain Category] (one table per domain from my context inventory)

## Open Board Format Export
(valid OBF 0.1 JSON, ready to import)

## Review Checklist (required before any live use)
- Every CONFIDENCE: LOW item, listed with its ambiguity noted
- Every item carried over from a child-coded original
- STATUS: DRAFT — NOT VALIDATED FOR CLIENT USE

## Next Steps
(what I should do next — native-speaker review, import test, client trial)

Do not mark this set "final," "validated," or "ready to use" anywhere — it
is always a draft pending clinical/native-speaker review. Do not default to
pediatric categories unless I described a child. Do not invent clinical
details about my client beyond what I told you.
```

---

## What good output looks like

- A profile summary that reflects exactly what you described — not a generic template with your language name swapped in.
- A vocabulary set organized by domains you actually named (your client's workplace, their specific healthcare context, etc.), not school/playtime categories.
- Translations that read like something an adult native speaker would actually say, with low-confidence items explicitly flagged rather than silently guessed.
- A valid, importable OBF JSON block you can drop into CoughDrop or another OBF-compatible app.
- A review checklist and an explicit "DRAFT — NOT VALIDATED" status, every time, with no exceptions.

## What this does not do

- It does not replace a licensed SLP's clinical judgment — it produces a first draft for one.
- It does not generate actual symbol graphics or know what's in your specific app's symbol library — only search-term suggestions.
- It does not connect to any AAC app, translation API, or clinical record system — everything here is typed/pasted in and typed/pasted out.
- It is a one-shot generator for one client/language at a time, not a persistent, shared, versioned library across clinicians — if you want that, you need a place (even a shared folder or repo) to store and reuse validated sets across cases.
