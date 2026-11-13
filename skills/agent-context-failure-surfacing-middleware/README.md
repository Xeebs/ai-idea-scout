# Agent Context-Failure Audit

A paste-into-any-AI-chat-tool prompt that audits an AI agent's code for one specific, costly blind spot: when a tool call, a conversation-history fetch, or an attachment/file download fails, does the agent's underlying model actually get told — in a way it can reason about — or does the agent just answer anyway, confidently, from a wrong or incomplete picture?

This is not a general code-quality or error-handling linter. It only looks at the three call-site types that decide what context a model has when it generates its next response: tool calls, history retrieval, and attachment fetches. A try/except that logs an error and moves on still fails this audit if the model never sees that anything went wrong.

## When to use this

Use this when:
- You're operating a production LangGraph, CrewAI, or custom-loop agent and users have reported (or you suspect) the agent gives confident answers that turn out to be based on a tool error, a missing chunk of history, or a file that never actually downloaded.
- You're about to adopt or build a runtime "failure-surfacing" layer and want to know, concretely, which of your existing call sites already need it versus which are fine.
- You're doing a pre-launch review of an agent's reliability before it goes in front of real users.

Don't use this for debugging one specific known incident with a known root cause — it's a systematic sweep across call sites, not an incident post-mortem.

## What you need to provide

This skill reads your actual code — not a paraphrase of it. Give it:

1. **Framework**: LangGraph, CrewAI, or "custom loop" (if custom, one sentence describing the loop's shape — e.g. "a while-loop that calls the model, executes any requested tool, and appends the result as a message").
2. **The code itself** for every call site that: (a) calls an external tool/function the model invoked, (b) retrieves prior conversation history or session state, or (c) fetches an attachment, image, or document. Paste the code verbatim, including the surrounding try/except block or the absence of one — this is the one thing the audit can't work around if it's missing.
3. **Optional**: a real or representative transcript where the agent answered despite a known backend hiccup. This isn't required, but it anchors the audit in an actual symptom instead of pure code reading.

If you're using a coding-capable AI tool that can read files directly (like Claude Code), you can just point it at the relevant files/paths instead of pasting — same audit, same procedure.

## The procedure

Work through the provided code in this order:

1. **List every call site** of the three types above (tool / history / attachment). Don't skip ones buried inside helper functions.
2. **Trace what happens on failure** for each one: find the try/except (or framework-level error hook). Does that failure branch return something, raise further, log only, or silently continue as if nothing happened?
3. **Classify each call site into exactly one of three buckets:**
   - **SURFACES** — on failure, a message naming what failed and what the model should assume is missing is actually injected into the model's own context (not just logged to a file or monitoring tool).
   - **UNSTRUCTURED** — the model does get something on failure, but it's a raw error string or stack trace that doesn't tell it what's missing or what to do next.
   - **SWALLOWED** — the model gets nothing distinguishing failure from success: an empty default, a stale cached value, or the exception is caught and the agent proceeds as if the call worked.
4. **Don't trust a try/except by itself.** If the except branch logs the error and then returns `[]`, `None`, or an empty string to the agent loop, that's still SWALLOWED — the model never sees it, regardless of what got logged elsewhere.
5. **Flag unbounded retry loops separately** as RETRY_LOOP — if a failing call gets retried forever with no escalation to the model or user, that's its own failure mode (a hang/timeout) independent of what the eventual message says.
6. **For every SWALLOWED, UNSTRUCTURED, or RETRY_LOOP finding, write a concrete fix**: the exact structured failure message to inject (what failed, what scope is affected, what the model should do — ask the user, retry once, or flag the answer as partial), as a code snippet in that framework's own style (a LangGraph `ToolMessage`/error message injected into graph state; a CrewAI tool wrapper returning the structured string instead of raising; a custom loop appending a message before the next model call).
7. **Rank the findings**: SWALLOWED first (most dangerous — a confidently wrong answer with zero signal anything went wrong), then RETRY_LOOP, then UNSTRUCTURED, then list SURFACES sites last as already-safe.
8. If a given call-site type (tool/history/attachment) simply doesn't appear in the code, say so — don't invent findings to pad the report.

## Output format

Produce a markdown report with exactly these sections:

1. **Summary table** — one row per call site: `Call site | Type | Bucket | Location`.
2. **Findings** — one subsection per SWALLOWED/UNSTRUCTURED/RETRY_LOOP site: the offending code quoted verbatim, one sentence on why it's dangerous, and the fix as a code snippet.
3. **Confirmed-safe** — a short list of SURFACES sites, so nobody wastes time "fixing" something that's already fine.
4. **Rollup** — counts per bucket per call-site type, plus one sentence naming the single highest-priority fix to make first.

## Guardrails

- Never mark something SURFACES just because a try/except exists — confirm the failure branch's output actually reaches the model's context.
- Never invent line numbers or code you weren't given — if there are no line numbers (pasted snippets), label the location with the snippet itself instead of guessing.
- Never pitch a specific commercial product or framework migration as "the fix" — every recommendation should be a code change to the codebase as given.
- Never report a finding for a call-site type that isn't present in the code — explicitly say "no attachment-fetch call sites found" instead.
- A generic `except Exception: pass` (or equivalent) sitting on a tool/history/attachment call path is SWALLOWED by definition, even if it reads like routine defensive coding elsewhere in the file.
