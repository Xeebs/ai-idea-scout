# AI Coding Agent Architecture Boundary Gate

A prompt template for drafting a layer-boundary CI gate for a repo where AI coding agents (Claude Code, Cursor, Codex, Copilot) regularly open PRs and keep crossing architectural boundaries — e.g. agent-generated code importing directly from an `infra/` layer it should only reach through `domain/`. Instead of hand-writing a one-off shell script (which is exactly what teams are doing today, and which breaks easily), this produces a reviewable draft bundle: a declarative rule file, matching enforcement snippets, and a merge-queue-safe CI trigger.

## When to use this

Use this the moment you (or your team) notice an AI coding agent's PRs keep crossing a layer boundary you care about — importing from a low-level module directly instead of going through the layer that's supposed to own it — and you want a CI-ready starting config instead of writing the rules from scratch. This is a bootstrap/drafting tool, not an always-running service: you run it once (or occasionally, as the repo evolves) to get a draft, then you review and wire it into your own CI yourself.

Don't use this for reviewing a single PR (that's a normal code review) or on a repo with no real layering and no agent-PR friction yet.

## Data source

This needs your repo's actual directory structure — never let the AI guess at a "typical" layout from memory. Two ways to provide it:

- **Connected (preferred)**: if you're using this inside a coding assistant with filesystem or GitHub access (e.g. Claude Code, or any tool that can run `gh` commands), it reads the real tree and recent merged-PR history itself. This uses the GitHub API/`gh` CLI, a mature connector already standard for CI tooling.
- **Manual (fallback)**: if you're pasting this into a plain chat tool with no repo access, paste the output of:
  ```
  find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*'
  ```
  and, if you have them, 3-5 recent merged PR diffs that touched cross-layer imports (optional, but it lets the draft cite real history instead of guessing).

You also need to tell it either:
1. Your intended layer boundaries in plain language (e.g. "`domain/` must never import `infra/` directly; `api/` can import `domain/` but not `infra/`"), **or**
2. Permission to infer boundaries from your folder names — in which case it will show you its guess and ask you to confirm before generating anything.

## What to paste into the chat tool

```
I want a draft architecture-boundary CI gate for this repo. Here is the directory
structure:

<paste `find . -type d` output, or describe it>

[Optional] My intended boundaries:
<e.g. "domain/ should never import infra/ directly. api/ can import domain/,
not infra/. web/ should only call api/ over HTTP, never import it directly.">

[Optional] We do / do not use a GitHub merge queue.

[Optional] Recent PRs that crossed a boundary, if you have diffs:
<paste diff excerpts>

Please:
1. Detect the languages in use from manifest files (package.json, pyproject.toml,
   requirements.txt, tsconfig.json).
2. If I didn't give explicit boundaries, infer candidate layers from folder names
   (api/, domain/, core/, infra/, adapters/, ui/, web/, services/) and show me the
   inferred rules as a numbered list before generating anything — don't assume
   I've confirmed them.
3. If my structure doesn't cleanly map to a layered pattern, tell me plainly and
   ask for an explicit boundary description instead of forcing a fake split.
4. If I gave you PR diffs or you have access to pull recent merged-PR diffs
   yourself, check whether any violate the confirmed rules and cite file:line.
   If you have no diff evidence at all, say so explicitly rather than claiming a
   violation count.
5. Generate:
   a. A declarative YAML rule file (layer names as keys, allow/deny import
      directions).
   b. A matching enforcement snippet per detected language: pytest-archon for
      Python, an ESLint eslint-plugin-boundaries config for JS/TS. Flag any other
      detected language as unsupported rather than inventing a tool for it.
   c. A merge-queue SHA-binding GitHub Actions snippet (triggering the gate job
      on `merge_group` in addition to `pull_request`) — only if I use a merge
      queue. If I don't, say plainly it's not applicable.
6. Present everything as a draft bundle for me to review — don't tell me it's
   ready to commit, and don't generate a PR yourself.
```

## What you get back

A single structured response with these sections, in order:

1. **Detected layers & languages** — what was found in the manifest files and folder names.
2. **Boundary rules table** — explicitly marked as either "confirmed by you" or "inferred — needs your confirmation," with a May-import-from / Must-not-import-from column per layer.
3. **YAML rule config** — a ready-to-save `boundary-gate.yml` encoding the table above.
4. **Backend snippet(s)** — a `pytest-archon` test file for Python, an ESLint `eslint-plugin-boundaries` config for JS/TS, one per language actually detected. Any detected language with no supported backend is named, not silently skipped.
5. **Merge-queue SHA-binding snippet** — a GitHub Actions trigger addition, or an explicit "not applicable, you don't use a merge queue" if that's the case.
6. **Historical violation check** — either a list of real file:line hits from recent merged PRs that the new rules would have caught, or an explicit "skipped, no diff evidence available" — never a fabricated count.
7. **A review checklist** — concrete steps to take (run locally first, pick warn-vs-block mode, check the merge-queue trigger addition) before wiring anything into live CI.

## Guardrails (what this will never do)

- It never commits, pushes, or opens a PR with the generated files — you review and wire them in yourself.
- It never guesses your repo's structure from memory — it requires the real tree, read directly or pasted.
- It never presents an inferred boundary as if you'd confirmed it — inferred rules are always labeled as a guess pending your sign-off.
- It never states a "this would have caught N violations" number without real diff evidence — if there's no diff access, it says so.
- It never generates a merge-queue snippet for a repo that doesn't use one.
- It never forces a layered rule set onto a flat or inconsistent repo — if your folders don't map to a clean layered pattern, it will tell you and ask for an explicit rule description instead of inventing layers.
- It never invents a fitness-check tool for a language that doesn't have an established one (currently: Python via pytest-archon, JS/TS via ESLint boundaries only).
