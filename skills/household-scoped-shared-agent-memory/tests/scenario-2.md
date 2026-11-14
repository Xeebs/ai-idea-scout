# Scenario 2 — Roommate household with an imminent departure

## Input (as the user would give it)

> Household roster:
> - Priya, Sam, and Dana — three unrelated adult roommates sharing a lease and a smart-home assistant. All three are equal, no one has admin/override — we explicitly don't want anyone to be able to see each other's private stuff.
>
> Content categories the assistant will handle:
> - Shared chore schedule
> - Shared grocery list
> - Each person's individual reminders (appointments, personal tasks)
> - Utility bill-splitting records (who owes what)
> - Voice queries to the assistant (weather, general questions)
>
> House rule: "We all agreed nobody should be able to see anyone else's individual reminders or voice query history, period, no exceptions."
>
> One more thing: Dana is moving out at the end of next month, and the lease is being re-signed without her. We want to know what should happen to her data when she goes, especially since she contributed to the shared grocery list and chore schedule.
>
> Memory backend: not decided yet.

## What a correct run looks like

- Role table lists Priya, Sam, and Dana, all with the same role (no admin/override — matching "no one has admin/override" from the input). No override access should be invented for anyone.
- Every named category (chore schedule, grocery list, individual reminders, bill-splitting records, voice queries) appears exactly once in the Content Visibility table with a stated reason.
  - Individual reminders and voice queries must be marked PRIVATE with the reasoning explicitly tied to the stated house rule ("no exceptions") — this is an easy fail mode if the skill defaults to CONDITIONAL/admin-visible when the input explicitly ruled that out.
  - Chore schedule and grocery list → SHARED.
  - Bill-splitting records → likely SHARED among roommates (money owed affects everyone) with stated reasoning, or CONDITIONAL if the run has a specific reason — either is acceptable as long as it's justified, not asserted.
- Override Rules section should state there are no overrides, consistent with the input, rather than inventing one.
- Departure-Removal Checklist must be concrete and must explicitly handle Dana's case:
  - Her fully private records (her individual reminders, her voice query history) → purge.
  - Her contributions to shared records (grocery list items she added, her share of chore schedule, her portion of bill-splitting history) → the checklist must state what happens to these (e.g., keep the shared record but strip her identifying attribution vs. fully remove her entries) and give a reason, not leave it unaddressed.
  - A verification step confirming no record remains attributable solely to Dana after the process.
- Because there's no parent/minor dynamic in this scenario, the Open Flags section may legitimately be short, but it should still flag any genuine judgment call made (e.g., "we assumed bill-splitting records should remain visible to remaining roommates for financial continuity — confirm this is what the household wants").
- No backend note is produced as a full section (backend was "not decided") — acceptable either to omit it or state briefly that it's deferred; should not fabricate a specific backend's metadata schema.

## Fail conditions
- Any override/admin access is invented for Priya, Sam, or Dana despite the input saying explicitly no one has one.
- Individual reminders or voice queries are marked anything other than PRIVATE, given the explicit "no exceptions" house rule.
- The departure checklist doesn't address Dana's shared/co-owned contributions (grocery list, chore schedule, bill-splitting) at all, or just says "delete her data" with no distinction between private and shared content.
- The skill produces a detailed Mem0/Letta/Zep-specific backend note despite the input stating the backend isn't decided.
- Any content category from the input is missing from the visibility table.
