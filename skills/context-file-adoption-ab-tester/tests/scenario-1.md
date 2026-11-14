# Scenario 1 — Mid-size SaaS repo, bloated CLAUDE.md inherited from a template

## Setup

A 6-person team at a B2B SaaS company pastes in their `CLAUDE.md`, which was originally copied from a popular open-source "starter CLAUDE.md" template eight months ago and has been lightly edited since. Agent used: Claude Code. Repo: "Node.js/TypeScript monorepo, ~45k LOC, Next.js frontend + Express API, Postgres via Prisma, roughly 60k LOC." No specific task prompts supplied (optional field left as "none provided").

Pasted file content:

```
# CLAUDE.md

## Code Style
- Write clean, readable, maintainable code.
- Use meaningful variable and function names.
- Add comments for complex logic.
- Follow SOLID principles.

## Tech Stack
This project uses TypeScript, React, and Node.js. We use npm for package
management. The database is PostgreSQL.

## Testing
Always write tests for new features. Run `npm test` before committing.
Our test coverage target is 80%.

## Git Workflow
- Create a feature branch for every change.
- Never push directly to main.
- Write descriptive commit messages following Conventional Commits.
- Open a PR and wait for review before merging — do not merge your own PRs,
  and never use `git push --force` to main under any circumstances.

## Legacy Auth Module
The old auth system lives in `src/auth/legacy/` and uses the deprecated
`passport-local-v1` package. Do not touch this code — it is being replaced
by the new Clerk-based auth flow in `src/auth/clerk/`. If you need to work
on auth, use the Clerk flow only.

## Deployment
Deploys are handled via `scripts/deploy-staging.sh` and
`scripts/deploy-prod.sh`. Never run `scripts/deploy-prod.sh` directly —
all production deploys must go through the CI pipeline and require a
manual approval step from an on-call engineer.

## Database Migrations
Run `npx prisma migrate dev` for local migrations. Production migrations
are applied automatically by CI on merge to main — do not run
`prisma migrate deploy` manually against production.
```

The team mentions in passing that the `passport-local-v1` legacy auth module was actually fully deleted three months ago during a cleanup sprint, and Clerk is now the only auth system — but they forgot to update this file.

## Pass criteria

- [ ] Report segments the file into the 6 sections (Code Style, Tech Stack, Testing, Git Workflow, Legacy Auth Module, Deployment, Database Migrations — 7 if split that granularly) in document order with a one-line paraphrase each.
- [ ] "Code Style" is flagged VERBOSE (generic best-practice advice with no repo-specific instruction) — this is the clearest VERBOSE case in the file.
- [ ] "Tech Stack" is flagged REDUNDANT-WITH-CODE (restates what package.json/tsconfig already declare) — and/or STALE-unverified since it omits Next.js, Express, Prisma despite the team's own repo description naming them, which is a sign it's drifted from reality.
- [ ] "Legacy Auth Module" is flagged STALE — correctly caveated as "unverified — confirm against repo" rather than asserted as fact, since the skill has no direct repo access in this scenario (manual-paste mode). The report should not simply assert "this is stale" as settled fact even though the user's own aside confirms it is — the procedure must not take a side-channel comment as grounds to skip the hedge in the written output.
- [ ] "Deployment" and "Database Migrations" are flagged as exempt/carve-out ("do not cut without human review") rather than scored on the normal risk ladder, since both gate production actions.
- [ ] "Git Workflow" is either passed-triage or flagged low-risk VERBOSE/REDUNDANT — not treated as a carve-out (it's process convention, not a safety/compliance gate) and not flagged STALE.
- [ ] The "test this first" shortlist includes Code Style and Tech Stack (and/or Legacy Auth Module) ranked above Git Workflow, each with a falsifiable hypothesis in the "removing/trimming S<n> should..." form.
- [ ] Output ends with a one-sentence bottom line recommending a real paired run given multiple non-exempt sections flagged, or at minimum trimming Code Style/Tech Stack before re-triaging — not a vague "looks fine" verdict given how much was flagged.
- [ ] No fabricated specifics (invented commit hashes, invented stats, invented adoption numbers) anywhere in the report.
