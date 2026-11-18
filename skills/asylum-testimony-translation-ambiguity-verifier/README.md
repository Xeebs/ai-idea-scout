# Testimony Guard: Translation Ambiguity Verifier

A portable prompt that round-trip-checks a machine-translated asylum, immigration, or other legal testimony against its original-language source, and flags the specific translation artifacts — a flipped pronoun, a shifted timeline, a literalized idiom — that have actually caused real asylum claims to be read as inconsistent and denied. It never translates for you and never clears a document for submission; it's a pre-submission triage report for a human translator or legal-aid reviewer who doesn't have time to fully re-translate every file by hand.

This is a reviewer-assistive tool only. It does not make, and must never be used to make, any decision about a case's merits or a claimant's credibility. Works in any AI chat tool; no installation needed.

## Why this exists

Real documented cases (reported by Techdirt, Context.news, and the Japan Times, and tested directly by Respond Crisis Translation on Arabic/Farsi/Pashto/Kurdish) show machine translation silently flipping "I" to "we" in a Pashto asylum statement, or rendering a word that means "father" in context as "boss" — each creating an apparent inconsistency that an adjudicator can read as dishonesty. The only mitigation anyone has documented so far is "don't use AI translation, use a human translator instead" — which isn't realistic given legal-aid translator shortages and contractors switching to MT on cost grounds anyway. No tool anywhere currently checks MT output against its source specifically for this legal-risk-shaped class of error before it's filed. This prompt is that check.

## How to use it

Gather, before you start:
1. **The original-language text** — the testimony or statement as given, in its original language (typed, OCR'd, or transcribed — note which).
2. **The machine-translated output** — the version currently intended for submission (usually English for US filings).
3. **The source language and dialect**, named explicitly (e.g. "Pashto," "Mexican Spanish," "Haitian Creole") — don't make the model guess, since dialect changes idiom and kinship-term meaning.
4. *(Optional)* Any case context that would make a particular kind of shift especially high-stakes (e.g. "the claim depends on a family relationship," "the timeline of the escape is contested").

If you don't have the original-language text — only the English MT output — stop here; this check has nothing to compare against and cannot do its job from the translation alone.

Then paste the prompt below into any AI chat tool, followed by your four inputs.

---

### The prompt

> You are performing a pre-submission translation-ambiguity check on a legal testimony (asylum, immigration, or similar). You will be given a source-language original and its machine-translated (MT) output intended for submission. Your job is NOT to produce a better translation and NOT to approve or clear the document — it is to flag specific places where the MT output may have introduced a discrepancy that could be misread by an adjudicator as a factual inconsistency, evasiveness, or dishonesty, versus what the original actually says.
>
> Procedure:
> 1. Segment both texts into matching sentence/clause units in original order. If segment counts don't match (something was merged, split, or dropped), flag that as its own discrepancy — a dropped clause is a legal-risk event on its own.
> 2. Back-translate the MT output, segment by segment, back toward the named source language and dialect.
> 3. Separately scan for "lemma-stable" ambiguity that a pure round-trip check cannot catch: a word that maps to the same MT rendering in both directions (so back-translating it produces no visible divergence) but plausibly carries a second figurative, idiomatic, dialect-specific, or kinship meaning given the context. The real documented case is Mexican Spanish "jefe," which can mean "boss" or, figuratively, "father" — back-translating "boss" just produces "jefe" again, hiding the ambiguity. For each content word, ask whether the dialect gives it a plausible second sense here, and whether context (who's being described, what relationship, what's at stake) makes that second sense at least as likely as the literal one. Flag it if so, even though back-translation alone wouldn't surface it.
> 4. Compare each back-translated segment to the actual original segment, combining both the round-trip divergences from step 2 and the lemma-stable ambiguities from step 3. For every divergence found by either method, classify it as one of: **pronoun/number/person shift** (e.g. "I" became "we"), **tense/aspect shift** (implies a different timeline), **idiom-to-literal substitution** (a figurative expression, including a kinship term with a figurative second meaning, rendered word-for-word), **honorific/formality collapse** (a respectful or indirect register flattened into something blunt-sounding), **negation/polarity flip**, **numeral/date/name shift**, or **structural drop/merge**. Use "other" rather than forcing a bad fit, but never drop a real divergence just because it doesn't fit a category cleanly.
> 5. Score each flag's confidence HIGH, MEDIUM, or LOW. Because missing a real ambiguity is far worse than over-flagging, resolve genuine toss-ups by flagging at LOW confidence rather than dropping them — never suppress a borderline case just to keep the report shorter. The reverse matters too: don't flag a segment that's actually a faithful translation with no plausible alternate reading — manufactured flags on clean segments waste reviewer time and undercut trust in the real flags.
> 6. Draft a suggested correction for each flag, labeled clearly as unverified and requiring a qualified human translator's confirmation — never present it as an accepted fix. If a lemma-stable ambiguity has two genuinely plausible readings rather than one clear fix, present both and say explicitly that a human translator must disambiguate using context you don't have access to.
> 7. Do not edit, rewrite, or "fix" the submitted document. Produce a report only.
>
> Output format — start every report with this exact banner:
> ```
> REVIEWER-ASSISTIVE TOOL — NOT A CLEARANCE OR TRANSLATION DECISION.
> This report flags where machine translation may have introduced a legal-risk
> discrepancy. Every flag requires review by a qualified human translator before
> any action is taken. Absence of a flag is not a certification of accuracy.
> ```
> Then one block per flagged segment, in source-text order:
> ```
> Segment [N]: <source-language segment, quoted>
> MT output:  <corresponding MT segment, quoted>
> Discrepancy type: <category>
> What shifted: <one sentence>
> Why this is risky: <one sentence — how an adjudicator could misread this>
> Suggested correction (unverified — human translator must confirm): <text>
> Confidence: HIGH | MEDIUM | LOW
> ```
> Close with: `N segments reviewed — F flagged (H high, M medium, L low). Recommend human translator review of all flagged segments before submission.` If nothing is flagged, still output the banner and a `0 flagged` summary line — a clean report is exactly when a reviewer might be tempted to skip further checking, so never drop the disclaimer.
>
> Guardrails: never say or imply the document "passed," is "clear," or is safe to submit. Never treat this as evidence about the claimant's honesty or the case's merits — you are checking translation fidelity only. If you are genuinely uncertain whether a word carries a figurative or dialect-specific second meaning, say so and flag it LOW confidence rather than silently picking one reading. Note in your summary that this report itself may be discoverable in the legal proceeding, and the user should confirm with counsel who should see it before sharing it. If no source-language original is given, say you cannot perform this check from the MT output alone and stop.
>
> Here are my inputs:
> Source language/dialect: [name it]
> Original-language text: [paste]
> Machine-translated output: [paste]
> Case context (optional): [any relevant notes]

## Full project context

This prompt is the MVP of a larger idea — a verification layer legal-aid orgs and crisis-translation groups could run before any translated statement becomes part of a legal record. See [`ideas/asylum-testimony-translation-ambiguity-verifier.md`](../../ideas/asylum-testimony-translation-ambiguity-verifier.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo for the full gap analysis, evidence, and impact case.
