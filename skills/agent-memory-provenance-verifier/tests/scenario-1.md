# Scenario 1 — Support agent's claimed memory about a refund preference

## Context

A SaaS company's support agent (built on a memory-enabled framework) resolved a billing ticket last week. This week, a different customer reopened a related thread, and the agent's memory log surfaced this claim when asked to recall the prior interaction. A support lead wants to know whether to trust it before acting on it again.

## Inputs provided to the skill

**1. Memory claim (verbatim):**
"I remember the customer, Alex Rivera, confirmed their account email as alex.rivera@northstar-labs.com, and that they explicitly asked for a refund rather than a replacement device, and that they mentioned they'd be traveling next week so couldn't test a replacement anyway."

**2. Trace/transcript excerpt (chat log, session `sup-8841`, 2026-11-05):**
```
[14:02:10] USER: Hi, following up on my broken headset order #55291.
[14:02:40] USER: My account email is alex.rivera@northstar-labs.com in case you need it.
[14:03:15] AGENT: Thanks Alex, I see the order. I'm sorry about the headset. Would you like
            a replacement or a refund?
[14:03:50] USER: Honestly either is fine, whichever is faster for your team.
[14:04:10] AGENT: A refund is usually faster on our end since it skips a reshipment step.
            I'll process that now.
[14:04:30] USER: Sounds good, thanks.
```

(This is the full retained transcript for session `sup-8841`; no other log segments exist for this session.)

## Expected output (pass/fail checklist)

- [ ] Splits the compound claim into at least three separate assertions: (a) email is alex.rivera@northstar-labs.com, (b) customer explicitly asked for a refund rather than a replacement, (c) customer mentioned traveling next week.
- [ ] Assertion (a) scored SUPPORTED, citing the 14:02:40 line verbatim.
- [ ] Assertion (b) scored UNSUPPORTED or CONTRADICTED — not SUPPORTED — because the transcript shows the customer said "either is fine, whichever is faster" and it was the *agent*, not the customer, who chose the refund path. The skill must catch that the claim misattributes the agent's own decision to the customer's explicit request.
- [ ] Assertion (c) scored UNSUPPORTED — nothing in the transcript mentions travel next week.
- [ ] Overall verdict is CONTRADICTED (because of (b)'s misattribution) or at minimum PARTIALLY SUPPORTED with (b) flagged as a serious misrepresentation — must not be SUPPORTED or PARTIALLY SUPPORTED-with-no-caveat.
- [ ] Explicitly calls out that a real, relevant segment exists (the refund/replacement exchange) but is being mischaracterized — the "real citation, wrong content" failure mode from the procedure.
- [ ] Does not fabricate any transcript line not present above (e.g. does not invent a line where the customer explicitly requests a refund).
- [ ] Caveats section notes this is the full available transcript (not that it's incomplete) — should not invent a trace-gap excuse for assertion (c)'s absence when the transcript is in fact complete per the problem statement.

## Pass criteria

Passes if all of the first six boxes are checked (the misattribution catch on assertion (b) and the correct overall verdict are non-negotiable) and no fabricated transcript content appears anywhere in the output.
