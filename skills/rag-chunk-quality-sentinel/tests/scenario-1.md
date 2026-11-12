# Scenario 1 — Internal HR handbook bot (Markdown, naive fixed-size splitter)

## Setup given to the skill

**Chunker config**: fixed-size character splitter (not markdown-aware), chunk size ≈ 480 characters, overlap 40 characters, source format: Markdown (`employee-handbook.md`).

**Sample of chunks** (12, in order, IDs as given):

```
[C1] # Employee Handbook — Leave Policies

## Parental Leave

Full-time employees are eligible for 12 weeks of paid parental leave following the birth, adoption, or foster placement of a child. Leave must be

[C2] taken within 12 months of the qualifying event and may be split into two blocks of at least two weeks each. Employees should notify their manager and HR at least 30 days before the intended start date whenever possible.

[C3] ## Bereavement Leave

Employees may take up to 5 paid days for the death of an immediate family member (spouse, child, parent, sibling) and up to 2 paid days for an extended family member. Additional unpaid leave can be arranged with manager approval.

[C4] ## Jury Duty

[C5] Employees summoned for jury duty should provide a copy of the summons to HR as soon as it is received. The company pays full salary for up to 10 business days of jury service; employees must submit a certificate of attendance from the court for each day claimed.

[C6] ## Paid Time Off Accrual Table

| Years of Service | Annual PTO Days | Carryover Cap |
|---|---|---|
| 0–2 | 15 |

[C7] | 3–5 | 20 | 10 |
| 6+ | 25 | 15 |

PTO accrues monthly and unused days above the carryover cap are forfeited at year-end unless local law requires payout.

[C8] ## Sick Leave

Sick leave accrues at one day per month, capped at 12 days per year. Employees in jurisdictions with statutory sick leave minimums receive whichever is greater between the statutory minimum and this policy.

[C9] ## Remote Work Eligibility

Roles classified as "remote-eligible" in the HR system may work from any company-approved location. Managers set core collaboration hours; employees are expected to be reachable during th

[C10] ese hours regardless of time zone. Exceptions require VP-level sign-off and are reviewed quarterly.

[C11] ## Travel Reimbursement

Business travel expenses are reimbursed per the Travel & Expense policy linked in the intranet. Receipts are required for any

[C12] single expense over $25. Reimbursement requests must be submitted within 60 days of the expense date or they may be denied.
```

No source document supplied beyond the chunks themselves.

## Planted defects (for the evaluator — not shown to the skill)

- **C4 — orphaned header**: `## Jury Duty` heading alone, zero body text; the content landed entirely in C5.
- **C6/C7 — broken table split**: the PTO table's header row + first data row are in C6, remaining rows in C7, split mid-table.
- **C9/C10 — truncation / mid-word cut**: C9 ends mid-word (`"th"`) and C10 starts with the word fragment completion (`"ese hours"`), a hard character-count truncation, not a sentence boundary.
- C1→C2, C11→C12 are also character-truncated mid-sentence (lower-severity truncation, same defect type as C9/C10) — a thorough run should catch at least the clearest case (C9/C10) and ideally also flag C1/C2 and C11/C12.
- No table/markup defects exist outside C6/C7 — a correct run should not invent additional table-split findings on clean chunks (C3, C5, C8, C11, etc.).
- No lost-cross-reference or duplicate-overlap defects are planted in this sample — a correct run should not report them.

## Pass/fail criteria

- [ ] Identifies C4 as an orphaned header (heading with no/minimal body).
- [ ] Identifies C6/C7 as a broken table split, naming both chunk IDs.
- [ ] Identifies C9/C10 as truncation/mid-word cut, quoting the split word as evidence.
- [ ] Does not report a table-split or orphaned-header defect on any chunk other than C4 and C6/C7.
- [ ] Does not fabricate a lost-cross-reference or duplicate-overlap finding (none are planted).
- [ ] Reports an overall defect rate as `flagged/12` with the sample size stated alongside it, not as a bare percentage.
- [ ] Recommends at least: (a) a markdown-aware or heading-attaching splitter to fix the orphaned header, (b) a table-atomic chunking rule to fix the table split, (c) a sentence-boundary-aware splitter (or larger chunk size) to fix the mid-word truncations — each recommendation tied to the specific chunk IDs it would fix.
- [ ] Does not add a low-confidence caveat that blocks the recommendations outright (12 chunks is a thin but usable sample — a caveat noting "this is a small sample, verify with more chunks before treating the rate as corpus-wide" is fine; refusing to give a rate or recommendations is not).
