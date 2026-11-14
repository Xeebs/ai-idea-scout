# Procedure Card: Cross-Client Reusable-Solution Extractor & Matcher

A paste-into-any-AI-chat-tool prompt for freelance developers, consultants, and agency engineers who work across multiple, isolated client codebases. It turns a task you just solved (or one you solved a while back) into a sanitized, reusable "procedure card" — the recipe, not the client-specific details — and it can also check a new task against a set of cards you've already saved to see if you've effectively solved this before.

This produces one markdown artifact per use. It is not a running tool, not a database, and it never decides anything silently: every card is drafted for your explicit confirmation before it counts as "saved," and every match is handed back as a starting point to verify, never as a script to run blind.

## When to use this
- **Capture**: You just finished a task that took real exploration — debugging, trying a few config options, picking between libraries — and you know you'll hit this exact class of problem again for a different client. Say: "save this as a procedure" or "turn this into a reusable recipe."
- **Match/Recall**: You're starting a new task and suspect you've solved something structurally similar before, just for a different client. Say: "check if I've solved something like this before" and point the assistant at your saved cards (or paste a couple of candidates).

## What to hand over

**Data source: Connected** (inside Claude Code) — the skill reads your current session's own transcript log directly (Claude Code already writes a session JSONL log and exposes a Hook API for session-end events; this is mature, built-in functionality, just not wired into a procedure-generalization step until now), so you don't have to paste anything for a same-session capture. **Falls back to Manual** whenever that log isn't accessible — a different client's session, a plain chat tool with no file access, or an old session no longer on disk. In that case, paste:

1. Two to three examples of the solved task: a chat/transcript excerpt, a commit diff with its commit messages, or your own written recollection of what you did and in what order.
2. For match mode: a one- or two-sentence description of your current task, plus either a folder of your saved cards (if the tool has file access) or 2-3 pasted candidate cards you think might apply.

## The procedure the assistant follows

### Capture
1. Read the transcript (or your paste) and pull out, strictly from what actually happened — never from generic "best practice" the assistant already knows but that you didn't actually use:
   - **Task type** — one line, e.g. "CI pipeline setup for a Next.js + Postgres monorepo on Vercel."
   - **Stack signature** — languages, frameworks, infra, relevant versions.
   - **Steps that worked** — an ordered, imperative list, with the false starts and back-and-forth stripped out.
   - **Rejected approaches** — what was tried and dropped, and why. Often the most valuable part: it saves you from re-walking a known dead end.
   - **Gotchas** — the actual traps hit (a version mismatch, an auth quirk, a silent default that broke something).
   - **Adapt-per-engagement checklist** — the 3-6 things that will be different next time (repo/org name, env var names, specific versions, credentials/endpoints) — flagged explicitly as "swap these."
2. **Mandatory sanitization pass**: every field gets scanned for anything client-identifying — company or employee names, internal hostnames/URLs, repo/org slugs, API keys, ticket IDs, emails, IPs. Each gets replaced with a bracketed placeholder (`[ORG_NAME]`, `[INTERNAL_HOST]`) and the assistant shows you exactly what it redacted so you can check it. Anything ambiguous gets flagged as "AMBIGUOUS — confirm," never silently decided.
3. The assistant shows you the full draft card plus the redaction list and asks you to confirm before treating it as final — it never claims the card is "saved" on its own.
4. Once you confirm, you get the final card (format below) plus a suggested filename for your own folder of cards — a plain folder of markdown files is all this needs; there's no special storage system to set up.

### Match/Recall
1. You give your current task description and either a folder path or a few pasted candidate cards.
2. Each candidate gets compared against the current task by whether the underlying technique would actually transfer, not by keyword overlap, and classified as **CLEAN MATCH** (same task type, same/near-identical stack), **PARTIAL MATCH** (same technique family, meaningfully different stack — real adaptation needed), or **NO MATCH** (different problem; dropped from the list).
3. CLEAN and PARTIAL matches get ranked with a one-sentence reason each.
4. The top match's steps, rejected approaches, and gotchas get surfaced as a starting recipe, with the adapt-per-engagement checklist re-flagged for your current client, plus an explicit reminder to verify it against your current environment — it's a starting point, not a guaranteed-working script.
5. If nothing clears the bar, the assistant says so plainly instead of forcing a weak match just to give you something.

## What you get back

**Capture mode:**
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

**Match mode:**
```
# Procedure Match for: <current task description>

1. [CLEAN MATCH | PARTIAL MATCH] <card name> — <one-sentence reasoning>
2. ...

## Recommended starting recipe (from top match)
<steps, rejected approaches, gotchas, adapt-per-engagement checklist, carried over>

**Verify before using**: <what to check against the current client's environment first>
```

## Guardrails (what the assistant should never do)

- Never mark a card "saved" without your explicit confirmation after sanitization — that confirmation step is exactly what catches an unredacted identifier before it does damage.
- Never leave in a card anything that reads as a secret, credential, specific name, company, domain, hostname, or ticket ID — flag anything ambiguous instead of guessing which way it goes.
- Never invent steps, gotchas, or rejected approaches that weren't actually in your transcript or paste. If the material doesn't show a real working solution, the assistant should say so rather than filling in generic advice you never actually used.
- Never hand back a match as ready to run as-is — it's always a reviewed starting point, because applying a recipe from the wrong context (e.g. a staging-only shortcut) in the wrong place could cause real damage.
- Never guess at what happened in a session it can't read — if the transcript/log isn't accessible, it should ask you to paste the material instead of inventing what probably happened.
