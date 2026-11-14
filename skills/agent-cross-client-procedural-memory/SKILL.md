---
name: agent-cross-client-procedural-memory
description: Turns a just-solved task (or a pasted description of one) into a sanitized, reusable "procedure card" — stack signature, steps, rejected approaches, gotchas, and what to adapt per engagement — and matches a new task against a folder of previously saved cards. Use when a freelancer, consultant, or agency engineer finishes a non-trivial recurring task and wants to bank it, or starts a new task and suspects they've solved something like it before on a different client.
---

# Procedure Card: Cross-Client Reusable-Solution Extractor & Matcher

## When to use this
A freelance developer, consultant, or agency engineer who works across multiple, isolated client codebases hits one of two moments:
1. **Capture** — they just finished a task that took real exploration (debugging, config trial-and-error, picking between library options) and recognize "I will definitely hit this exact class of problem again on a different client." Trigger phrases: "save this as a procedure", "bank this so I don't re-derive it next time", "turn this into a reusable recipe."
2. **Match/Recall** — they're starting a new task and suspect they've solved something structurally similar before, but for a different client, and want to check their saved procedure cards before re-deriving the approach from scratch. Trigger phrases: "have I solved something like this before", "check my procedures for X", "what's my recipe for Y stack."

This skill produces or matches a single markdown artifact per invocation — it is not a running background service, a database, or an automatic session hook. It does not silently decide what to save or apply; every card is drafted for explicit confirmation before being treated as saved, and every match is presented as a starting point requiring review, never as an auto-applied script.

## Inputs
**Data source**: Connected — when run inside Claude Code, read the current session's own transcript directly from the session JSONL log (the file under the project's `.claude`/session-log path, or whatever the active session's log path resolves to) and, if configured, via the Hook API's session-end event, rather than asking the user to paste the transcript; this primitive (session logs, hooks) already exists and is mature in Claude Code today — no one has wired it into a procedure-generalization step yet. When that log is not accessible (a different client, a chat-only tool, or a session too old to still be on disk), fall back to **Manual**: the user pastes 2-3 examples of the past (or just-finished) solved task — a chat/transcript excerpt, a commit diff with commit messages, or their own written recollection of what they did and in what order.

For Match mode specifically, also gather:
1. A one- or two-sentence description of the current task.
2. Either a path/folder of previously saved procedure cards (if running somewhere with file access), or 2-3 pasted candidate cards the user believes might be relevant.

## Procedure

### Mode A — Capture
1. Confirm this is a capture request and identify the source material: the session transcript (Connected) or the pasted material (Manual fallback). If neither is available, ask for the paste rather than guessing at what happened.
2. Extract, from what actually happened (never from general best-practice knowledge not evidenced in the material):
   - **Task type** — one canonical line naming the class of problem, e.g. "CI pipeline setup for a Next.js + Postgres monorepo on Vercel."
   - **Stack signature** — concrete tags: languages, frameworks, infra, and relevant version numbers.
   - **Steps that worked** — an ordered, imperative list ("Run X before Y, because Z"), stripped of narration, false starts, and back-and-forth that didn't contribute to the final solution.
   - **Rejected approaches** — what was tried and abandoned, and specifically why it didn't work. This is frequently the most valuable field: it prevents re-walking a known dead end.
   - **Gotchas** — specific traps actually hit (a version mismatch, an auth quirk, an ordering dependency, a silent default that broke things).
   - **Adapt-per-engagement checklist** — the 3-6 concrete parameters that will differ next time (repo/org name, env var names, specific package versions, specific credentials/endpoints) called out explicitly as "swap these before reusing."
3. **Sanitization pass (mandatory, cannot be skipped):** scan every extracted field for anything client-identifying — company/organization names, employee or contact names, internal hostnames/URLs, specific repo or org slugs, API keys or secrets, ticket/issue IDs, email addresses, IP addresses. Replace each with a bracketed placeholder (`[ORG_NAME]`, `[INTERNAL_HOST]`, `[REPO_SLUG]`) and keep a visible list of exactly what was redacted so the user can check it. If something is ambiguous — could plausibly be generic or could be identifying — flag it explicitly as "AMBIGUOUS — confirm" rather than silently choosing either way.
4. Present the full draft procedure card plus the redaction list to the user and ask for explicit confirmation before treating it as final. Do not present it as already saved.
5. On confirmation, output the final card (format below) plus a suggested filename slug (`<task-type-slug>__<stack-signature-slug>.md`) for the user's own local folder of cards. This skill does not create or manage that folder's storage mechanism — a plain directory of markdown files is sufficient and is the user's to maintain.

### Mode B — Match/Recall
1. Take the current task description and the candidate procedure cards (from a folder, if file access exists, or from paste).
2. For each candidate, compare stack signature and task-type against the current task — not by raw keyword overlap, but by whether the underlying technique would actually transfer. Classify each as:
   - **CLEAN MATCH** — same task type, same or trivially different stack.
   - **PARTIAL MATCH** — same technique family, meaningfully different stack or constraints (will need real adaptation, not just parameter substitution).
   - **NO MATCH** — different problem class; discard from the ranked list.
3. Rank CLEAN and PARTIAL matches, each with one sentence of reasoning for the classification.
4. For the top match, surface its steps, rejected approaches, and gotchas as a starting recipe, with the adapt-per-engagement checklist re-flagged for the current engagement, and an explicit reminder that this is a starting point to verify against the current client's actual environment, not a guaranteed-working script.
5. If no CLEAN or PARTIAL match exists, say so plainly — do not force a weak candidate into the output just to have something to show.

## Output format

**Capture mode** produces one markdown card:
```
# Procedure: <Task Type>
**Stack signature**: <tags>
**Captured**: <date>

## Steps
1. ...

## Rejected approaches
- <approach> — <why it failed>

## Gotchas
- ...

## Adapt per engagement
- <parameter> — swap for the new client's value

## Redactions applied
- <original category> -> <placeholder>, for: <field(s)>
```

**Match mode** produces a ranked list:
```
# Procedure Match for: <current task description>

1. [CLEAN MATCH | PARTIAL MATCH] <card name> — <one-sentence reasoning>
2. ...

## Recommended starting recipe (from top match)
<steps, rejected approaches, gotchas, adapt-per-engagement checklist, carried over>

**Verify before using**: <what specifically to check against the current client's environment before applying any step>
```
If no match: state plainly that no existing card applies and recommend capturing a fresh one once this task is solved.

## Guardrails
- Never save a procedure card without explicit user confirmation after the sanitization pass completes — this is the exact point where an unredacted identifier would do the most damage.
- Never include, in a saved card, anything that reads as a secret, credential, specific person's name, company name, domain, hostname, or ticket/issue ID — flag ambiguous terms rather than guessing either direction.
- Never fabricate steps, gotchas, or rejected approaches that are not actually evidenced in the transcript or pasted material. If the source material doesn't contain a working solution, say so rather than padding the card with generic "best practice" advice that was never actually used.
- Never present a matched procedure as ready to apply automatically. Always frame it as a reviewed starting point — misapplying a recipe from the wrong context (e.g., a staging-only auth bypass) could cause real harm in production.
- Never guess at session contents when the transcript/log isn't accessible — ask the user to paste the material instead of inventing what probably happened.
