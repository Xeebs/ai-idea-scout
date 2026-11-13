# Scenario 2: Medical literature RAG with PMID citations and dosage tables

## Input

A small team building an internal RAG assistant for clinicians to look up drug dosage guidance from package inserts and journal articles. They provide:

**DOMAIN**: FDA drug package inserts and peer-reviewed journal articles on drug dosing.

**CITATION/REFERENCE CONVENTION**: "Journal articles are cited by PMID, like 'PMID: 34521098'. Package inserts have dosage tables by patient weight/age band that must never be split from their row."

**REAL EXCERPTS**:

Excerpt 1 (from a package insert dosage section):
```
2.2 Recommended Dosage by Body Weight

| Body Weight       | Recommended Dose      | Frequency        |
|--------------------|------------------------|-------------------|
| 10 kg to < 20 kg   | 2.5 mg                | Every 12 hours    |
| 20 kg to < 40 kg   | 5 mg                  | Every 12 hours    |
| 40 kg and above    | 10 mg                 | Every 12 hours    |

Do not exceed 20 mg per day regardless of body weight. See Section 5.1 for dosage
adjustment in renal impairment.
```

Excerpt 2 (from a journal abstract):
```
Smith JA, Lee K, Patel R. Weight-based dosing outcomes in pediatric patients:
a retrospective cohort study. J Pediatr Pharmacol. 2024;29(3):210-218.
PMID: 34521098. Results showed that weight-banded dosing reduced adverse
events by 18% compared to flat dosing (p<0.01).
```

**KNOWN ISSUES**: not mentioned.

**KNOWN SUB-VARIANTS**: "This is for one specific drug's package insert plus general pediatric dosing literature — we haven't checked whether this generalizes to adult dosing or other drugs yet."

## Procedure walkthrough (self-check)

1. Structural evidence extracted: a dosage table with weight-band rows that must stay paired with their dose/frequency; an inline cross-reference ("See Section 5.1"); a journal citation format `Lastname Initial, ...  PMID: \d+`.
2. Chunking rules: treat each dosage table as one atomic unit (never split a weight-band row from its dose), and keep the "do not exceed" ceiling statement attached to the table since it modifies all rows; flag the Section 5.1 cross-reference as a case for overlap or a linked-section rule.
3. Citation patterns: `PMID:\s*\d+` — CONFIRMED, matches "PMID: 34521098"; journal citation author-list format (Lastname Initial list + journal + year) — CONFIRMED with the quoted excerpt.
4. Eval rubric: e.g. "An answer about dosage must preserve the exact weight band, dose, and frequency from a single row, never mixing rows"; "An answer citing a journal finding must include the PMID, not just the author names"; "An answer must not drop the daily-maximum ceiling when giving a per-dose answer."
5. Limitations: the user explicitly said this hasn't been checked for adult dosing or other drugs — the draft must state this as an unconfirmed scope boundary, not quietly generalize.

## Pass/fail criteria

PASS if the output:
- [ ] Produces all five required sections
- [ ] Chunking rules explicitly treat the dosage table as atomic, including the "do not exceed" ceiling statement, grounded in excerpt 1
- [ ] Citation table includes a CONFIRMED `PMID` pattern with the exact quoted match "PMID: 34521098"
- [ ] Does not invent a DOI pattern or any citation format not shown (no excerpt used DOI)
- [ ] Eval rubric includes a criterion specifically about not mixing dosage rows across weight bands
- [ ] Known Limitations section explicitly states the pack is scoped to this drug/pediatric population only, per the user's stated sub-variant note, and flags adult dosing / other drugs as unconfirmed
- [ ] Ends with the unvalidated-starter-draft reminder and does not claim clinical validation

FAIL if it treats the dosage table rows as independently splittable, invents a citation format beyond PMID/author-list, or omits the pediatric-only scope limitation despite the user stating it directly.
