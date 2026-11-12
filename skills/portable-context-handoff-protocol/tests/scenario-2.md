# Scenario 2 — Thin input, no existing context file, three-tool team workflow

## Input

> I'm switching between AI coding tools on the same project and want a portable context bundle so I stop re-explaining myself to each one.
>
> Project: a new "notification preferences" feature for our React Native app — letting users mute specific notification categories. Just started this week.
>
> Tools I switch between: I brainstorm architecture with ChatGPT, then implement in Claude Code, and occasionally my teammate reviews in Cursor. Render for: all three.
>
> Here's my existing context — I don't have a CLAUDE.md or rules file for this feature yet, it's brand new. The app overall uses React Native, Redux, and Firebase Cloud Messaging for push notifications, if that helps.
>
> Recent decisions, open threads, and anything tried and abandoned:
> Honestly not much yet — we talked through a rough idea in a ChatGPT session yesterday about storing preferences as a bitmask in Firestore, but didn't finalize it. That's really all I've got right now.
>
> Please do the same thing as before: five sections, mark unknowns, render for all three tools, note staleness and what's missing.

## Pass criteria

- [ ] Produces a canonical bundle with all five sections present, even though input is thin — does not refuse or ask the user to come back with more before producing anything.
- [ ] Architecture Summary correctly includes React Native, Redux, and Firebase Cloud Messaging (the only concrete facts given) and does not invent additional stack details (e.g., does not assert a specific backend framework that was never mentioned).
- [ ] Recent Decisions section reflects that nothing is actually decided yet — the bitmask-in-Firestore idea is marked as discussed/tentative, not written as a finalized decision, since the input explicitly says "didn't finalize it."
- [ ] Open Threads includes the bitmask-vs-alternative storage question as unresolved.
- [ ] Rejected Approaches and File/Component State are marked `UNKNOWN — not provided` (or equivalent) rather than fabricated, since the input gives nothing for either.
- [ ] Produces three labeled adapter blocks (Claude Code / CLAUDE.md, Cursor / AGENTS.md or .cursorrules, generic/ChatGPT) since the user asked for "all three."
- [ ] The generic/ChatGPT adapter is phrased as prose suitable for a custom-instructions box, not just a copy of the markdown bundle.
- [ ] Ends with both a staleness recommendation and an explicit list of what's missing (e.g., "no rejected approaches recorded yet, no file/component state yet — bring these once the feature has more history").
- [ ] Does not pad thin input with generic, made-up architecture or decision content to make the bundle look more complete than it is.
