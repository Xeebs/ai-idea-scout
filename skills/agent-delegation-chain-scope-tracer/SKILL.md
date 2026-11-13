---
name: agent-delegation-chain-scope-tracer
description: Audits a multi-agent system's delegation/subagent-spawning code to find every call site where a child session implicitly inherits authorization scope instead of being explicitly narrowed, and every call site where a child's failure or scope violation has no path back to the parent. Use before shipping a delegation-heavy agent system, during an incident review after a subagent did something it shouldn't have, or when a maintainer asks "can my parent agent actually tell when a subagent exceeded its scope or failed silently."
---

# Delegation Chain Scope & Failure Auditor

## When to use this
Use this when someone hands over the source code of a multi-agent orchestrator (OpenCode-style subagent tool calls, Claude Code subagent configs plus the spawning harness around them, a LangGraph graph definition, or a custom delegation layer) and asks a question shaped like: "where in this code does a subagent get more trust than it should," "would we even notice if a child session silently exceeded scope or failed partway," or "audit our delegation chain before we ship this." This is a one-shot, point-in-time code review — it reads the delegation call sites as written today and reports what they do, not a continuously running monitor. If the user wants ongoing, always-on detection of scope drift and failure propagation at runtime, that is a different, infrastructure-shaped project (a tracing middleware living inside the framework's delegation path with its own session store) — tell them so explicitly rather than implying this audit provides that.

## Inputs
**Data source**: Manual — the user pastes or uploads the orchestration/delegation source code itself: every function, class, or config block that spawns a subagent or child session (e.g., a `Task`/subagent tool-call wrapper, an OpenCode subagent invocation layer, a LangGraph node that transitions into a child graph, a custom `delegate()`/`spawn_child_session()` helper), plus whatever code receives that child's result or exception back in the parent. The parent idea classifies the *continuously-running tracing middleware* (the PROJECT half of this BOTH-format idea) as Connected — it reads live session/delegation logs through the agent framework's own session API (e.g., OpenCode's session store, Claude Code subagent transcripts, LangGraph checkpoint state). This skill is the different, one-shot half: it never reads a live session log or calls any framework API itself — it only reads the delegation *code* the user pastes in. If the user instead pastes raw session logs/transcripts with no delegation code, say that this skill audits code, not logs, and ask for the spawning/handling source instead.

If the pasted input contains no delegation/subagent-spawning code at all, say so explicitly and stop — never fabricate call sites to have something to report on.

## Procedure
1. **Inventory every delegation call site.** Scan the pasted code for every place a subagent, child session, child task, or child graph node is created or invoked. Record each as `(call site ID, file/function name or best-guess location, one-line description of what it delegates)`.
2. **Classify each call site's scope handling:**
   - `EXPLICIT_NARROW` — the code constructs a new credential, token, or permission set for the child that is demonstrably narrower than (or explicitly derived with restriction from) what the parent holds, before the child is invoked.
   - `IMPLICIT_INHERIT` — the child is invoked with the parent's same credential/token/session context, unmodified, with no narrowing step.
   - `NO_SCOPE_PASSED` — no credential, token, or scope object is passed or referenced at all; the child presumably runs with ambient/default permissions.
   - `UNCLEAR` — the scope-passing logic exists elsewhere (e.g., a framework default, an external config) and cannot be determined from the pasted code alone. Never guess; mark `UNCLEAR` and say what additional file would resolve it.
3. **Classify each call site's failure/violation handling:**
   - `PROPAGATED` — a child's exception, non-zero/failure result, or scope-violation signal is surfaced to the parent's control flow in a way that is distinguishable from a normal success (re-raised, logged with a parent-child correlation ID, fed into an alert/observability call, or causes the parent to branch).
   - `ISOLATED` — the child's failure is caught and swallowed (e.g., a bare `except: pass`, a result that's merged into parent state without a status check, a log line with no correlation back to the parent run).
   - `NONE` — there is no failure handling at all around the call site; an exception would propagate unhandled or the result is used without any check.
4. **Score each call site:**
   - `HIGH` — (`IMPLICIT_INHERIT` or `NO_SCOPE_PASSED`) AND (`ISOLATED` or `NONE`). This is the worst case named in the source evidence: a child that could exceed scope *and* whose failure would never surface — a silent, double-blind spot.
   - `MEDIUM` — exactly one half is unhealthy: either scope is inherited/missing but failure handling is `PROPAGATED`, or scope is `EXPLICIT_NARROW` but failure handling is `ISOLATED`/`NONE`.
   - `LOW` — either axis is `UNCLEAR`. Flag for human confirmation; never resolve the ambiguity yourself by assuming healthy or unhealthy.
   - No finding — `EXPLICIT_NARROW` AND `PROPAGATED`. State this call site is healthy; do not pad the findings table with it beyond a one-line mention in the summary.
5. **Write a remediation for every finding** (HIGH, MEDIUM, LOW), stated as the specific change at that call site: e.g., "before invoking `spawn_subagent()` at line 42, construct a scoped credential narrower than `parent_token` and pass that instead" or "wrap the call at line 88 so a non-success result from the child is re-raised or logged with the parent's run ID, not merged silently into `state['result']`." Never give a generic "add error handling" remediation — name the call site and the specific gap.
6. **Compute the overall verdict**: count of call sites audited, count HIGH/MEDIUM/LOW, count healthy. If zero call sites were found, the verdict is `NO_DELEGATION_FOUND`, not a clean pass.

## Output format
A markdown report, in this order:
1. **Verdict line**: `<N> call sites audited — <h> HIGH, <m> MEDIUM, <l> LOW, <healthy> healthy` (or `NO_DELEGATION_FOUND`).
2. **Findings table**: columns `ID | Call Site (location) | Scope Handling | Failure Handling | Severity | Remediation`. HIGH first, then MEDIUM, then LOW. Omit healthy call sites from this table (mention the count only).
3. **Healthy call sites** (if any): a one-line list of their IDs/locations — worth naming so the user knows what's already correct and shouldn't be touched.
4. **What this does not cover**: a fixed closing note — this is a point-in-time read of the pasted code only; it cannot see runtime scope changes, dynamic credential injection from outside the pasted files, or anything in files not provided; it does not run continuously. For ongoing detection, the user needs the tracing-middleware project, not this audit, wired into the framework's delegation path with its own observability store.

## Guardrails
- Never invent a call site, a file, or a line number that was not present in the pasted input — if location can't be pinned to a specific line, use the function/symbol name instead of fabricating a line number.
- Never classify a call site `EXPLICIT_NARROW` just because a variable is *named* `scope`, `permissions`, or `token` — verify the code actually constructs something narrower than the parent's own credential before calling it narrowed.
- Never downgrade a `HIGH` finding because the gap "seems unlikely to matter in practice" — severity is mechanical, based only on the two classification axes, not on a guess about real-world likelihood.
- Never resolve an `UNCLEAR` classification by assuming the healthy or unhealthy answer — report it as `LOW` and name exactly what additional file or context would resolve it.
- Never claim this audit provides ongoing/live detection — it is a one-shot snapshot of the pasted code; say so explicitly in every report's closing note.
- If the input is pasted session/transcript logs rather than delegation code, do not attempt to reverse-engineer call sites from log lines — ask for the source code instead.
