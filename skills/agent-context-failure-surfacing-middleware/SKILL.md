---
name: agent-context-failure-surfacing-middleware
description: Audits an agent's tool-call, history-retrieval, and attachment-fetch code paths to classify whether each one actually tells the model a failure happened, or lets the agent answer from a wrong or incomplete picture. Use before adopting any failure-surfacing middleware, or whenever a production agent has given a confidently wrong answer after a backend hiccup.
---

# Agent Context-Failure Audit

## When to use this
A team building or operating a production LangGraph, CrewAI, or custom-loop agent notices (or suspects) that the agent sometimes answers confidently from stale, missing, or partial context — a tool call that errored, a history fetch that came back empty, or an attachment download that failed — without saying so. This skill is the one-time diagnostic a team runs before deciding whether to build or adopt a runtime failure-surfacing layer: it tells them exactly which call sites are already safe and which ones are silently or vaguely failing, with a concrete fix for each.

Do not reach for this skill to debug a single one-off incident with a known root cause — it's for a systematic pass across an agent's call sites, not an incident post-mortem.

## Inputs
**Data source**: Connected — the skill reads the user's own agent codebase directly, either via file path/repo access (when run in an environment with file tools, e.g. Claude Code's Read/Grep) or via pasted code sections when run in a plain chat tool with no file access. There is no third-party API or SaaS connector involved; "connected" here means direct access to the user's own source rather than requiring everything retyped into the chat. This connector already exists trivially in any coding-capable AI tool today — nothing new needs to be built for it.

To run this skill, provide:
1. The agent's framework: LangGraph, CrewAI, or "custom loop" (describe the loop's shape in one sentence if custom).
2. The code for every call site that does one of three things: calls an external tool/function, retrieves conversation history, or fetches an attachment/file — either as file paths to read, or pasted verbatim including the surrounding try/except (or lack of one).
3. Optional but valuable: one real or representative transcript where the agent answered despite a known backend failure, to anchor the audit in an actual symptom.

## Procedure
1. **Enumerate call sites.** Walk the provided code (or files) and list every call site matching one of three types:
   - **Tool** — any call out to an external function/API/tool the model invoked.
   - **History** — any retrieval of prior conversation/session state (DB read, cache lookup, memory-store fetch).
   - **Attachment** — any fetch of a file, image, or document referenced in the conversation.
2. **Trace the failure path for each one.** For each call site, find what happens when the call raises, times out, or returns empty/partial data: is there a try/except (or framework-level error hook)? What does that branch actually do — return a value, raise further, log only, or silently continue?
3. **Classify each call site into exactly one bucket:**
   - `SURFACES` — on failure, a message naming what failed and what the model should assume is missing is injected into the model's own context (e.g., a LangGraph `ToolMessage`, a CrewAI tool-wrapper's returned string, an appended message in a custom loop) — not just logged or raised outside the model's view.
   - `UNSTRUCTURED` — the model does receive something on failure, but it's an opaque raw error ("Error: 500", a stack trace, a bare exception string) that doesn't tell the model what's missing or what to do about it.
   - `SWALLOWED` — the model receives nothing distinguishing failure from success: an empty list/string/default value, a stale cached value, or the code catches the exception and proceeds as if the call had worked.
4. **Do not trust the presence of a try/except alone.** A try/except that logs to stdout/a monitoring tool and then returns `[]` or `None` to the agent loop is `SWALLOWED`, not safe — the model still never sees it. Confirm the failure branch's return value actually reaches the messages/context the model reads next.
5. **Check for a related but distinct failure mode while you're in the code**: an unbounded retry loop on the same failing call (the model or framework retries forever with no escalation) — flag this separately as `RETRY_LOOP` even if the eventual message would otherwise classify as `SURFACES`, since infinite retry is its own user-facing failure (hang/timeout) regardless of what the model is eventually told.
6. **For every `SWALLOWED`, `UNSTRUCTURED`, or `RETRY_LOOP` site, draft a concrete fix**: the specific structured failure message to inject (failure type, affected scope — e.g. "last 10 messages before this point are unavailable," suggested model behavior — e.g. "ask the user to resend" or "flag this answer as based on partial history"), expressed as a code snippet in the host framework's own idiom (LangGraph: inject a `ToolMessage`/error-typed message into the graph state; CrewAI: have the tool wrapper return the structured string instead of raising; custom loop: append a system/tool-role message before the next model call).
7. **Rank findings by severity**: `SWALLOWED` first (highest risk — confidently wrong answers with no signal anything went wrong), then `RETRY_LOOP`, then `UNSTRUCTURED`, then list `SURFACES` sites last as confirmed-safe.
8. If the provided code contains zero tool/history/attachment call sites, say so plainly — do not invent findings to fill out a report.

## Output format
A markdown audit report with:
1. **Summary table**: one row per call site — `Call site | Type (Tool/History/Attachment) | Bucket | Location (file:line or snippet label)`.
2. **Findings**, one subsection per `SWALLOWED`/`UNSTRUCTURED`/`RETRY_LOOP` site, each containing: the offending code (quoted verbatim, never paraphrased), why it's dangerous in one sentence, and the suggested fix as a code snippet.
3. **Confirmed-safe** section: a short list of `SURFACES` sites, so the team knows what not to touch.
4. **Rollup**: counts per bucket per call-site type, and a single sentence naming the highest-priority fix to make first.

## Guardrails
- Never classify a call site as `SURFACES` just because a try/except exists — verify the failure branch's output actually reaches the model's context, not just a log line or monitoring call.
- Never fabricate file/line numbers or invent code structure that wasn't provided — when working from pasted code without line numbers, cite the snippet itself as the location label instead of guessing a line number.
- Never recommend a specific commercial middleware product or framework migration as "the fix" — the output is a code-level fix for this codebase as it stands, not a sales pitch for adopting new infrastructure.
- Never report findings for call-site types that aren't present in the provided code — report "no attachment-fetch call sites found" rather than padding the report to look more thorough.
- Never treat a generic catch-all `except Exception: pass` (or language equivalent) anywhere in agent-loop code as automatically out of scope — if it sits on a tool/history/attachment call path, it's `SWALLOWED` by definition even if it looks like unrelated defensive coding.
