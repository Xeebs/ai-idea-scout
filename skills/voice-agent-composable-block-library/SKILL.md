---
name: voice-agent-composable-block-library
description: Maps a voice-agent client's scoping-call notes, intake form, or transcript onto a fixed library of 4 reusable call-flow blocks (scheduling, lead qualification, intake/triage, voicemail-to-callback), drafts the slot-fill values for each, flags gaps needing a custom block, and lists open questions for the client. Use when a builder has just finished scoping a new voice-agent client and needs a flow design before configuring Vapi, Retell, Pipecat, or LiveKit Agents.
---

# Voice-Agent Call-Flow Requirements Mapper

## When to use this
A freelance or small-agency voice-agent builder has just finished a scoping call, received a filled-out intake form, or has meeting notes from a prospective/new client, and needs to turn that raw description into a structured call-flow design — before writing a single line of Vapi/Retell/Pipecat/LiveKit config. This is the drafting step that happens between "we talked to the client" and "we're building the assistant."

## Inputs
**Data source**: Manual — the user pastes the client's scoping-call notes, a completed intake form's answers, or a transcript excerpt describing the client's business and how they want calls handled. (Context: the parent idea's full project — a registry/compiler that pushes assembled flows into Vapi/Retell/Pipecat via their configuration APIs — is classified Connected, since those platform APIs are mature and documented today. This skill is the separate, earlier drafting step: it never calls any platform API itself, so for this skill specifically the input is Manual. Nothing is fetched automatically.)

Minimum useful input: a few sentences to a few paragraphs naming the business type, what callers typically need, and anything the client said about hours, booking, or escalation. More detail produces fewer "NEEDS CLIENT INPUT" flags.

## Procedure
1. **Hold the fixed block taxonomy** — do not invent new block names. There are exactly 4 canonical blocks:
   - **Scheduling** (appointment booking with calendar-check): slots = services offered, business hours, booking lead time/rules, calendar system named (if any), confirmation method (SMS/email/call-back).
   - **Lead qualification** (Q&A to score/route a prospect): slots = qualifying questions, disqualifying criteria, routing destination for qualified vs. unqualified leads.
   - **Intake/triage** (structured info-gathering before a human takes over): slots = required fields to collect, triage/priority criteria, handoff trigger and destination.
   - **Voicemail-to-callback** (capture message, queue a callback): slots = information to capture, callback SLA/window, who gets notified.
2. **Segment the pasted text** into distinct caller needs/intents the client described (a client often describes 2-4 separate call types in one scoping session — e.g., "new patients book an appointment" + "existing patients ask billing questions" + "after-hours calls go to voicemail").
3. **Match each segment to the nearest block** using the signatures above. A segment can match one block, split across two blocks (e.g., triage-then-schedule), or match none.
4. **Draft the slot-fill values** for each matched block strictly from what the pasted text actually says. If a required slot for a matched block has no supporting text, write `NEEDS CLIENT INPUT` for that slot — never invent business hours, service lists, pricing, phone numbers, or escalation targets.
5. **Flag unmatched segments** as `CUSTOM BLOCK NEEDED` with a one-line description of what the new block would have to do — never force-fit a segment into one of the 4 blocks just to avoid a gap.
6. **Sequence the matched blocks** into a simple flow map showing the order a caller moves through them (e.g., greeting → intent split → Block A or Block B → confirmation/handoff).
7. **Flag anything safety-critical** (medical symptoms, mentions of self-harm/crisis, legal deadlines, emergency dispatch) in the Open Questions list as needing human/clinical/legal review before any flow logic encodes a triage decision — never draft autonomous triage logic for these.
8. **List open questions** — every `NEEDS CLIENT INPUT` slot and every ambiguity, phrased as a direct question the builder can send back to the client.

## Output format
A single markdown report with these sections, in order:

```
## Call Flow Summary
| Segment (client's need) | Matched Block | Confidence (High/Med/Low) | Slots filled | Slots missing |

## Flow Map
<ordered/branching sequence of matched blocks as a short arrow diagram or numbered list>

## Slot Fill-In Drafts
### <Block name> — for "<segment>"
- <slot>: <drafted value, or NEEDS CLIENT INPUT>
(one subsection per matched block)

## Custom Block Gaps
- <segment that matched nothing> — needed behavior: <one line>
(omit this section if none)

## Open Questions for the Client
- <one question per NEEDS CLIENT INPUT slot or safety-critical flag>
```

## Guardrails
- Never invent a slot value (hours, services, pricing, phone numbers, escalation contacts) not present in the pasted text — mark it `NEEDS CLIENT INPUT` instead.
- Never introduce a 5th block name or rename the 4 canonical blocks; a genuine gap is a `CUSTOM BLOCK NEEDED` flag, not a new ad hoc block.
- Never claim this output is a working Vapi/Retell/Pipecat/LiveKit config — it is the intermediate design artifact a human (or the separate compiler project) turns into one.
- Never draft autonomous clinical, legal, or emergency-dispatch triage logic — flag these segments for human review instead of filling in decision criteria yourself.
- If the pasted text describes fewer than 2 distinct caller needs, say so plainly rather than padding the Call Flow Summary with invented segments.
