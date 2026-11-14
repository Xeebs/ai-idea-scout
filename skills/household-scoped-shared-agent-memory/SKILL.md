---
name: household-scoped-shared-agent-memory
description: Drafts a household's memory-visibility scheme (what's shared vs. private by default, who can override, what triggers reclassification, and how to purge a departing member's data) for a shared AI assistant serving multiple people. Use when someone is designing, configuring, or auditing a household/family AI assistant's privacy model, before any memory backend gets wired up.
---

# Household Memory-Partition Designer

## When to use this
Reach for this when someone is building, configuring, or reviewing a shared AI assistant (a family smart-speaker skill, a household chatbot, a multi-person memory-enabled agent) and needs to decide, on paper, which categories of content stay private to the person who created them versus which are visible to the whole household — before writing any access-control code or picking a memory backend. Also use it to audit an existing assistant's privacy model by checking its current behavior against the scheme this produces.

Do not reach for this to write or review actual enforcement code (the access-control middleware itself is a different, infrastructure-level build) and do not reach for it to resolve real family-law or custody disputes — it drafts a design the household and product owner still have to approve, and it is not legal advice.

## Inputs
**Data source**: Manual — the user describes their household directly in the conversation; this skill does not connect to Mem0, Letta, Zep, a smart-speaker's user-ID metadata, or any other live system (the underlying memory-backend connectors are mature and already exist, but wiring into them is the separate runtime-infrastructure half of this idea, not this design-aid skill). Collect, by asking if not given:

1. **Household roster** — each member's name/handle and role: admin (sets policy, e.g. a parent or lease-holder), adult member, minor/teen, guest/visitor, or any custom role the household uses. Note which roles have override/admin read access.
2. **Content categories the assistant will handle** — e.g. voice chat transcripts, calendar/scheduling, grocery/shopping lists, search queries, financial/billing reminders, health/medication reminders, messages drafted to third parties, location data. A short list is enough; the skill will ask about any category left unclear.
3. *(Optional)* **Existing house rules or constraints** — anything already decided, e.g. "no one's search history is visible to anyone else, full stop" or "the lease-holder can see billing but nothing else."
4. *(Optional)* **The memory backend in use or planned** (Mem0, Letta, Zep, a custom store, or "not decided yet") — only changes whether the output includes a backend-specific tagging note; the scheme itself is backend-agnostic either way.

If the roster or content-category list is missing entirely, ask for it before drafting — a scheme with no named members or categories is not usable. If optional inputs are missing, proceed and note the gaps.

## Procedure
1. **Build the role table.** List every household member with their role and whether that role carries override/admin read access over other members' default-private content.
2. **Classify each named content category's default visibility** as one of: `SHARED` (visible to everyone in the household), `PRIVATE` (visible only to its owner, plus admins if the household's rules say so), or `CONDITIONAL` (visible to a specific subset, e.g. admins only, or visible until/after a trigger event). Never leave a named category unclassified — if the input doesn't make the right default obvious, state your reasoning and flag it as a judgment call the household should confirm, rather than silently picking one.
3. **Write override rules** — for each role with admin/override access, state exactly what it can see and under what condition (always, or only after a specific trigger). Default to the narrowest override that satisfies what the user described; do not grant blanket "admin sees everything" access unless the user explicitly said so.
4. **Define reclassification triggers** — concrete events that move a category or a specific record from one visibility to another (e.g., "a gift purchase stays PRIVATE until the gift date passes, then becomes SHARED," "financial reminders move from CONDITIONAL to PRIVATE for a member once they turn 18," "any record a member explicitly marks 'share with household' becomes SHARED immediately"). Every trigger must name the event and the visibility change it causes — no vague "as appropriate."
5. **Write the departure-removal checklist** — the ordered steps for when a member leaves the household: (a) identify every record tagged to that member, (b) decide the fate of records they co-created with others still in the household (full purge vs. redact-their-identity-and-keep-the-shared-part — state which the scheme uses and why), (c) remove them from the role table, (d) verify zero records remain attributable solely to them, (e) log that the removal happened and when. This checklist must be concrete enough that someone could follow it as a literal procedure, not a restatement of "remove their data."
6. **Surface every ethically or legally loaded call as an open flag instead of resolving it silently** — most commonly a minor's privacy vs. a parent's access expectations, or a departing member's co-owned content. State the competing considerations in one line each and explicitly recommend checking real family-law guidance before the household or product treats this scheme as a privacy guarantee to end users.
7. **Self-check before returning**: every content category named in the input appears in the visibility table exactly once; every role in the roster appears in the role table; the departure checklist names a concrete action for shared/co-owned content, not just private content. If any of these three checks fail, fix the output before returning it.

## Output format
```markdown
# Household Memory-Partition Scheme — <household name/label>

## Role Table
| Member | Role | Override/Admin Access |
|---|---|---|

## Content Visibility
| Category | Default Visibility | Reasoning |
|---|---|---|

## Override Rules
- <role>: can see <what>, <always | only after trigger X>

## Reclassification Triggers
| Trigger Event | Category/Record Affected | Visibility Change |
|---|---|---|

## Departure-Removal Checklist
1. ...
2. ...

## Open Flags — Needs Human Decision
- <competing considerations in one line> — not legal advice; confirm against real family-law guidance before relying on this as a privacy guarantee.

## Backend Note (only if a backend was named)
<how to encode owner tag + visibility label as metadata fields in Mem0/Letta/Zep/custom, in one short paragraph — not implementation code>
```

## Guardrails
- Never leave a named content category unclassified, and never classify one without a stated reason — "it felt private" is not a reason; tie it to what the user said about the household or the category itself.
- Never resolve a minor's-privacy-vs-parent's-access tension (or any similar real conflict) unilaterally — always surface it as an open flag with both sides stated, never a silent default.
- Never present this scheme as legally compliant, enforced, or a finished privacy guarantee — it is an unimplemented design draft; say so explicitly every time it's produced.
- Never write or imply working access-control code, SQL, or API calls — if asked to also implement enforcement, say that is the separate runtime-infrastructure half of this idea and out of scope for this design aid.
- Never invent a household member, role, or content category not given by the user to pad the output — if the input is thin, produce a thin, honest scheme and ask follow-up questions instead of guessing to fill rows.
