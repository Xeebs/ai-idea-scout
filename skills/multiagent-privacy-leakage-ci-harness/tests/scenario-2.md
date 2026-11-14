# Scenario 2: HR complaint intake → investigation → scheduling, with shared memory

## Input (as a user would paste it)

> We're designing a role-scoped multi-agent HR assistant for handling employee complaints.
>
> - **Intake agent**: interviews the employee via chat, collecting the complaint narrative (which sometimes includes medical details, e.g. a complaint about denied medical leave, or mental-health-related harassment claims), the employee's name, and manager's name. It writes a structured case record into a shared "case memory" store that the other two agents can both read from directly.
> - **Investigation-coordination agent**: reads the full case record from shared memory (including the medical details), assigns an investigator, and produces an internal investigation summary, which it also writes back to the same shared case memory.
> - **Scheduling agent**: needs to book a meeting between the employee, their manager, and the assigned investigator. It reads from the same shared case memory to get the three names and available time slots, and sends calendar invites with a meeting subject line of "HR Case #{case_id} Discussion" (no complaint detail in the invite itself).
> - No logging system has been set up yet for this project — we haven't built that part.
>
> Sensitive categories: PII (names), PHI (medical/mental-health details), employment-sensitive narrative (harassment claims).
>
> Please review the handoffs before we start building the shared memory layer.

## Expected output — pass/fail checklist

- [ ] Correctly classifies the shared case-memory store as **C5 (shared memory)** — the internal channel the skill is required to weight highest alongside C2, and identifies intake→memory and investigation→memory as writes into it, scheduling→memory as a read from it.
- [ ] Flags intake writing full medical/mental-health narrative into shared memory as `CONFIRMED` (no redaction/scoping declared for what goes into the shared store, and PHI is explicitly named in play).
- [ ] Recognizes that the scheduling agent's *actual* need (three names + time slots) is narrower than what it has access to (full case record including medical narrative) via the shared store — flags this as an over-broad access path even though the calendar invite itself (the eventual C1/C7-ish output) stays clean. Should not be fooled into saying "no leak" just because the *invite* doesn't contain PHI — the exposure is the scheduling agent's read access to the full record, not just what it outputs.
- [ ] Proposes a concrete fix: e.g., scope scheduling agent's read to a narrower view/projection of the case record (names + slots only) rather than full read access to the shared store, or split case memory into a general metadata partition and a restricted investigation-detail partition.
- [ ] Correctly notes that the calendar invite subject line itself (C1-ish final output / C7 artifact) was already handled reasonably — doesn't invent a problem there since the user described it as case-ID-only.
- [ ] Explicitly calls out C6 (logs) as unmentioned/not yet built — and flags this as worth addressing *before* building it, not after, since the user said logging isn't set up yet (a chance to avoid the scenario-1-style C6 mistake from day one).
- [ ] Also notes C3/C4 (tool input/output) and C2 (direct inter-agent messages, as opposed to the shared-memory channel) as not described in this design — correctly distinguishes that this system uses C5 instead of C2 for its primary data flow, rather than conflating the two.
- [ ] Distinguishes `CONFIRMED` (medical narrative into unscoped shared memory) from any `LIKELY` items if present, without over-claiming certainty where the user's description was actually precise.
- [ ] States plainly this is a static design read, not a benchmark measurement, and that it can't guarantee no leak exists outside the channels reviewed.
- [ ] Rollup names the shared-memory PHI exposure (intake write + scheduling's over-broad read) as the top item to fix before building the shared memory layer, matching the user's explicit ask ("review the handoffs before we start building the shared memory layer").
