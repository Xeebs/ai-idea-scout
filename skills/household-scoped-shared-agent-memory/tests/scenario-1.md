# Scenario 1 — Family building a household assistant before launch

## Input (as the user would give it)

> Household roster:
> - Alex — parent, sets policy for the household (admin)
> - Jordan — Alex's partner, adult, co-parent, no special override beyond what any adult has
> - Riley — 16-year-old, Alex and Jordan's kid
>
> Content categories the assistant will handle:
> - Voice chat transcripts (anyone talking to the assistant out loud)
> - Shared calendar/scheduling
> - Grocery/shopping list
> - Each person's individual search queries to the assistant
> - Financial/billing reminders (rent, subscriptions)
> - Health/medication reminders
> - Messages the assistant drafts on someone's behalf to send to other people
>
> Existing house rules: none written down yet, but Alex says "I want to be able to check in on Riley's safety if something seems off, but I don't want Jordan and Riley to feel like I'm reading everything they say to the assistant all the time."
>
> Memory backend: we're planning to use Mem0.

## What a correct run looks like

- Role table lists all three members with correct roles; Alex marked with override/admin access, Jordan and Riley without blanket override.
- Every one of the 7 named content categories appears in the Content Visibility table exactly once, each with a stated default (SHARED/PRIVATE/CONDITIONAL) and a one-line reason — not a generic reason.
  - Reasonable expected defaults: calendar and grocery list → SHARED; individual search queries → PRIVATE or CONDITIONAL (not blanket SHARED, since nothing in the input says searches should be visible to the whole household); financial/billing → CONDITIONAL (admin-visible) or SHARED among adults only, with reasoning; health/medication → CONDITIONAL (who needs to know); messages drafted to third parties → PRIVATE to the sender, with a note about who the message is to.
- Override Rules section states Alex's override narrowly (not "sees everything") and ties it to Alex's stated concern (safety check-ins), not a blanket grant.
- The tension Alex raised (wanting safety visibility into Riley's activity without blanket surveillance, and the implied discomfort Jordan/Riley might feel) is surfaced explicitly in the **Open Flags** section, with both sides stated — this must NOT be silently resolved by just granting Alex full override.
- Reclassification Triggers table includes at least one concrete, named trigger (not necessarily related to Riley's age, since no turning-18 detail was given — a fabricated trigger not tied to anything in the input is a fail).
- Departure-Removal Checklist is present with numbered steps and explicitly addresses what happens to shared/co-owned content (e.g., a shared grocery list item Riley added) as well as fully private content — a checklist that only mentions "delete their private data" and ignores shared/co-owned content fails this test.
- Backend Note section is present (since Mem0 was named) and is a short paragraph, not code.
- No content category is left out of the visibility table; no roster member is left out of the role table.
- Nothing in the output claims the scheme is legally compliant or already enforced.

## Fail conditions
- Alex is given blanket "sees everything" override without the narrowing tied to the stated safety concern.
- The parent-access-vs-teen-privacy tension is resolved silently in either direction instead of being flagged as an open question.
- Any of the 7 content categories is missing from the table, or appears with no stated reasoning.
- The departure checklist only covers private data and never addresses shared/co-owned records.
- The output includes actual code, an API call, or a claim of legal compliance.
