# Household Memory-Partition Designer

A paste-into-any-AI-chat-tool prompt that drafts a privacy/visibility scheme for a shared household AI assistant — before anyone writes access-control code or picks a memory backend (Mem0, Letta, Zep, or a custom store).

## When to use this
Use it when you (or a team you're advising) are building, configuring, or auditing an AI assistant meant to serve a whole household — a family smart-speaker skill, a shared household chatbot, any agent with persistent memory that multiple people talk to. The problem it solves: without a deliberate design, these assistants either blend everyone's input into one undifferentiated memory (a teen's search history or a partner's private chat can surface to the rest of the household) or force everyone onto fully separate assistants, losing the shared convenience the household wanted in the first place. This produces the middle path on paper: which content categories are shared by default, which are private, who (if anyone) can override that, what events change a category's visibility over time, and exactly what happens to someone's data when they leave the household.

It is not a code generator and not legal advice. It produces a design document a household or product team reviews and approves; actual enforcement (the code that reads/writes a memory backend respecting this scheme) is separate work.

## What you need to provide
This is a manual, conversational skill — there is no live data connection. You type the following directly into the chat:

1. **Household roster**: every member's name/handle and role — admin (sets policy, typically a parent or lease-holder), adult member, minor/teen, guest, or any custom role your household uses. Say which roles (if any) have override access to see other members' normally-private content.
2. **Content categories the assistant handles**: a short list is enough — e.g. voice chat transcripts, calendar/scheduling, grocery lists, search queries, financial/billing reminders, health reminders, messages drafted to third parties, location data.
3. *(Optional)* **Existing house rules**: anything already decided, e.g. "no one's search history is ever visible to anyone else" or "the lease-holder can see billing only."
4. *(Optional)* **Memory backend** in use or planned (Mem0, Letta, Zep, custom, or "not decided") — only affects whether you get a short backend-tagging note at the end.

If you don't give a roster or content list, the assistant running this prompt should ask you for them before drafting anything — a scheme with no named people or content categories isn't usable.

## The prompt

Paste this into your AI tool of choice, filling in your own household details where marked:

```
You are a household memory-partition designer. I'm building/configuring/auditing a shared AI assistant for my household and need a privacy/visibility design before any backend gets wired up.

Household roster:
<list each member: name/handle, role (admin/adult/teen/guest/custom), and whether their role has override access to others' private content>

Content categories the assistant will handle:
<list: e.g. voice chat transcripts, calendar, grocery lists, search queries, financial reminders, health reminders, messages to third parties, location data>

Existing house rules (if any):
<anything already decided, or "none yet">

Memory backend (if decided):
<Mem0 / Letta / Zep / custom / not decided>

Do the following:
1. Build a role table: every member, their role, and their override/admin access (if any).
2. For every content category I listed, classify its default visibility as SHARED (whole household), PRIVATE (owner only, plus admins if my house rules say so), or CONDITIONAL (a specific subset, or visible only after a trigger event). Give a one-line reason for each — never classify a category without saying why, and never skip a category I named.
3. Write override rules: for each role with override access, state exactly what it can see and under what condition (always, or only after a trigger) — default to the narrowest override that fits what I described, not "admin sees everything" unless I said that.
4. Define reclassification triggers: concrete events that change a category's or specific record's visibility over time (e.g. "a gift purchase stays private until the gift date passes, then becomes shared," "financial reminders become private to a member once they turn 18"). Every trigger needs a named event and the visibility change it causes.
5. Write a departure-removal checklist: the exact ordered steps for when a member leaves — identify every record tagged to them, decide the fate of anything they co-created with people still in the household (full purge vs. redact-their-identity-and-keep-the-shared-part — state which and why), remove them from the role table, verify zero records remain attributable solely to them, and log that removal happened.
6. Flag any ethically or legally loaded call (most commonly a minor's privacy vs. a parent's access expectations, or what happens to co-owned content on departure) as an open flag with both sides stated in one line each — don't resolve it silently, and note this isn't legal advice.
7. Before giving me the final answer, check: every category I listed appears exactly once in the visibility table, every roster member appears in the role table, and the departure checklist has a concrete step for shared/co-owned content, not just private content. Fix anything that fails before answering.

Output format:
# Household Memory-Partition Scheme — <household name>
## Role Table (table: Member | Role | Override/Admin Access)
## Content Visibility (table: Category | Default Visibility | Reasoning)
## Override Rules (bullet list)
## Reclassification Triggers (table: Trigger Event | Category/Record Affected | Visibility Change)
## Departure-Removal Checklist (numbered steps)
## Open Flags — Needs Human Decision (bullet list, note this isn't legal advice)
## Backend Note (only if I named a backend — one short paragraph on how to encode owner tag + visibility label as metadata, no code)

Guardrails: never leave a category unclassified or unexplained; never resolve a minor's-privacy-vs-parent's-access tension or similar conflict yourself — always flag it; never claim this is legally compliant or already enforced — it's an unimplemented draft; never write or imply actual access-control code; never invent a member, role, or category I didn't give you.
```

## What you get back
A structured markdown document with six sections (seven if you named a backend): a role table, a content-visibility table with reasoning, override rules, a reclassification-trigger table, a numbered departure-removal checklist, and an open-flags section for anything ethically or legally loaded that the tool declined to resolve on its own. Treat it as a first draft for the household and/or product team to review — not a finished privacy policy and not working code.

## Guardrails (what this will refuse to do)
- It won't silently decide a minor's privacy should yield to a parent's access (or the reverse) — it surfaces that as an open question every time, because real families and real products disagree on this and a design tool shouldn't pretend there's one right answer.
- It won't tell you the scheme is legally compliant or already protects anyone — it's an unimplemented draft that needs human review and, for anything consumer-facing, real legal input.
- It won't write the actual enforcement code — that's separate infrastructure work (a middleware layer in front of your memory backend), not this design step.
- It won't invent household members or content categories you didn't mention just to make the output look fuller.
