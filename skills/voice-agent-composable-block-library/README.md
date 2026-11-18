# Voice-Agent Call-Flow Requirements Mapper

A paste-into-any-AI-chat-tool prompt for freelance and small-agency builders who set up voice AI agents (Vapi, Retell, Pipecat, LiveKit Agents, Bland, or similar) for clients. Use it right after a scoping call or intake form, before you write a single line of agent config, to turn the client's raw description into a structured flow design built from a fixed library of 4 reusable call-flow blocks.

## When to use this

You've just scoped a new voice-agent client — a scoping call, a filled-out intake form, or notes from a meeting — and you need to turn what they told you into a concrete flow design: which standard call-flow pattern(s) apply, what needs to be filled in for this specific client, and what's genuinely custom and not covered by a standard pattern. This is the drafting step between "we talked to the client" and "we're building the assistant."

## What this does not do

This does not connect to Vapi, Retell, Pipecat, or any other platform. It does not create, configure, or push a live assistant anywhere. It only works from text you paste in and produces a design document you (or a compiler tool, if you have one) use to actually build the agent.

## What to hand it

Paste one or more of:
- Your scoping-call notes
- A completed client intake form's answers
- A transcript excerpt of the scoping call

Minimum useful input: a few sentences to a few paragraphs describing the business, what callers typically need, and anything said about hours, booking systems, or how/when calls should hand off to a human. The more detail you give it, the fewer gaps it has to flag.

## The 4 canonical blocks

This prompt always maps against exactly these 4 blocks — it never invents a 5th:

1. **Scheduling** — appointment booking with a calendar-check. Slots: services offered, business hours, booking lead time/rules, calendar system (if named), confirmation method.
2. **Lead qualification** — Q&A to score and route a prospect. Slots: qualifying questions, disqualifying criteria, routing destination for qualified vs. unqualified leads.
3. **Intake/triage** — structured info-gathering before a human takes over. Slots: required fields to collect, triage/priority criteria, handoff trigger and destination.
4. **Voicemail-to-callback** — capture a message and queue a callback. Slots: information to capture, callback SLA/window, who gets notified.

Any caller need the client describes that doesn't fit one of these 4 is flagged as a **custom block gap**, not force-fit into the nearest one.

## The exact prompt

Paste this whole block into your AI chat tool, then paste your scoping notes/intake form/transcript right after it:

```
You are mapping a voice-agent client's requirements onto a fixed library of 4 reusable call-flow blocks, so I can configure their voice agent efficiently instead of designing the flow logic from scratch.

The 4 canonical blocks — never introduce a 5th, never rename these:
1. Scheduling (appointment booking + calendar-check). Slots: services offered, business hours, booking lead time/rules, calendar system, confirmation method.
2. Lead qualification (Q&A to score/route a prospect). Slots: qualifying questions, disqualifying criteria, routing destination for qualified vs. unqualified leads.
3. Intake/triage (structured info-gathering before human takeover). Slots: required fields, triage/priority criteria, handoff trigger and destination.
4. Voicemail-to-callback (capture message, queue callback). Slots: information to capture, callback SLA/window, who gets notified.

Do this:
1. Segment my pasted notes into the distinct caller needs the client described (there are often 2-4 in one scoping session).
2. Match each segment to the nearest block, or to more than one if it's a multi-step flow (e.g. triage then schedule).
3. For each matched block, draft the slot-fill values using ONLY what my text actually says. If a required slot has no supporting text, write "NEEDS CLIENT INPUT" for it — never invent business hours, pricing, services, phone numbers, or escalation contacts.
4. Flag any segment that matches none of the 4 blocks as "CUSTOM BLOCK NEEDED" with a one-line description of what it would have to do.
5. Sequence the matched blocks into a simple flow map (e.g. greeting -> intent split -> Block A or Block B -> confirmation/handoff).
6. Flag anything safety-critical (medical symptoms, crisis/self-harm mentions, legal deadlines, emergency dispatch) as needing human/clinical/legal review — do not draft autonomous triage decision logic for these, just flag them as an open question.
7. List every NEEDS CLIENT INPUT slot and safety flag as a direct, answerable question I can send back to the client.

Output format, exactly these sections in this order:

## Call Flow Summary
A table: Segment (client's need) | Matched Block | Confidence (High/Med/Low) | Slots filled | Slots missing

## Flow Map
A short ordered/branching sequence of the matched blocks.

## Slot Fill-In Drafts
One subsection per matched block, named "### <Block name> — for "<segment>"", listing each slot and its drafted value or NEEDS CLIENT INPUT.

## Custom Block Gaps
One bullet per unmatched segment with the needed behavior in one line. Omit this section if there are none.

## Open Questions for the Client
One bullet per NEEDS CLIENT INPUT slot and per safety-critical flag, phrased as a direct question.

If my pasted text describes fewer than 2 distinct caller needs, say so plainly instead of padding the table with invented segments.

Here are my scoping notes / intake form answers / transcript:

<PASTE YOUR NOTES HERE>
```

## What you get back

A single markdown report with the 5 sections above: a summary table of which block matched which client need, a flow map, ready-to-use slot drafts for each matched block, any gaps that need a custom block built, and a list of exactly what to ask the client before you can finish the config. Hand the slot drafts to whoever (or whatever compiler) actually builds the Vapi/Retell/Pipecat/LiveKit assistant.

## Guardrails this prompt enforces

- It will never make up business hours, pricing, services, phone numbers, or escalation contacts — anything not in your notes comes back as `NEEDS CLIENT INPUT`, not a guess.
- It will never invent a 5th block or rename the 4 — a real gap becomes a `CUSTOM BLOCK NEEDED` flag instead.
- It will never claim to have built or configured anything live — the output is a design document, not a working assistant.
- It will refuse to draft autonomous medical/legal/emergency triage logic and will flag those for human review instead.
