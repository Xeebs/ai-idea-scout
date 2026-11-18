# MCP Hosted Deploy Approval Gateway — Skill (Portable Prompt Template)

Paste this whole document into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with the information requested in "What to hand over" below. No installation, no plugin, no prior context about any other project required.

## What this does

You're about to ask someone to approve a new internal MCP (Model Context Protocol) server — or a scope/tool change to an existing one — before it goes live. Instead of writing the approval request from scratch and hoping you didn't miss something a security reviewer would flag, this prompt turns your server's manifest and a short checklist into: a completeness check, a scope-by-scope risk review, an auth-vs-data-sensitivity flag, a clear recommendation (approve / approve with conditions / escalate / block), and a ready-to-paste pull request description.

This is a one-shot authoring and review aid for a human preparing or reviewing an approval request. It does not deploy, merge, or approve anything itself — a named human reviewer always makes the final call.

## What to hand over (manual paste — no connected accounts needed)

Paste or type the following. If any of the first five is missing, say so — don't guess.

1. **Server name and purpose** — one line on what it does.
2. **Full tool list with requested scopes** — every tool the server exposes, and the specific permission/scope each one requests (e.g., "`post_comment` — requires `issues:write`").
3. **Auth type** — OAuth (name the scopes), static API key, mTLS, service account, or none.
4. **Data the server reads and/or writes** — be specific: "customer PII," "internal ticket metadata," "read-only public documentation," etc.
5. **Named human maintainer** — a real person, not a team alias or distribution list.
6. **Intended hosting target** (optional).
7. **Any existing automated security/trust scan output** (optional — will be treated as supporting evidence only, never as the deciding factor).

If you're working inside a coding assistant that can read files, you can instead point it at the server's manifest/README/config files directly and ask it to extract the same six fields — the rest of the procedure is identical either way.

## The procedure (what the assistant should do with your input)

1. **Extract the checklist.** Pull out the six required fields. Mark each Present or Missing.
2. **Block on missing required fields first.** If the server name/purpose, auth type, data touched, or maintainer is missing, the review stops short of APPROVE — it becomes at best ESCALATE, or BLOCK if the maintainer or auth type specifically is missing, or if multiple fields are missing.
3. **Check every tool's scope against its stated purpose.** For each tool, ask: does what this tool is supposed to do actually need the scope it's requesting? A "read tickets" tool asking for write access, or a "post a status comment" tool asking for admin/delete rights, gets flagged OVERBROAD — regardless of how benign the tool's description sounds.
4. **Cross-check auth strength against data sensitivity.** If the data involved is anything like PII, credentials, financial records, or source code containing secrets, and the auth is "none," a shared static key, or an overly broad service account, that specific combination gets flagged HIGH RISK — even if every individual scope passed step 3.
5. **Treat scanner output as supporting evidence only.** A clean automated scan result is noted, but it never overrides the manual scope and auth-sensitivity checks above.
6. **Land on one recommendation:**
   - **APPROVE** — everything required is present, no scope is overbroad, auth strength matches data sensitivity.
   - **APPROVE WITH CONDITIONS** — fields are all present, but a specific fix (narrow this scope, confirm this maintainer, re-run this scan) should happen before merge.
   - **ESCALATE** — a HIGH RISK auth/data combination exists, or one non-identity required field is missing — a named security reviewer, not just the requesting team, needs to weigh in.
   - **BLOCK** — the maintainer or auth type field is missing, or multiple required fields are missing. Don't let this go to a reviewer yet.
7. **Draft the PR description**, ready to paste into GitHub (or whatever your team's review tool is).

## Output you should get back

Every run should produce, in this order:

1. A **checklist table**: field name, Present/Missing, and the value (or "MISSING — requester must provide").
2. A **scope risk table**: one row per tool — tool name, requested scope, stated purpose, verdict (OK or OVERBROAD), and a short note.
3. One **auth/data risk sentence** stating the auth type, the data sensitivity call, and whether that pairing is HIGH RISK.
4. A bolded **recommendation** — APPROVE / APPROVE WITH CONDITIONS / ESCALATE / BLOCK — with 1–3 sentences citing exactly which table rows drove the call.
5. A **draft PR body**, in a code block, with these sections: `## Server`, `## Requested Scopes`, `## Auth Type`, `## Data Accessed`, `## Maintainer`, `## Hosting Target`, `## Scanner Results (if any)`, `## Reviewer Recommendation`.

## Guardrails — the assistant should never

- Output APPROVE when the maintainer, auth type, or data-touched field is missing. Missing accountability or sensitivity information always forces at least ESCALATE.
- Invent a tool, scope, or checklist answer that wasn't actually given. Ambiguous or absent information gets marked Missing, not filled in with a plausible guess.
- Let a clean automated scanner result override the manual scope/auth checks — it's one input, not a verdict.
- Imply that it deployed, merged, or gave final approval to anything. It drafts and recommends; a named human always makes the actual call.
- Downgrade an OVERBROAD scope finding to OK just because the tool's written description sounds harmless. The verdict follows the actual permission string against the actual stated purpose.

## Example of how to open the conversation

"I need to get an internal MCP server approved before we deploy it. Here's the manifest and checklist info: [paste]. Please run the MCP deploy approval review on it and give me the checklist table, scope risk table, recommendation, and a draft PR body I can paste into GitHub."
