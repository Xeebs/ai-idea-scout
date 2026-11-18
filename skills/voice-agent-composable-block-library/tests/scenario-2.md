# Scenario 2 — Home-services (plumbing/HVAC) intake form

## Input (paste this as the client's filled-out intake form)

```
Intake form — Northside Plumbing & HVAC

1. What should the agent do for a caller who wants a quote on a new
   job (e.g. water heater replacement, AC install)?
   -> Ask what kind of job it is, square footage/number of units if
      HVAC, and whether it's urgent. Qualify: we only do residential,
      not commercial. If commercial, tell them we don't service that
      and end the call politely. If residential, pass the details to
      the sales team, who calls back same day.

2. What about an existing customer with no heat/no AC or a leaking
   pipe right now?
   -> This is urgent dispatch. Collect address, callback number, and
      a one-line description of the problem. Do NOT ask them to
      self-diagnose or decide severity — just get a technician
      dispatched same-day. We have an on-call tech between 7am-9pm;
      outside that window, take the message and call back at 7am.

3. Anything else callers commonly ask for?
   -> Yes — a lot of callers ask to leave a Google review right there
      on the phone, or ask us to text them a link to leave one. We'd
      like the agent to offer to text a review link at the end of any
      call where the issue got resolved or a job got booked.

4. Business hours / booking system?
   -> Office is open 8am-6pm Mon-Sat. We use Jobber for scheduling but
      haven't set up API access for the voice agent yet.
```

## Pass criteria

- [ ] Output has the 5 sections in order, matching the SKILL.md format.
- [ ] Segment 1 (new job quote) maps to **Lead qualification**, with qualifying question (job type, sq ft/units, urgency), disqualifying criterion (commercial = disqualified, scripted decline), and routing destination (sales team, same-day callback) all filled from the text.
- [ ] Segment 2 (no heat/leak dispatch) maps to **Intake/triage**, with required fields (address, callback number, one-line problem description), explicit instruction that the agent must NOT perform symptom severity triage itself, and a time-conditioned handoff (on-call tech 7am-9pm vs. callback at 7am otherwise) captured correctly.
- [ ] The review-link request (segment 3) is flagged as **CUSTOM BLOCK NEEDED** — it does not fit Scheduling, Lead qualification, Intake/triage, or Voicemail-to-callback, and the output must not force-fit it into one of the 4 (e.g. must not mislabel it as part of Scheduling's "confirmation method" slot).
- [ ] Business hours (8am-6pm Mon-Sat) and the note that Jobber has no live API access yet are reflected in the Scheduling-adjacent context or Open Questions — not invented with different hours.
- [ ] No fabricated details: no invented technician names, no invented dispatch radius/service area, no invented pricing.
- [ ] Open Questions includes at least: whether/how the review-link offer should be implemented (since it's the flagged custom block) and any slot not covered by the form (e.g. whether there's an after-hours voicemail path for non-urgent calls outside 8am-6pm, which the form never actually states).

## Fail conditions

- Drafts specific severity-triage criteria for segment 2 (e.g. deciding what counts as an emergency) instead of preserving the client's explicit "don't ask them to self-diagnose" instruction.
- Silently drops or misfiles the review-link request instead of flagging it as a custom block gap.
- Invents a service area, technician roster, or pricing not present in the form.
