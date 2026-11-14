---
name: ai-coding-agent-architecture-boundary-gate
description: Drafts a declarative layer-boundary rule config (YAML schema + pytest-archon/ESLint-boundaries snippets + a merge-queue SHA-binding CI check) for a repo where AI coding agents (Claude Code, Cursor, Codex) regularly open PRs and keep crossing architectural layers. Use when a team wants to bootstrap an architecture-fitness gate from their existing folder structure instead of hand-writing one.
---

# AI Coding Agent Architecture Boundary Gate

## When to use this
A team's repo has agent-authored PRs (Claude Code, Cursor, Codex, or any bot/commit-trailer-tagged agent) landing at meaningful volume, and someone — a maintainer, platform engineer, or the agent itself mid-session — wants a CI-ready layer-boundary rule config drafted from the repo's own structure instead of hand-rolling a shell script or starting from a blank fitness-function template. Reach for this the moment someone says "the agent keeps importing from infra directly" or "we need a gate so Claude Code stops crossing layers" or "draft us an architecture-fitness config for this repo."

Do not use this for a one-off single-file review (that's a normal code review) or for repos with no AI-agent PR volume and no layering friction yet — this is a bootstrap/drafting aid for a specific, already-felt problem, not a generic "add architecture tests" starter kit.

## Inputs
**Data source**: Connected — reads the target repo's directory structure directly (via Claude Code's filesystem/Glob tools, or `git ls-tree -r --name-only HEAD` / `find . -type d`) and recent merged-PR diff history via the GitHub API/`gh` CLI (`gh pr list --state merged`, `gh pr diff`) — both mature, already-standard connectors for CI tooling. If working in a plain chat tool with no repo access, the user pastes: (1) the output of `find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*'`, and (2) optionally, 3-5 recent merged PR diffs that touched cross-layer imports. Never proceed on a guessed or remembered repo structure — always get the real tree or diffs from one of these sources.

Required from the user:
1. The repo's directory tree (read directly, or pasted).
2. Either a plain-language description of the intended layer boundaries ("domain/ must never import infra/ directly"; "ui/ can only call api/ over HTTP, no direct imports") OR permission to infer boundaries from folder naming conventions.

Optional but improves accuracy:
- Whether the repo uses a GitHub merge queue (if unknown, check for a `merge_group` workflow trigger or ask).
- Primary language(s) if not obvious from `package.json`/`pyproject.toml`/`requirements.txt`/`tsconfig.json` presence.
- Recent PR diffs that already crossed a boundary, to ground the draft in real history.

## Procedure
1. **Get the real repo structure.** Read it directly if you have filesystem/GitHub access; otherwise require the user to paste a directory listing. Never invent a folder structure.
2. **Detect language(s)** from manifest files present (`pyproject.toml`/`requirements.txt` → Python; `package.json`/`tsconfig.json` → JS/TS). If the repo is polyglot, plan to generate one backend snippet per detected language with a known backend. If a detected language has no known backend (anything other than Python or JS/TS), say so explicitly and skip generating a snippet for it rather than guessing a tool.
3. **Establish boundaries.** If the user gave a plain-language description, use it verbatim as the source of truth. If not, infer candidate layers from folder names matching common patterns (`api/`, `domain/`, `core/`, `infra/`, `adapters/`, `ui/`, `web/`, `services/`) and propose a draft rule set (e.g., "domain/ → no imports from infra/ or api/; api/ → may import domain/, not infra/ directly"). **Always present inferred rules back to the user as a numbered list and get explicit confirmation or correction before generating any config** — never silently ship a guessed boundary. If the folder structure doesn't map cleanly to any recognizable layered pattern (flat `src/` with mixed concerns, no naming convention), say so plainly and ask the user for an explicit boundary description instead of forcing a fake layer split.
4. **Check history, if available.** If you have `gh`/GitHub API access, pull the last 5-10 merged PRs' diffs and check whether any changed import touches a path that the confirmed boundary rules would have forbidden. Record exact file:line hits. If you don't have this access and the user didn't paste any diffs, skip this step and say so in the output — never state a "would have caught N violations" count without diff evidence behind it.
5. **Generate the declarative YAML rule schema** — one file, layer names as keys, each with an `allow`/`deny` import-direction list, matching the confirmed boundaries from step 3.
6. **Generate per-language backend snippet(s)** matching the confirmed boundaries:
   - Python → a `pytest-archon` test file encoding the same allow/deny rules.
   - JS/TS → an ESLint config snippet using import-boundary rules (e.g. `eslint-plugin-boundaries`) encoding the same rules.
   - Any other detected language → explicitly flagged as unsupported, not silently skipped.
