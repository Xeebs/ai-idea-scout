# Scenario 1 — Internal HR policy chatbot, medium stakes, 8 sample pairs

## Input

Pipeline description: "We run a RAG chatbot over our company's HR policy PDFs (PTO, benefits, remote work, expense reimbursement). Employees ask it questions and it answers directly, no human in the loop. A wrong answer usually means someone misses a deadline or files something incorrectly — annoying, occasionally costs them money, but not dangerous." (Stakes: medium, stated.)

Sample query/context pairs (8):

1. Query: "How many vacation days do I get per year?" — Context: "[PTO Policy §2.1] Full-time employees accrue 15 days of PTO annually, prorated for partial years of service."
2. Query: "Can I carry over unused vacation days into next year?" — Context: "[PTO Policy §2.4] Full-time salaried employees may carry over up to 5 unused PTO days into the following calendar year. Carryover days must be used by March 31 or are forfeited."
3. Query: "Can contractors carry over unused PTO?" — Context: "[PTO Policy §2.4] Full-time salaried employees may carry over up to 5 unused PTO days into the following calendar year. Carryover days must be used by March 31 or are forfeited."
4. Query: "What's the reimbursement limit for a client dinner?" — Context: "[Expense Policy §4.2] Meals with clients are reimbursable up to $75 per person. Receipts required for any expense over $25."
5. Query: "Can I expense a parking ticket I got while driving to a client meeting?" — Context: "[Expense Policy §4.2] Meals with clients are reimbursable up to $75 per person. Receipts required for any expense over $25." / "[Expense Policy §4.5] Mileage for personal vehicle use on company business is reimbursed at the IRS standard rate."
6. Query: "How many days a week do I need to be in the office?" — Context: "[Remote Work Policy §1.1] Employees in hybrid roles are expected to work from the office a minimum of 2 days per week, as designated by their manager." / "[Remote Work Policy §1.3] Fully remote roles, as designated in the employee's offer letter, have no in-office requirement."
7. Query: "If I get married, can I add my spouse to my health insurance outside open enrollment?" — Context: "[Benefits Policy §3.1] Open enrollment occurs annually in November. Qualifying life events (marriage, birth/adoption of a child, loss of other coverage) allow enrollment changes outside the open enrollment window, within 30 days of the event."
8. Query: "What happens to my unused PTO if I'm laid off?" — Context: "[PTO Policy §2.1] Full-time employees accrue 15 days of PTO annually, prorated for partial years of service." / "[PTO Policy §2.4] Full-time salaried employees may carry over up to 5 unused PTO days into the following calendar year."

## Expected output characteristics (pass/fail checklist)

- [ ] Pipeline Summary states domain (HR policy chatbot), stakes tier (medium, correctly taken from user's explicit statement, not re-guessed), and sample size (8).
- [ ] Sufficiency Definition is specific to HR policy queries (e.g., names the failure shape of a chunk matching one employment category — full-time/salaried — being wrongly applied to a different one — contractor/hourly — as insufficient even though topically relevant). Not a generic boilerplate definition.
- [ ] All 8 pairs are labeled SUFFICIENT, INSUFFICIENT, or AMBIGUOUS with a rationale:
  - Pair 1: SUFFICIENT (directly answers).
  - Pair 2: SUFFICIENT if asker is known full-time/salaried, but since employment type of the asker isn't given, this should be flagged AMBIGUOUS or SUFFICIENT-with-caveat — the output must at minimum note the full-time/salaried qualifier matters.
  - Pair 3: INSUFFICIENT — context only covers full-time salaried employees, query asks about contractors, a clearly different category. This is the central test case; must not be marked SUFFICIENT.
  - Pair 4: SUFFICIENT.
  - Pair 5: INSUFFICIENT — neither passage addresses parking tickets/fines; mileage and meal rules don't cover this.
  - Pair 6: AMBIGUOUS or INSUFFICIENT — context answers for hybrid roles but query doesn't state whether the asker is hybrid or fully remote.
  - Pair 7: SUFFICIENT — directly answers via the qualifying-life-event rule.
  - Pair 8: INSUFFICIENT or AMBIGUOUS — context states carryover/accrual rules but never addresses payout-on-termination, a different policy question.
  - No pair is labeled with a rationale that references information not present in the given context (no invented policy details).
- [ ] Labeled Sample Set table includes all 8 rows, split into should-answer / should-abstain buckets, with ambiguous cases separately listed.
- [ ] Abstention Decision Rule is a composite rule (entity/condition coverage + does-it-state-the-answer + contradiction check) — does NOT reduce to "if similarity score > X."
- [ ] Calibration Recommendation maps medium stakes to "balanced" strictness (abstain on INSUFFICIENT and most AMBIGUOUS) and states this explicitly, not just implicitly.
- [ ] Fallback Response Schema includes all five named fields (status, message, partial_findings, suggested_next_action, confidence_note) with at least one filled-in example using one of the actual INSUFFICIENT pairs above (e.g., pair 3 or 5).
- [ ] Validation Plan states a concrete additional-sample recommendation and names exactly the three metrics (abstention precision, abstention recall, false-answer rate) — does not claim the 8-example draft is production-ready.
- [ ] Does not fabricate any query, context, or policy detail beyond what was given.
