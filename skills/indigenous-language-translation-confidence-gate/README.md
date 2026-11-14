# Indigenous Language Translation Confidence Gate

A paste-in prompt for checking a machine-translated phrase or short document into an indigenous Mexican language variant (Mixteco, Zapoteco, Nahuatl, or a related variant) for known failure signatures *before* a school, health, or community worker hands it to a parent or patient — instead of finding out it was wrong from the family's confused reaction.

## When to use this

You already ran something through Google Translate, ModelFront, Nurbli, or another MT tool into an indigenous-language variant — a school notice, an appointment reminder, a line on an enrollment form, an IEP summary, a vaccination instruction — and before you send it, print it, or read it aloud, you want a second check on whether it's trustworthy.

This is not a certified-interpreter replacement, and it will not translate anything itself. It only evaluates text you already have.

## What to hand over

Copy this into any AI chat tool, fill in the brackets, and paste:

```
I have a machine-translated phrase/document I want checked before I use it.

SOURCE TEXT (Spanish or English):
[paste the original text]

MT OUTPUT (paste exactly as returned, including anything that looks odd — don't clean it up):
[paste the translation]

TARGET VARIANT:
[be as specific as you can — e.g. "Mixteco de San Juan Mixtepec," "Zapoteco del Istmo." If you only know "Mixtec" or "Zapotec" generically, say so.]

CONTEXT/DOMAIN:
[school notice / health instruction / enrollment form / IEP or legal / emergency / casual reminder, etc. — state the stakes, not just the topic]

OPTIONAL — BACK-TRANSLATION:
[if you can, run the MT output back through a translator into Spanish/English and paste that result here — this is the single most useful optional input]

OPTIONAL — VALIDATED GLOSSARY ENTRIES FOR THIS VARIANT:
[paste any phrases your organization has already had confirmed by a native speaker for this exact variant, if any]

Please run the confidence-gate check described below and give me a tier and a recommendation.
```

## What the AI should do with it (the full procedure)

1. **Check coverage first.** If the target variant was only named generically ("Mixtec," "Zapotec") rather than at the town/region level, say so up front. There are 81 documented Mixtec variants and 50+ Zapotec languages (per INALI) that often don't understand each other well — checking against the wrong variant's norms is worse than not checking at all.

2. **Scan the MT output for known failure signatures** — this doesn't require knowing the target language:
   - A literal "no entiendo," error message, placeholder, or "[translation unavailable]"-style string.
   - The same word or short phrase repeated three or more times in a row (a known degenerate-loop failure mode).
   - Output that's identical or nearly identical to the source text (it didn't actually translate).
   - Output that's drastically shorter than the source for a phrase that isn't naturally short (possible dropped content).
   - Garbled or mixed-script text, mojibake, or repeated punctuation runs.
   Any one of these is an automatic red flag, no matter what else checks out.

3. **Compare the back-translation to the source**, if one was supplied. Do the key facts match — same dates, times, numbers, names? Does the core instruction match (required vs. optional, do vs. don't)? Any mismatch in entities or core meaning is a red flag. If no back-translation was supplied, that caps how confident the result can be, even if everything else looks fine.

4. **Score the complexity of the source text.** Research on these language pairs shows translation quality is strong for short, common, single-clause phrasing (like dates, times, simple instructions) and degrades sharply for idioms, multi-clause/conditional sentences, or legal/medical jargon — in academic tests, BLEU scores ranged from about 17-22 on general text up to 96-99 on narrow, common-phrase text. Mark the source LOW complexity (short, common, single-clause) or HIGH complexity (anything more nuanced). HIGH complexity caps the result at a middle confidence level even if the output looks clean.

5. **Check against any supplied glossary entries.** If the user provided validated phrases for this exact variant and one matches the source phrase, treat it as ground truth and flag any mismatch with the pasted MT output. If no glossary was supplied, skip this — never invent a glossary entry. Making up a "validated" translation would be exactly the kind of false confidence this check exists to catch.

6. **Assign a tier:**
   - **HIGH** — no red flags, the phrase is low-complexity, and either the back-translation was consistent or a glossary match confirmed it.
   - **MEDIUM** — no red flags, but missing back-translation or glossary confirmation, or the phrase was high-complexity, or the variant was only named generically.
   - **LOW** — any red flag triggered (failure signature, back-translation mismatch, or glossary mismatch).

7. **Apply the stakes override.** Regardless of the tier, if the context is legally or medically binding — IEP/special-education meetings, informed medical consent, immigration or legal proceedings, emergency instructions — the recommendation is always to use a human interpreter, stated as a hard rule, not a suggestion, even if the tier came back HIGH.

8. **Give a concrete recommendation**, not just a score: send as-is, send with a stated caveat (name it — e.g. "not validated for this specific variant"), or escalate to a human interpreter (name the kind of resource: a district language liaison, a service like Indigenous Interpreting+, a phone-interpretation line like Nurbli, or whatever the user's own partner organization is).

## Output you should get back

```
CONFIDENCE TIER: HIGH | MEDIUM | LOW

Coverage: [variant as given, flagged if generic]
Signature scan: [pass, or which signature(s) triggered]
Back-translation check: [not supplied / consistent / where it diverged]
Complexity: LOW | HIGH — [why]
Glossary check: [not supplied / match / where it mismatched]

Recommendation: [send as-is | send with caveat: "..." | escalate to human interpreter via <named resource>]
Stakes override: [none, or "YES — this domain always requires a human interpreter regardless of tier"]
```

## What this will never do

- Invent an indigenous-language glossary entry, a back-translation, or a dialect fact you didn't supply. If you want a real glossary for your specific variant, that has to come from a native speaker or a partner organization — this check only evaluates what you give it.
- Call it HIGH confidence when the variant is only named generically. Variant mismatch (wrong town, wrong dialect) is the single biggest documented cause of these translations failing.
- Let a clean-looking result override the stakes rule for IEP meetings, medical consent, or legal/immigration matters — those always get the human-interpreter recommendation.
- Claim to be a certified interpreter, a compliance artifact, or a substitute for your organization's actual language-access obligations. It's a second opinion on text you already have, nothing more.
