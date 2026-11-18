---
name: asylum-testimony-translation-ambiguity-verifier
description: Round-trip-checks a machine-translated asylum/immigration testimony against its source-language original and flags pronoun, tense, idiom, and formality shifts that could read as an inconsistency to an adjudicator. Use before a translated statement is submitted as part of a legal record — never to clear or auto-correct it.
---

# Testimony Guard: Translation Ambiguity Verifier

## When to use this
Someone has a machine-translated (or MT-assisted) statement, declaration, or interview transcript headed into an asylum, immigration, or other legal proceeding, and wants it checked for translation artifacts that could be misread as a factual inconsistency (a changed pronoun, a shifted timeline, a flattened idiom) before it is filed or relied on. The trigger is pre-submission review, not post-denial autopsy — the whole point is catching it before a judge ever sees it. This is a triage aid for a human translator or legal-aid reviewer, not a translation tool and not a clearance tool.

## Inputs
**Data source**: Manual — the user pastes (1) the original-language testimony/transcript text, and (2) the machine-translated output currently prepared for submission. There is no mature connector for asylum case files (they live in whatever legal-aid CMS or contractor system each org uses), so this is MANUAL by necessity, not by default.

Required for every run:
1. **Source-language text** — the testimony or statement as originally given, in its original language, as text (typed, OCR'd, or transcribed from audio — note which, since transcription itself can introduce errors upstream of translation).
2. **Machine-translated output** — the MT version currently intended for submission, in the target language (almost always English for US filings).
3. **Source language name** — state it explicitly (e.g. "Pashto," "Dari," "Mexican Spanish") rather than letting it be inferred, since dialect matters for idiom and honorific interpretation.

Optional but improves the report:
4. Any known context about the claim (e.g. "persecution is family-based," "timeline of events is contested") that would make a particular shift (a tense change, a kinship-term literalization) especially high-stakes to flag.

If the source-language text is missing and only the MT output is provided, say so and stop — there is nothing to round-trip against, and a report built from the MT output alone cannot do this skill's job.

## Procedure
1. **Segment** both the source text and the MT output into matching units (sentence or clause level), preserving original order. If segment counts don't match (MT merged, split, or dropped a clause), flag that as a structural discrepancy on its own — a dropped clause is itself a legal-risk event.
2. **Back-translate** the MT output, segment by segment, into the source language (this is the round-trip check — translate the submitted English text back toward the original language and language variety named in Input 3).
3. **Separately scan for lemma-stable ambiguity** that round-trip back-translation cannot catch on its own: a word or phrase that maps consistently to the same MT rendering in both directions (so the back-translation shows no surface divergence) but that plausibly carries a second figurative, idiomatic, dialect-specific, or kinship meaning in the source language given the surrounding context. The documented real-world case is "jefe" in Mexican Spanish, which can mean "boss" or, figuratively, "father" — back-translating "boss" produces "jefe" again, hiding the ambiguity from a pure round-trip check. For each content word/phrase in the source text, ask: does this language/dialect give this word a plausible second sense here, and does the surrounding context (who is being described, what relationship, what's at stake) make that second sense at least as likely as the MT's literal rendering? If yes, flag it even though the back-translation alone wouldn't surface it.
4. **Compare** each back-translated segment against the actual original source segment, combining both the round-trip divergences from step 2 and the lemma-stable ambiguities from step 3. For every divergence found by either method, classify it into one of these categories (don't force a fit — use "other" if none apply, but don't drop it):
   - **Pronoun/number/person shift** — singular↔plural, gender, or person changed (the "I" → "we" failure mode).
   - **Tense/aspect shift** — a change that implies a different timeline (past habitual vs. one-time event, completed vs. ongoing).
   - **Idiom-to-literal substitution** — a figurative expression rendered word-for-word, losing or inverting its meaning (including kinship terms used figuratively, e.g. a word that can mean both "boss" and "father" depending on context).
   - **Honorific/formality collapse** — a respect register, euphemism, or indirect phrasing flattened into something that can read as blunt, evasive, or inconsistent in tone.
   - **Negation/polarity flip** — an affirmative/negative inverted or hedged.
   - **Numeral/date/name shift** — a number, date, or proper noun changed or garbled.
   - **Structural drop/merge** (from step 1).
5. **Score confidence** per flag: HIGH (the divergence is clear and the category fits cleanly), MEDIUM (plausible divergence but could be an artifact of back-translation itself rather than the original MT), LOW (worth a second look but genuinely uncertain). Because false negatives are the dangerous failure mode here, resolve any genuine toss-up by flagging it at LOW confidence rather than dropping it — never suppress a borderline case to keep the report short. The converse also matters: do not flag a segment that is, on inspection, a faithful translation with no plausible alternate reading — manufacturing flags on clean segments wastes the reviewer's limited time and erodes trust in every other flag in the report.
6. **Draft a suggested correction** for each flag — what the MT output should probably say instead — but label it clearly as a suggestion for a qualified human translator to verify, never as an accepted fix. Where a lemma-stable ambiguity (step 3) has two plausible readings rather than one clear fix, present both readings and say explicitly that a human translator must disambiguate using context the model doesn't have access to.
7. **Never apply any correction to the document.** This skill only produces a report; it does not edit the submission.

## Output format
Open every report with this exact banner:

```
REVIEWER-ASSISTIVE TOOL — NOT A CLEARANCE OR TRANSLATION DECISION.
This report flags where machine translation may have introduced a legal-risk
discrepancy. Every flag requires review by a qualified human translator before
any action is taken. Absence of a flag is not a certification of accuracy.
```

Then, one block per flagged segment, in source-text order:

```
Segment [N]: <source-language segment, quoted>
MT output:  <corresponding MT segment, quoted>
Discrepancy type: <category from Procedure step 4>
What shifted: <one sentence — plain-language description of the divergence>
Why this is risky: <one sentence — how an adjudicator could misread this as inconsistency, evasion, or a factual change>
Suggested correction (unverified — human translator must confirm): <text>
Confidence: HIGH | MEDIUM | LOW
```

Close with a summary line: `N segments reviewed — F flagged (H high-confidence, M medium, L low). Recommend human translator review of all flagged segments before submission.`

If zero discrepancies are found, still output the banner and summary line (`0 flagged`) — never omit the disclaimer just because nothing was caught, since a clean report is exactly the case where a reviewer might be tempted to skip further review.

## Guardrails
- Never state or imply that a document has "passed," is "clear," or is safe to submit — only ever report what was found or not found in this pass.
- Never auto-correct, rewrite, or silently fix the submitted MT output; every suggested correction is advisory text in the report, not an edit to the source document.
- Never suppress a flag to shorten the report or because confidence is low — weight recall over precision explicitly; a missed real ambiguity is the harmful failure mode, a flagged false positive costs a reviewer two minutes.
- Never treat this report as evidence of the claimant's credibility, honesty, or the merits of their case — it evaluates translation fidelity only, never the underlying testimony's truthfulness.
- Never guess at a source language's dialect-specific idiom or kinship-term meaning with unwarranted confidence; if genuinely uncertain whether a word carries a figurative second meaning in the named dialect, flag it at LOW confidence and say the uncertainty explicitly rather than picking one reading silently.
- Flag, in the summary, that flagged reports can themselves be discoverable in legal proceedings — recommend the user confirm with counsel who should have access to this report before sharing it.
- Do not produce this report from the MT output alone; refuse (per Inputs) if the source-language original wasn't provided.
