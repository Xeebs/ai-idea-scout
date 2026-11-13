# Delegation Chain Scope & Failure Auditor

A paste-into-any-chat-tool prompt that audits a multi-agent system's delegation code for two specific, mechanical gaps: places where a subagent/child session silently inherits full authorization scope instead of being narrowed, and places where a child's failure or scope violation has no path back to the parent. It does not run anything, call any API, or read live logs — it only reads the source code you paste in, once.

## When to use this

Use this right before shipping a delegation-heavy agent system (anything where a parent agent spawns subagents, child sessions, or child graph nodes — OpenCode-style subagent tool calls, Claude Code subagent configs plus their spawning harness, LangGraph nodes that transition into child graphs, or a custom `delegate()`/`spawn_child_session()` helper), or right after an incident where a subagent did something outside its intended scope, or silently failed, and nobody noticed until the parent's output was already wrong. The question this answers: "where in this code does a subagent get more trust than it should, and where would its failure go unnoticed?"

This is a one-time code review, not a monitor. If what you actually need is something that watches delegation in production continuously and alerts in real time, you need a tracing middleware wired into your framework's own session API — a different, bigger piece of infrastructure than this prompt. This skill tells you where that middleware would need to attach; it doesn't replace it.

## What to hand over

**Data source: Manual.** Paste the actual delegation/orchestration source code:
- Every function, class, or config block that spawns a subagent, child session, child task, or child graph node.
- Whatever code constructs or passes credentials, tokens, or permission/scope objects to that child (if any exists).
- Whatever code receives the child's result or exception back in the parent — the error handling, result merging, or logging around the call.

Do not paste live session logs or transcripts instead of code — this prompt audits what the delegation code *does*, not a record of what happened in one run. If you only have logs, say so and this prompt will ask for the source instead.

If you don't have an explicit scope-narrowing step in your code at all today, that's fine — paste what you have; "no scope handling exists" is itself a valid, reportable finding, not a reason to withhold the audit.

## What happens

1. **Every delegation call site in the pasted code gets inventoried** — each place a child agent/session/task is created.
2. **Each call site is classified on two independent axes:**
   - *Scope handling*: `EXPLICIT_NARROW` (a genuinely narrower credential is built for the child before it's invoked), `IMPLICIT_INHERIT` (the child gets the parent's same token/session unmodified), `NO_SCOPE_PASSED` (no credential is passed at all — ambient/default permissions), or `UNCLEAR` (can't be determined from what was pasted).
   - *Failure handling*: `PROPAGATED` (a child failure or scope violation is distinguishably surfaced to the parent — re-raised, correlated in a log, fed to an alert, or branches parent control flow), `ISOLATED` (caught and swallowed, or merged into parent state with no status check), or `NONE` (no handling at all).
3. **Each call site gets a severity**, computed mechanically from those two classifications — never from a gut feel about how likely the gap is to matter:
   - **HIGH**: scope is inherited or missing *and* failure is isolated or unhandled — the worst case, a silent double blind spot.
   - **MEDIUM**: only one axis is unhealthy.
   - **LOW**: either axis came back `UNCLEAR` — flagged for you to confirm, never silently resolved either way.
   - **Healthy**: explicit narrowing *and* propagated failure handling — no finding, just noted as already correct.
4. **Every HIGH/MEDIUM/LOW finding gets a specific remediation** naming the exact call site and the exact change — never a generic "add error handling."

## Output you get

A report with, in this order:
1. A verdict line: how many call sites were audited, and the HIGH/MEDIUM/LOW/healthy breakdown (or `NO_DELEGATION_FOUND` if the pasted code had no delegation in it).
2. A findings table (HIGH first): `ID | Call Site | Scope Handling | Failure Handling | Severity | Remediation`.
3. A short list of which call sites are already healthy, so you know what not to touch.
4. A closing note restating that this is a one-time read of the code you pasted — it can't see runtime scope changes, config outside what you gave it, or anything that happens only at execution time, and it is not a substitute for an always-on tracing/observability layer if that's what you actually need.

## Copy-paste prompt

```
You are auditing a multi-agent system's delegation code for two specific gaps: (1) call sites where a
subagent/child session implicitly inherits full authorization scope instead of being explicitly narrowed,
and (2) call sites where a child's failure or scope violation has no path back to the parent's error
handling or observability. This is a one-time code review of what I paste below — you are not running
anything, calling any API, or reading live logs.

Here is the delegation/orchestration code (every place a subagent/child session/child task/child graph
node is spawned, any credential/scope-passing logic, and any code that receives the child's result or
exception back in the parent):

<PASTE CODE HERE>

Do this:
1. Inventory every delegation call site in the code above.
2. For each, classify scope handling as EXPLICIT_NARROW (a genuinely narrower credential is built for the
   child before invocation), IMPLICIT_INHERIT (child gets the parent's same token/session unmodified),
   NO_SCOPE_PASSED (no credential passed at all), or UNCLEAR (can't tell from this code — say what else
   you'd need to see).
3. For each, classify failure handling as PROPAGATED (a child failure/violation is distinguishably surfaced
   to the parent), ISOLATED (caught/swallowed or merged without a status check), or NONE (no handling).
4. Score each call site: HIGH if scope is inherited/missing AND failure is isolated/unhandled; MEDIUM if
   only one axis is unhealthy; LOW if either axis is UNCLEAR; otherwise mark it healthy. Never downgrade a
   HIGH because the gap "seems unlikely" — severity is mechanical, not a judgment call.
5. For every HIGH/MEDIUM/LOW finding, write a specific remediation naming the exact call site and the exact
   change — not generic advice.
6. Output: a verdict line (call sites audited, HIGH/MEDIUM/LOW/healthy counts, or NO_DELEGATION_FOUND if
   none exist), a findings table (HIGH first) with columns ID | Call Site | Scope Handling | Failure
   Handling | Severity | Remediation, a one-line list of healthy call sites, and a closing note that this
   is a one-time read of the pasted code only — not a live monitor.

Never invent a call site, file, or line number not present in the code I pasted. Never classify something
EXPLICIT_NARROW just because a variable is named "scope" or "token" — verify it's actually narrowed. Never
resolve an UNCLEAR by guessing; report it as LOW and say what you'd need to confirm it.
```
