# Testimony Guard: A Legal-Risk Ambiguity Verification Layer for Asylum Translation

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-18-applied-ai-for-underserved-domains.md · P4
- **Maturity verdict**: OPEN — multi-channel search (GitHub, web, Techdirt/Lowy Institute/Context.news/Respond Crisis Translation's own 2025 LLM test) found only reporting on the failure mode and the current non-AI mitigation ("use volunteer human translators instead"); no tool, product, or research prototype flagging translation-ambiguity confidence specifically for legal/asylum testimony was found anywhere.
- **Format**: BOTH
- **Data Sources**: MANUAL — the user pastes the original-language testimony transcript (or audio-derived transcript) and the machine-translated output currently being prepared for submission. CONNECTED is not viable today: asylum case files live in whatever legal-aid CMS or government contractor system each org uses, with no shared or mature API across them, so this starts MANUAL by necessity rather than by default.

## The Gap
Techdirt and Context.news both document a case where automated translation flipped "I" to "we" in a Pashto-speaking asylum seeker's statement, creating an apparent inconsistency with her interview testimony that contributed to her case being rejected. Respond Crisis Translation notes government contractors are increasingly substituting AI machine translation for human translators on cost grounds anyway. The only current mitigation documented anywhere is avoiding AI translation entirely in favor of trained human translators (Respond Crisis Translation's own model) — OpenAI's usage policy now explicitly bars its models from migration/asylum decision-making, which is itself evidence no compliant AI-side fix exists yet.

## The Project
A verification layer that runs after machine translation but before submission: it re-translates the MT output back to the source language (round-trip check), flags specific linguistic structures with known legal-risk profiles (pronoun number/person shifts, verb tense changes that imply different timelines, idiom-to-literal substitutions, honorific/formality collapses that can read as evasiveness), and produces a structured risk report a human reviewer can act on before a translated statement becomes part of a legal record — explicitly not a pass/fail gate, since no model should autonomously clear legal testimony, but a triage tool that tells an overloaded legal-aid translator exactly where to spend their limited review time.

## Tangible Impact
**Population**: The roughly 2.28 million people with asylum applications currently pending in U.S. immigration courts, plus another 1 million+ pending at USCIS (TRAC, Syracuse University, August 2026 data) — a substantial share of whom testify in a language other than English and depend on machine or human translation of that testimony.
**Mechanism**: Today, a translation error that creates an apparent inconsistency between a written statement and prior interview testimony can be read by an adjudicator as evidence of dishonesty, directly harming case outcomes — exactly what happened in the documented Pashto "I"/"we" case. A pre-submission ambiguity flag lets a translator or legal-aid reviewer catch and correct that error before it ever reaches a judge, instead of after a denial.
**Measure**: Recall on a labeled test set of known translation-ambiguity failure types (built from documented cases like the Pashto example) vs. an unflagged MT baseline; reviewer time spent per document when triaged by risk flags vs. full manual re-translation; case-outcome correlation (a longer-horizon metric: do flagged-and-corrected cases show fewer "inconsistency" denials than a historical baseline).

## Why Now
Respond Crisis Translation's own 2025 test of Arabic/Farsi/Pashto/Kurdish LLM translation and the Pashto case documentation give concrete, recent failure examples to build a labeled eval set from, and the same frontier models now capable of fluent translation are also capable of structured round-trip/ambiguity-detection analysis — the underlying capability exists, it has simply never been pointed at this specific legal-risk task.

## Skill Angle
The skill is the entire MVP: given a pasted source-language transcript and its machine translation, it runs a round-trip back-translation, flags pronoun/tense/idiom discrepancies between the round-trip and the original, and outputs a structured risk report (location in text, discrepancy type, suggested correction, confidence) for a human reviewer — never auto-correcting the submitted document itself.

## MVP Sketch
A single-invocation pipeline: source text + MT output in, structured risk report out. Built from a labeled test set of ~20-30 known/constructed ambiguity cases (pronoun shifts, tense shifts, idiom literalization) validated with a trauma-informed translator familiar with asylum casework, run through round-trip translation plus a targeted comparison prompt. The single experiment: does the flagged-risk-type recall on the labeled set beat a naive "just re-read it" baseline reviewer time, measured with one partner legal-aid or crisis-translation org.
## Risks & Open Questions
- This sits adjacent to active legal/regulatory risk (OpenAI's own policy bars AI from asylum decisions) — the tool must be scoped unambiguously as reviewer-assistive, never decision-making, and that framing needs legal sign-off before any real deployment.
- A tool that flags "ambiguity" could itself be weaponized by an adjudicator or opposing counsel if its existence or outputs become discoverable — governance of who sees flagged reports needs design.
- False negatives (a real ambiguity the tool misses) are the dangerous failure mode, not false positives — the eval bar should weight recall heavily over precision.
- Building a labeled eval set requires access to real or realistic case examples, which is sensitive data; starting from public documented cases (like the Pashto example) and synthetic constructed cases may be the only ethical path for an MVP.
