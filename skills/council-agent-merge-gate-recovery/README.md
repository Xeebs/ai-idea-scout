# Council Agent Merge-Gate & Recovery Auditor

A paste-and-go audit prompt for teams running a "council of agents" delivery pipeline — multiple AI agents independently producing competing or complementary work (PRs, drafts, analyses) against the same ticket, which a gating layer then reviews and merges as a set. It checks your merge-gate and recovery code for three specific, documented failure modes and hands back a concrete remediation plan. It does not run anything, connect to anything, or touch your repo — it only reads what you paste.

## When to use this

Use this when any of the following is true:

- One council member returned an empty response or timed out, and your pipeline logged the *entire panel* as failed even though other members actually succeeded.
- A council member merged, pushed, or finalized its output before your gate reviewed it, and the recovery/rollback afterward got confused about which member actually went wrong.
- You're about to build or adopt a council-of-agents merge gate and want a pre-flight review before these bugs show up in production.

If your setup is a single agent or a strictly sequential pipeline (not multiple agents producing work in parallel that gets merged as a set), this skill is not the right fit — it's scoped specifically to parallel council/panel delivery.

## What to hand over

**Data source: Manual.** You paste two things:

1. **Required** — the actual code or config for your merge gate and status tracking: whatever decides when the council's combined output is ready to merge, and however you currently track each member's status (a status dict, a database table, a set of flags — whatever it actually is).
2. **Optional but recommended** — a plain description of your setup (how many council seats/members, what platform you're using — e.g. GitHub PRs with check runs, a task queue, an orchestration framework's own task-state API) and, if you're auditing a specific incident, what happened: what you observed, what got logged, what state things ended up in.

Without an incident description, you'll get a pre-flight design review instead of a root-cause trace. Both are useful; the audit works either way.

## What it does

The audit checks three specific things, and only these three — it will not freelance an opinion on unrelated parts of your pipeline:

1. **Cross-seat status inference.** Does each council member have its own independently tracked status, or is there a single shared flag/counter that multiple members write to (so one member's silence or empty response can get read as "the whole panel failed" or "nothing failed yet")?
2. **Early-merge interception.** If a member merges, pushes, or finalizes its output *outside* the gate — before the gate has reviewed it — is there anything that detects that and intercepts it, or does it silently corrupt the gate's view of the pipeline?
3. **Timeout/empty-response recovery policy.** When a member times out or returns empty, is there a clear, seat-specific policy (retry that one seat, escalate to a human) — or does the ambiguity bleed into other seats' recorded status?

For each of the three, it gives you one of four verdicts, always backed by a quote from what you pasted — never a guess:

- **CONFIRMED** — the exact problematic pattern is in your pasted code, quoted.
- **LIKELY** — a structural risk exists even if it hasn't bitten you yet.
- **NOT PRESENT** — you've already handled this correctly, quoted.
- **CANNOT DETERMINE** — the pasted material doesn't cover that path; it tells you exactly what additional code or config it would need to check.

If you described a specific incident, it also traces the symptom you saw back to the specific line(s) in your code responsible for it.

Then it produces:

- A **remediation plan** — one item per CONFIRMED/LIKELY finding, naming the exact location and the specific change (before/after), never recommending a shared/aggregate status field as any part of a fix.
- A **recovery policy table** — for timeout, empty response, and detected early merge, a recommended action (retry-same-seat with a configurable count, escalate-to-human, or revert-and-requeue only that seat) plus the config knob name you'd need to expose to make it tunable.

## How to use this with any AI chat tool

Paste this whole prompt into any capable AI chat tool, then paste your merge-gate/status-tracking code or config and your setup description right after it:

> You are auditing a council-of-agents delivery pipeline (multiple AI agents independently producing work against the same ticket, gated and merged as a set) for exactly three failure modes: (1) cross-seat status inference — one member's status being read as representative of or overwriting another's; (2) unintercepted early/out-of-band merges — a member finalizing before the gate reviews it, with no detection; (3) ambiguous timeout/empty-response recovery — no clear per-seat policy for what happens when a member times out or returns nothing.
>
> I will paste my merge-gate/status-tracking code or config below, plus a description of my setup and (optionally) a specific incident.
>
> For each of the three failure modes, give me a verdict of CONFIRMED (quote the exact problematic snippet), LIKELY (structural risk, explain why), NOT PRESENT (quote the protective pattern already in place), or CANNOT DETERMINE (say what additional code you'd need to see). Do not guess at code I haven't shown you.
>
> If I described an incident, trace it back to the specific line(s) responsible for exactly one of the three failure modes.
>
> Then give me: (a) a remediation plan — one item per CONFIRMED/LIKELY finding, with the exact location, a quoted "before," and an "after" sketch, never recommending a shared/aggregate status field as part of any fix; (b) a recovery policy table for timeout / empty response / detected early merge, each with a recommended action (retry-same-seat with a configurable count, escalate-to-human, or revert-and-requeue only that one seat) and a config knob name.
>
> If reverting an early merge on a shared branch is part of the remediation, explicitly flag that this is a real git operation with real risk, not a sandboxed rollback. If my framework collapses all seats into one aggregate response before this code even runs, tell me plainly that the fix needs upstream instrumentation, not just gate-logic changes — don't propose a fix that can't work given that constraint. Stay scoped to these three failure modes only; if I ask about something else in my pipeline, say it's out of scope for this audit.
>
> Here is my code/config and setup description:
> [paste here]

## What this will not do

- It will not connect to your repo, CI system, or orchestration framework — everything it knows comes from what you paste.
- It will not execute, test, or apply any remediation — it hands you a plan, you implement it.
- It will not invent findings about code you didn't show it — anything it can't verify from your paste comes back as CANNOT DETERMINE, not a guess.
- It will not expand scope beyond the three named failure modes.
