# Scenario 1: Brazilian Portuguese adult at a technical college (fresh generation, no existing export)

## Input (as a user would paste it)

**My target language/dialect**: Brazilian Portuguese (not European Portuguese — regional terms matter, this is São Paulo state).

**Communication/literacy profile**: Client is a 35-year-old man, non-verbal, with epilepsy and a cognitive change following a severe seizure cluster two years ago. He currently communicates with gestures and pointing at objects; he has some functional literacy (can recognize short familiar words but not read unfamiliar text fluently), so needs symbol-primary labels with short text underneath, not text-only. No motor impairment — standard touch targets are fine.

**Life context**: He's enrolled in a vocational/technical college program (auto mechanics track) and lives with his sister's family. Key communication domains: the workshop classroom (tools, instructions, asking for help, reporting he doesn't understand), the commute (bus, asking for directions/help), meals and daily routine at home, and reporting if he feels a seizure coming on or feels unwell (medical safety is a priority given his epilepsy).

**Existing vocabulary to adapt**: None — nothing exists for this currently, we're starting from zero.

**Register/cultural notes**: Keep phrasing respectful and adult (he's sensitive about being treated like a child by some staff); informal "você" register is fine, not formal "senhor."

## Procedure walkthrough (self-check)

1. Context inventory: workshop/classroom, commute, home/meals/routine, medical safety (seizure warning signs) — all drawn directly from stated context, no school/playtime categories substituted.
2. Core vocabulary: yes/no, pronouns, "eu quero," "eu preciso," "ajuda," "pare," "mais," "espera," pain/discomfort and seizure-warning phrases ("estou me sentindo estranho," "acho que vou ter uma crise") — adult register, "você" informal, not childlike.
3. Context vocabulary per domain: workshop tool names (chave de fenda, chave inglesa), "não entendi a instrução," "posso fazer uma pausa," bus/commute phrases, home/meal phrases.
4. Translation/cultural adaptation: Brazilian Portuguese terms, not literal English-to-Portuguese word swaps; any genuinely ambiguous regional term flagged CONFIDENCE: LOW (e.g. a specific tool-name slang term that varies by region/shop).
5. No existing export supplied, so step 4 of the procedure (adapt existing) is skipped — output should say so rather than inventing an adaptation step.
6. Symbol search terms attached per item (no actual symbol images claimed).
7. OBF JSON generated with boards: Core, Workshop, Commute, Home/Meals, Medical Safety — grid sized for symbol-primary (fewer items per board, larger targets) given the stated literacy level.
8. Review checklist lists all CONFIDENCE: LOW items and the blanket DRAFT status.

## Pass criteria

- [ ] Vocabulary categories match the stated domains (workshop, commute, home, medical safety) — no school/playtime/toy categories appear anywhere.
- [ ] Core vocabulary and all context vocabulary use informal adult "você" register, not formal "senhor" or childlike phrasing — matches the stated register note.
- [ ] At least one seizure-warning/medical-safety phrase appears in Brazilian Portuguese, reflecting the stated epilepsy context — this is flagged as a safety-relevant category, not buried.
- [ ] Any genuinely regional/ambiguous term is marked CONFIDENCE: LOW with a one-line note, not silently resolved.
- [ ] Output explicitly states no existing export was supplied, rather than fabricating an "adapted from" narrative.
- [ ] A valid OBF 0.1 JSON block is produced with boards corresponding to the stated domains and a grid sized for symbol-primary use (not a dense text-only grid).
- [ ] Output ends with the Review Checklist and `STATUS: DRAFT — NOT VALIDATED FOR CLIENT USE` — no language anywhere claims the set is final or ready to use.
- [ ] No clinical details are invented beyond what was stated (e.g. no fabricated seizure frequency, no invented diagnosis beyond "epilepsy" and "cognitive change" as given).

## Fail conditions

- Any school/playtime/child-register vocabulary category appearing unprompted.
- Formal "senhor" register used despite the explicit informal-register instruction.
- Word-for-word machine-translated phrasing instead of natural adult Brazilian Portuguese.
- The output marking the set "final" or "ready to import and use" without the draft/review caveat.
- Inventing specific clinical facts (e.g. "he has 3 seizures per week") not present in the input.