7. **Generate the merge-queue SHA-binding check**, only if the repo uses (or the user confirms they'll enable) a GitHub merge queue: a GitHub Actions snippet that triggers the boundary-gate job on `merge_group` (the queue's resolved SHA) in addition to `pull_request`, so the gate can't be bypassed by a merge-queue re-resolution landing a different SHA than the one that was checked. If the repo has no merge queue, state plainly that this section is not applicable and why, rather than generating a snippet for a feature that isn't in use.
8. **Assemble the bundle** exactly in the Output format below, labeled as a draft for human review — never auto-wire it into CI, open a PR with it, or commit it yourself.

## Output format
```
# Architecture Boundary Gate — Draft for <repo name>

## Detected layers & languages
- Languages: <e.g. Python (pyproject.toml), TypeScript (tsconfig.json)>
- Layers found/confirmed: <list, or "no clean layered structure detected — see note below">

## Boundary rules (confirmed with user / inferred — state which)
| Layer | May import from | Must NOT import from |
|---|---|---|
| domain/ | (none) | infra/, api/ |
| api/ | domain/ | infra/ |

## YAML rule config (boundary-gate.yml)
```yaml
<generated schema>
```

## Backend snippet(s)
### Python — pytest-archon
```python
<generated test>
```
### JS/TS — ESLint boundaries
```json
<generated config>
```
(or: "No backend generated for <language> — no known fitness-check tool for this language.")

## Merge-queue SHA-binding check
```yaml
<generated workflow snippet>
```
(or: "Not applicable — this repo does not appear to use a GitHub merge queue.")

## Historical violation check
<"This rule set would have flagged N import(s) across M of the last K merged PRs: file:line list" OR "Skipped — no PR diff access available; this section reflects no historical evidence, not an absence of violations.">

## Review checklist before wiring into CI
- [ ] Confirm the boundary rules above match intent (especially any inferred, unconfirmed ones)
- [ ] Run the backend snippet(s) locally against the current tree before enabling in CI — expect some existing violations on first run
- [ ] Decide enforcement mode (warn vs. block) for the first 1-2 weeks
- [ ] If using a merge queue, confirm the `merge_group` trigger is added alongside `pull_request`, not replacing it
```

## Guardrails
- Never commit, push, or open a PR with the generated config — this is a draft the human reviews and wires in themselves.
- Never guess a repo's directory structure or PR history from memory or general knowledge of "typical" layouts — always read it or require it pasted.
- Never present inferred boundary rules as confirmed; always mark them as inferred until the user explicitly confirms or corrects them.
- Never claim a historical "would have caught N violations" number without actual diff evidence behind it — state plainly when that check was skipped.
- Never generate a merge-queue SHA-binding snippet for a repo that doesn't use a merge queue; state it's not applicable instead.
- Never force a layered rule set onto a repo whose structure doesn't support one — flag messy/flat structures and ask for an explicit boundary description rather than inventing layers to fill the template.
- Never generate a backend snippet for a language with no established fitness-check tool behind it (anything beyond Python/pytest-archon and JS-TS/ESLint-boundaries) — flag it as unsupported instead of inventing one.
