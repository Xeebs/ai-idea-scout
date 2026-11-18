# Scenario 2 — Kinship-term idiom and clean segment (false-positive discipline) in a Mexican Spanish statement

## Setup
A crisis-translation volunteer is reviewing a client's sworn statement for a gender/family-based persecution claim before it's submitted to an immigration judge as part of a continuance filing. The client's native language is Mexican Spanish. The volunteer has the original Spanish text and the MT output a case-management system auto-generated. This scenario also tests that the skill does NOT over-flag a segment that is actually fine, since false positives have a real cost (reviewer time) even though they're less dangerous than false negatives.

**Source language/dialect**: Mexican Spanish

**Original-language text (Spanish)**:
1. Mi jefe me golpeó muchas veces cuando yo era niña.
2. Nadie en mi familia me ayudó porque tenían miedo de él también.
3. Me fui de la casa en 2019 y no he regresado desde entonces.
4. Cuando llegó la policía, ya era demasiado tarde para mi hermana.

**Machine-translated output (English, auto-generated, intended for the filing)**:
1. My boss hit me many times when I was a little girl.
2. No one in my family helped me because they were also afraid of him.
3. I left the house in 2019 and I have not returned since then.
4. When the police arrived, it was already too late for my sister.

## Known ground-truth discrepancies (for grading only — not given to the skill)
- Segment 1: "jefe" has a well-documented figurative/regional second meaning of "father" in Mexican/Mexican-American Spanish (the same ambiguity reported by the Japan Times on real asylum MT failures), alongside its literal meaning of "boss." Rendering it as "boss" when context (a child being hit, by someone the whole family fears) strongly implies "father" is an idiom-to-literal substitution that could make a family-based persecution claim unintelligible or read as abuse by an employer rather than a parent — a materially different legal theory.
- Segments 2, 3, and 4 are accurate, faithful translations with no meaningful shift — these exist specifically to test that the skill doesn't invent discrepancies where none exist.

## Pass criteria
- Flags segment 1 as an idiom-to-literal substitution (or equivalent category), explicitly naming the "jefe" = boss/father ambiguity and explaining why reading it as "boss" undermines a family-based persecution claim.
- Does NOT flag segments 2, 3, or 4 — or if it raises any of them, does so only as a genuinely low-confidence, clearly-labeled LOW note rather than treating them as real discrepancies on par with segment 1.
- Correctly reports a count line reflecting 1 (or at most 1 high-confidence) flag out of 4 segments — not 4 flags out of 4, which would indicate the skill is pattern-matching on "any segment exists" rather than actually comparing meaning.
- Opens with the disclaimer banner; closes with the summary line; recommends human translator review.
- Suggested correction for segment 1 proposes "father" (or flags both readings as needing a human translator's disambiguation) rather than confidently asserting only one reading without noting the ambiguity requires human confirmation.

## Fail criteria
- Misses the "jefe" ambiguity entirely (the single documented, highest-value catch in this scenario).
- Flags segments 2–4 as discrepancies with no real basis, producing a noisy report that would waste a time-constrained reviewer's attention and undermine trust in the tool (the "precision still matters, just less than recall" failure mode).
- Asserts confidently that "jefe" definitely means "father" here as settled fact rather than flagging it as requiring human translator confirmation.
