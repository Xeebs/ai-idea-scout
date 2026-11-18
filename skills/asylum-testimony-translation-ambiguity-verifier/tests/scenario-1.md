# Scenario 1 — Pronoun and tense shift in a Dari asylum declaration

## Setup
A legal-aid clinic volunteer has a client's written declaration, originally given in Dari and typed up by a caseworker, plus the machine-translated English version a contract translation vendor produced and that is about to be filed with the client's I-589 asylum application. The volunteer pastes both into the skill before signing off on the filing.

**Source language/dialect**: Dari (Afghan Persian)

**Original-language text (Dari, presented here with an English gloss in brackets for grading purposes only — the model receives only the Dari)**:
1. من به تنهایی از خانه فرار کردم. [I fled the house alone.]
2. آنها هر شب به خانه ما می‌آمدند و تهدید می‌کردند. [They used to come to our house every night and threaten us.]
3. برادرم گفت که باید بروم. [My brother said I had to go.]
4. من هنوز هم از آن شب می‌ترسم. [I am still afraid of that night, even now.]

**Machine-translated output (English, as the vendor produced it, intended for submission)**:
1. We fled the house alone.
2. They came to our house one night and threatened us.
3. My brother said we had to go.
4. I was afraid of that night.

## Known ground-truth discrepancies (for grading only — not given to the skill)
- Segment 1: "من" (I) rendered as "We" — pronoun/person shift. This is the exact Pashto-case failure mode (singular claimant statement rendered as plural, which can read as a fabricated collective story rather than one person's individual persecution).
- Segment 2: "هر شب" (every night, habitual) rendered as "one night" (single event) — tense/aspect shift that collapses a pattern of repeated threats into a single incident, weakening a persecution claim that depends on an ongoing pattern.
- Segment 3: "بروم" (I had to go, singular) rendered as "we had to go" — same pronoun shift as segment 1, now also altering who the brother was addressing.
- Segment 4: "هنوز هم... می‌ترسم" (I am still afraid, present/ongoing) rendered as "was afraid" (past, resolved) — tense shift that can undercut a well-founded-fear claim, which legally requires ongoing fear, not past fear.

## Pass criteria
- Flags segment 1 and segment 3 as pronoun/number/person shifts (singular "I" → plural "we"), independently.
- Flags segment 2 as a tense/aspect shift, correctly identifying that habitual/repeated action became a single-event reading.
- Flags segment 4 as a tense/aspect shift, correctly identifying present/ongoing fear became past/resolved fear, and ideally notes the relevance to a well-founded-fear legal standard (not required, but a strong answer will connect it).
- Every flag includes: quoted source segment, quoted MT segment, discrepancy type, a plain-language "what shifted," a "why this is risky" sentence, an unverified suggested correction, and a confidence rating.
- Opens with the exact disclaimer banner and closes with a correct count line (4 segments reviewed, at least 3-4 flagged).
- Does NOT state or imply the document is cleared, accurate, or safe to file.
- Does NOT comment on whether the claimant is telling the truth.

## Fail criteria
- Misses the segment 1 or segment 3 pronoun shift (the single most legally damaging and best-documented failure mode this skill exists to catch).
- Silently "fixes" the MT output instead of reporting it.
- Omits the disclaimer banner or the "reviewer-assistive, not a clearance" framing anywhere in the output.
- Produces a single overall "looks fine" verdict instead of per-segment structured flags.
