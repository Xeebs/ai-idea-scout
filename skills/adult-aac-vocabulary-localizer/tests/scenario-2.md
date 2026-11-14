# Scenario 2: Kinyarwanda-speaking stroke survivor, adapting an existing (pediatric, English) export

## Input (as a user would paste it)

**My target language/dialect**: Kinyarwanda (Rwanda) — not Kirundi, which I know is sometimes confused with it.

**Communication/literacy profile**: Client is a 58-year-old woman, had a stroke eight months ago, left with severe expressive aphasia (she understands spoken Kinyarwanda well, can occasionally produce single words, but cannot form sentences). She was literate before the stroke in Kinyarwanda but now has difficulty reading long text, so short text plus symbols is better than symbol-only or long text. No significant motor impairment in her hands.

**Life context**: Lives at home with her husband and adult daughter, in a suburban setting. Key domains: home/daily routine with family, grocery/market errands (she sometimes goes with her daughter), medical appointments (ongoing physical therapy and neurology follow-ups), and expressing needs/preferences to her husband and daughter (she gets frustrated when she can't specify what she wants, e.g. food preferences, pain location).

**Existing vocabulary to adapt**: Yes — my clinic has an English-language OBF export originally built for a pediatric client (word list only, no JSON, since that's all I have access to): "mommy, daddy, school, friend, play, toy, snack, juice, bathroom, tired, happy, sad, more, stop, help, teacher, recess, homework, bus (school bus)."

**Register/cultural notes**: None specified beyond respectful adult register — she is a grandmother and should be addressed/represented accordingly, not in childlike terms.

## Procedure walkthrough (self-check)

1. Context inventory built from stated domains: home/family routine, market/errands, medical appointments (PT, neurology), preference/needs expression (food, pain) — no school domain invented.
2. Existing export review: "mommy, daddy, school, friend, play, toy, teacher, recess, homework, bus (school bus)" are explicitly child-coded and must be flagged/replaced or dropped given the adult context; "snack, juice, bathroom, tired, happy, sad, more, stop, help" are plausibly adult-adaptable core items and should be kept/adapted into Kinyarwanda rather than discarded wholesale.
3. Translation into Kinyarwanda must be adult-register (e.g. not translating "mommy/daddy" literally into a child's-address form when the new context is a grandmother's own household — this should be caught and reframed, e.g. toward family-member vocabulary she'd use to refer to/address her husband and daughter as an adult, or dropped if not applicable).
4. New domain vocabulary added: market/errand phrases, medical-appointment phrases (pain location reporting is safety-relevant, aligns with her neurology follow-ups), preference-expression phrases (food choices).
5. Any Kinyarwanda term the model is unsure about (regional variation, an idiom for pain description) flagged CONFIDENCE: LOW.
6. Output must explicitly state what was kept, changed, and added from the original pediatric word list — not silently regenerate from scratch and ignore the supplied list.
7. OBF JSON generated with boards reflecting the new adult domains, short-text-plus-symbol format given her literacy profile.
8. Review checklist and DRAFT status included.

## Pass criteria

- [ ] Output explicitly lists what was kept, changed, and added from the supplied pediatric English list — this is the core behavior being tested (adapt, don't discard-and-restart).
- [ ] "School," "teacher," "recess," "homework," "school bus," "play," "toy" are flagged as child-coded and either dropped or clearly reframed for the adult context — not carried over unchanged.
- [ ] Plausibly adult-adaptable items ("snack"→food/drink, "tired," "happy," "sad," "more," "stop," "help," "bathroom") are kept and translated into Kinyarwanda in adult register, not discarded just because the source was pediatric.
- [ ] New vocabulary is added for market/errands, medical appointments, and pain/preference reporting — matching her stated stroke/aphasia/PT context, including at least one pain-location phrase.
- [ ] "Mommy/daddy" style address terms are not carried over unchanged into an adult grandmother's vocabulary set without being flagged or reframed.
- [ ] At least one Kinyarwanda term is marked CONFIDENCE: LOW if genuinely ambiguous, or the output explicitly states none were ambiguous enough to flag (either is acceptable, but silent translation of a genuinely uncertain regional term is not).
- [ ] Valid OBF JSON produced with short-text-plus-symbol formatting matching her literacy profile (not symbol-only, not dense unsupported long text).
- [ ] Ends with Review Checklist and `STATUS: DRAFT — NOT VALIDATED FOR CLIENT USE`.

## Fail conditions

- Carrying over "mommy/daddy/school/teacher/recess/homework/toy/play" into the output unchanged and unflagged, as if an adult stroke survivor's vocabulary set.
- Discarding the entire supplied list and generating a fresh set with no acknowledgment of what was reused.
- Confusing Kinyarwanda with Kirundi or another regional language despite the explicit clarification.
- Omitting pain/medical-safety vocabulary despite the stated ongoing neurology/PT context.
- Claiming the adapted set is validated or ready for immediate clinical use.
