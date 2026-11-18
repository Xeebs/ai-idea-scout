# Ripple Check — Cross-Project Impact Flag

A copy-paste prompt for any AI chat tool (Claude, ChatGPT, etc.) that checks whether a change you just made in one project might quietly break or affect an open task in one of your *other* concurrent projects — the ones you're not currently looking at.

## Who this is for

Freelancers, contractors, and small dev shops (2-10 people) who run CLI coding agents (Claude Code, Cursor, Codex) across multiple concurrent client engagements at once. The specific failure this catches: you change something in Project A — deprecate a field, switch a pagination style, rename an endpoint — and three days later you (or a teammate) start a task in Project B that silently assumed the old behavior. Nothing today flags that automatically unless you remember it yourself.

This is the manual, install-nothing version of that check. There's no daemon, no persistent memory, no code reading your repos — you paste what changed and your task lists, and it tells you what to double-check.

## What you need before you start

1. **The change** — a one-to-three-sentence description of what you just did, or the actual diff. Be concrete: name the field, endpoint, convention, or dependency that changed, and what the old vs. new behavior is. "Fixed a bug" is not enough; "switched the /products endpoint from offset pagination (`page`/`limit`) to cursor pagination (`cursor`/`limit`), old params still work for 30 days" is.
2. **One or more open task lists** — whatever you already keep (a TASKS.md, a backlog doc, a sticky-note list), each one labeled with the project or client it belongs to.
3. **(Optional, but makes the check sharper)** — a note on which of these projects, if any, actually share a system, library, vendor API, or database with the one you just changed. Without this, the check will correctly refuse to connect two projects just because their tasks use similar words.

**Important on data**: everything here is pasted by you. Nothing is read from your filesystem, your git history, or any API — if you want the always-on version that watches your repos directly, that's a separate project (not this skill) and doesn't exist as a ready-made tool yet.

## The prompt

Paste this into your AI tool, filling in the bracketed parts:

```
I need a Ripple Check: tell me which of my open tasks below might be affected by a change I just made, across one or more of my concurrent projects.

THE CHANGE:
[describe what you changed, concretely — the field/endpoint/convention, old behavior vs. new behavior]

SHARED SYSTEMS (optional — tell me if any of these projects share a library, vendor API, or database with the one I just changed; otherwise assume they don't):
[e.g., "Project B and the changed project both call the same internal Billing API" — or write "none that I know of"]

TASK LIST — [Project/Client A name]:
- [task 1]
- [task 2]
...

TASK LIST — [Project/Client B name]:
- [task 1]
- [task 2]
...

(add more TASK LIST blocks as needed)

Now do this:
1. Restate my change as one concrete technical fact, and list the exact things (field names, endpoint names, conventions) another task could depend on.
2. Go through every task in every list, one at a time. For each, decide:
   - LIKELY: the task's text names or clearly implies the exact thing that changed.
   - POSSIBLE: same project as the change and touches the same area, but doesn't explicitly confirm it — OR a different project I explicitly said shares the relevant system.
   - NONE (default): no real dependency. Do NOT flag two tasks just because they use similar topic words (e.g., both mention "pagination") if they're in different projects I didn't say share a system — that's a coincidence, not a dependency.
3. Never skip a list — if nothing in a list is flagged, say so explicitly.
4. For every LIKELY/POSSIBLE flag, give one specific reason (the exact overlapping term or system) and a recommended next action (confirm with teammate / update the task / re-test after merge / ignore as false positive).
5. If any two flagged projects belong to different clients, abstract the cross-client reason so it never reveals the first client's specific field names, code, or business details to the second — just "an upstream convention changed in another engagement, worth checking."
6. End with one line noting how confident this check is given what I pasted (e.g., if I only gave task titles and not full descriptions).

Output as a short Markdown report, one section per project, flags as a bullet list under each.
```

## What you'll get back

A short report with one section per project/client you listed. Each flagged task gets a LIKELY or POSSIBLE label, a one-line concrete reason, and a suggested next action. Projects with nothing flagged say so explicitly rather than being left out. If you listed tasks across different clients, any flag that crosses that boundary is deliberately vague about the other client's specifics — that's intentional, not a missing detail.

## What this will NOT do

- It will not connect to your GitHub, your local git history, or any coding CLI's session files — it only reasons over what you paste in that one message.
- It will not flag two tasks as related just because they share a topic (pagination, auth, exports) if they're in different projects and you didn't say those projects share a system — that's the single biggest failure mode of a tool like this (alert fatigue from noisy matches), so it defaults to NONE when unsure.
- It will not remember anything between sessions. Run it again fresh each time you want a check — there's no persistent state to maintain.
