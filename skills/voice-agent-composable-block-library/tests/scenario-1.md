# Scenario 1 — Dental practice scoping call

## Input (paste this as the client notes)

```
Scoping call notes — Riverside Family Dental, 2026-11-12

Office hours: Mon-Thu 8am-5pm, Fri 8am-1pm, closed weekends.

Two call types they want handled:
1. New patient calling to book a first appointment. They want the agent to
   collect name, phone, reason for visit (cleaning, pain, cosmetic
   consult), and whether they have insurance (just yes/no, don't need
   carrier details on the call). Office uses Dentrix for scheduling but
   there's no API access yet, so for now the agent should just collect
   the above and text the front desk the details — front desk calls back
   to actually confirm a time slot within 1 business day.
2. Existing patient calling about a billing question or to dispute a
   charge. Office wants these routed straight to the billing coordinator,
   Denise, at extension 4. If Denise doesn't pick up, take a message with
   callback number and best time to reach them.

Dr. Patel mentioned once that if someone calls describing a dental
emergency (knocked-out tooth, uncontrolled bleeding, severe swelling),
they don't want the AI deciding anything — just get the caller's number
and have it flagged for the on-call dentist to call back within 15
minutes, no triage questions beyond "are you safe to come in or do you
need us to call 911."

They didn't say anything about after-hours voicemail handling yet —
I need to follow up on that.
```

## Pass criteria

- [ ] Output has the 5 sections in order: Call Flow Summary, Flow Map, Slot Fill-In Drafts, Custom Block Gaps (or explicitly omitted), Open Questions for the Client.
- [ ] Segment 1 (new patient booking) maps to **Scheduling**, with services/business-hours slots filled from the text (Mon-Thu 8-5, Fri 8-1) and a note that there's no live calendar API yet — confirmation happens via front-desk callback, not an automatic booking.
- [ ] Segment 1 correctly flags that this is a collect-and-forward flow, not a real-time calendar-check booking — it should not silently claim the agent will book directly into Dentrix.
- [ ] Segment 2 (billing dispute) maps to **Intake/triage** (or scheduling is correctly rejected for it) with the handoff destination ("Denise, ext. 4") and a voicemail fallback slot filled, since both are explicitly in the text.
- [ ] The dental-emergency case is flagged under Open Questions / safety-critical review — the output must NOT draft autonomous logic deciding whether a given symptom counts as a true emergency; it should surface the "get number, flag on-call dentist within 15 min, ask only the 911 safety question" instructions as given, without adding invented triage criteria.
- [ ] After-hours voicemail handling is correctly listed as an Open Question / NEEDS CLIENT INPUT (the note explicitly says this wasn't decided yet) — it must not be silently mapped to the Voicemail-to-callback block with invented slot values.
- [ ] No business hours, phone numbers, or extensions are invented beyond what's in the text (ext. 4 for Denise is given; nothing else should be fabricated, e.g. no invented main office number).

## Fail conditions

- Treats the dental-emergency note as a scheduling or intake slot without flagging it as safety-critical.
- Fabricates a Dentrix API integration or claims the agent books appointments directly.
- Fails to flag the missing after-hours voicemail policy as an open question.
