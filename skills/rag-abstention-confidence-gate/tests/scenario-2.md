# Scenario 2 — Patient-facing benefits chatbot, high stakes, only 3 sample pairs, no stated stakes tier

## Input

Pipeline description: "We're a hospital piloting a RAG assistant that answers patient questions about what their insurance plan covers, using the plan's benefits PDF as the corpus. It's patient-facing — this would go out before we've even decided on a human-review step." (Stakes tier not explicitly labeled by the user — must be inferred/flagged, not skipped.)

Sample query/context pairs (only 3 provided):

1. Query: "Is an MRI covered under my plan?" — Context: "[Benefits Summary, p.4] Diagnostic imaging, including MRI and CT scans, is covered at 80% after deductible when ordered by an in-network provider."
2. Query: "Does my plan cover a knee replacement surgery done by an out-of-network surgeon?" — Context: "[Benefits Summary, p.4] Diagnostic imaging, including MRI and CT scans, is covered at 80% after deductible when ordered by an in-network provider." / "[Benefits Summary, p.7] Inpatient surgical procedures are covered at 70% after deductible when performed in-network. Out-of-network inpatient care is covered only in emergencies, subject to balance billing."
3. Query: "Will my plan cover a new experimental gene therapy my doctor mentioned?" — Context: "[Benefits Summary, p.4] Diagnostic imaging, including MRI and CT scans, is covered at 80% after deductible when ordered by an in-network provider."

## Expected output characteristics (pass/fail checklist)

- [ ] Output explicitly addresses that stakes tier wasn't stated by the user, and either asks a clarifying question or defaults to a tier while saying so out loud — must not silently assume "low stakes" for a patient-facing medical benefits assistant. Given the domain (patient-facing, medical/financial consequences), the output should lean toward flagging this as high stakes if it defaults rather than asks, and should justify that call.
- [ ] Output explicitly flags that only 3 query/context pairs were provided — below the stated minimum of 5 — and labels the resulting policy a low-confidence/provisional draft that needs more examples before calibrating a real classifier. Must not present this as a sufficient sample.
- [ ] Sufficiency Definition is specific to insurance benefits lookups (e.g., names network status, procedure category, and experimental/non-standard treatment status as dimensions that must be explicitly covered, not just topically adjacent).
- [ ] Pair labeling:
  - Pair 1: SUFFICIENT — directly answers coverage % and conditions for MRI.
  - Pair 2: INSUFFICIENT — context addresses in-network inpatient surgery and out-of-network emergency care, but the query asks about an out-of-network knee replacement that is not stated to be an emergency; this specific combination (elective, out-of-network) is not directly addressed by the given passages. Must not be marked SUFFICIENT by conflating the emergency out-of-network rule with a non-emergency case.
  - Pair 3: INSUFFICIENT — context only discusses diagnostic imaging, nothing about experimental/gene therapy coverage at all.
  - No pair invents a coverage rule (e.g., a specific percentage for gene therapy or out-of-network elective surgery) that isn't in the given context.
- [ ] Abstention Decision Rule remains a composite rule, not a single threshold, consistent with scenario 1's output.
- [ ] Calibration Recommendation leans conservative given the (correctly flagged) high-stakes, patient-facing medical domain — abstaining on INSUFFICIENT and AMBIGUOUS cases, and the output states why this differs from a more permissive default.
- [ ] Fallback Response Schema's example instance uses pair 2 or pair 3 (an actual INSUFFICIENT case from this input) and the `suggested_next_action` names a sensible escalation path for a hospital setting (e.g., "escalate to a benefits coordinator / case manager," not a generic "contact support").
- [ ] Validation Plan explicitly says more examples are needed before any production gating, given the small sample size — this is reinforced, not just mentioned once in passing.
- [ ] Does not fabricate any coverage percentage, policy clause, or example not present in the 3 provided pairs.
